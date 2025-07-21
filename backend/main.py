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

# Enable CORS for frontend dev (safe even if using Vite proxy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Optional: legacy route still works
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    return await process_image(file)

# Shared logic for both upload endpoints
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

        part_number = extract_part_numbers(detected_texts)
        car_info = await car_ai.identify_car_part(content, detected_texts)

        return JSONResponse(content={
            "filename": file.filename,
            "size_kb": size_kb,
            "message": "Image processed successfully",
            "detected_texts": detected_texts,
            "part_number": part_number,
            "texts_found": len(detected_texts),
            "car_info": car_info
        })

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
