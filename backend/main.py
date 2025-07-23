from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import easyocr
from PIL import Image
import numpy as np
import io
import re
import httpx
from car_ai import CarPartAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()

# Initialize AI detector
car_ai = CarPartAI()

# Enable CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import parts database AFTER app initialization
from parts_database import parts_db

def extract_part_numbers(texts):
    part_patterns = [
        r'^[A-Z0-9]{3,6}-[A-Z0-9]{2,4}-[A-Z0-9]{2,6}$',
        r'^[A-Z0-9]{4,10}-[A-Z0-9]{3,6}$',
        r'^[A-Z0-9]{6,12}$',
        r'^[0-9]{8,12}$',
        r'^[A-Z]{2,4}[0-9]{4,8}[A-Z]?$',
        r'^[0-9]{2,4}-[0-9]{3,6}-[0-9]{2,4}$',
    ]

    potential_parts = []

    for text in texts:
        cleaned = re.sub(r'[^\w-]', '', text.upper())
        for pattern in part_patterns:
            if re.match(pattern, cleaned) and len(cleaned) >= 5:
                potential_parts.append({
                    'original': text,
                    'cleaned': cleaned,
                    'confidence': len(cleaned)
                })

    if potential_parts:
        best_match = max(potential_parts, key=lambda x: x['confidence'])
        return best_match['cleaned']

    return None


@app.get("/")
def read_root():
    return {"message": "Car Parts AI Backend is running!"}

# ✅ New: Match frontend call to /api/predict


@app.post("/api/predict")
async def predict_api(file: UploadFile = File(...)):
    return await process_image(file)


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    return await process_image(file)

async def process_image(file: UploadFile):
    try:
        content = await file.read()
        size_kb = round(len(content) / 1024, 2)

        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload an image file"}
            )

        image = Image.open(io.BytesIO(content)).convert("RGB")
        np_img = np.array(image)

        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(np_img)
        detected_texts = [text for (_, text, confidence) in result if confidence > 0.5]

        # Extract part numbers using existing function
        part_number = extract_part_numbers(detected_texts)
        
        # Get AI analysis
        ai_analysis = await car_ai.identify_car_part(content, detected_texts)
        
        # Search parts database for additional compatibility info
        database_result = None
        if part_number:
            database_result = await parts_db.search_part_by_number(part_number)
        elif detected_texts:  # Try searching with any detected text
            for text in detected_texts:
                database_result = await parts_db.search_part_by_number(text)
                if database_result:
                    break
        
        # Create enhanced response
        enhanced_response = {
            "filename": file.filename,
            "size_kb": size_kb,
            "message": "Image processed successfully",
            "detected_texts": detected_texts,
            "part_number": part_number,
            "texts_found": len(detected_texts),
            
            # Enhanced AI analysis
            "ai_analysis": ai_analysis,
            
            # Database compatibility results  
            "database_result": {
                "found": database_result is not None,
                "data": {
                    "part_name": database_result.part_name if database_result else None,
                    "category": database_result.category if database_result else None,
                    "compatibility": [
                        {
                            "make": comp.make,
                            "model": comp.model, 
                            "years": comp.years,
                            "engines": comp.engines,
                            "confidence": comp.confidence,
                            "notes": comp.notes
                        } for comp in database_result.compatibility
                    ] if database_result else [],
                    "interchangeable": [
                        {
                            "part_number": part.part_number,
                            "brand": part.brand,
                            "type": part.type,
                            "price_range": part.price_range
                        } for part in database_result.interchangeable  
                    ] if database_result else [],
                    "specifications": database_result.specifications if database_result else {}
                } if database_result else None
            },
            
            # Combined confidence score
            "overall_confidence": (
                (ai_analysis.get('confidence', 0.5) + 
                 (database_result.confidence if database_result else 0.3)) / 2
            ),
            
            # Data sources used
            "sources": {
                "ocr": "easyocr",
                "ai_vision": "openai_gpt4o" if ai_analysis.get('ai_used') else "rule_based",
                "parts_database": database_result.source if database_result else "not_found"
            }
        }

        return JSONResponse(content=enhanced_response)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )


@app.get("/partinfo/")
async def part_info(part_number: str):
    google_url = f"https://www.google.com/search?q={part_number}+car+part"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={part_number}"
    amazon_url = f"https://www.amazon.com/s?k={part_number}"

    results = []
    error_message = None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            ebay_resp = await client.get(ebay_url, headers=headers)

            if ebay_resp.status_code == 200:
                soup = BeautifulSoup(ebay_resp.text, "html.parser")
                items = soup.find_all("div", class_="s-item__wrapper")

                for item in items[:5]:
                    try:
                        title_tag = item.find("h3", class_="s-item__title")
                        price_tag = item.find("span", class_="s-item__price")
                        img_tag = item.find("img")
                        link_tag = item.find("a", class_="s-item__link")

                        if title_tag and price_tag and link_tag:
                            title_text = title_tag.get_text(strip=True)
                            if "Shop on eBay" not in title_text:
                                results.append({
                                    "title": title_text,
                                    "price": price_tag.get_text(strip=True),
                                    "image_url": img_tag.get("src", "") if img_tag else "",
                                    "listing_url": link_tag.get("href", ""),
                                })
                    except:
                        continue
    except Exception as e:
        error_message = f"Lookup failed: {str(e)}"

    return JSONResponse(content={
        "part_number": part_number,
        "google_url": google_url,
        "ebay_url": ebay_url,
        "amazon_url": amazon_url,
        "ebay_results": results,
        "results_count": len(results),
        "error": error_message
    })


@app.on_event("shutdown")
async def shutdown_event():
    await parts_db.close()
    