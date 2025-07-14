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

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is working."}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    size_kb = round(len(content) / 1024, 2)

    # OCR
    image = Image.open(io.BytesIO(content)).convert("RGB")
    np_img = np.array(image)
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np_img)
    detected_texts = [text for (_, text, _) in result]

    # Find likely part number (e.g., XXXXX-XXX-XXX)
    part_number = None
    for text in detected_texts:
        formatted = text.replace(" ", "").upper()
        if re.match(r'^[A-Z0-9]{3,6}-[A-Z0-9]{2,4}-[A-Z0-9]{2,6}$', formatted):
            part_number = text
            break

    return JSONResponse(content={
        "filename": file.filename,
        "size_kb": size_kb,
        "message": "Image uploaded successfully.",
        "detected_texts": detected_texts,
        "part_number": part_number
    })

@app.get("/partinfo/")
async def part_info(part_number: str):
    google_url = f"https://www.google.com/search?q={part_number}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={part_number}"
    amazon_url = f"https://www.amazon.com/s?k={part_number}"

    results = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            ebay_resp = await client.get(ebay_url, headers=headers)
            soup = BeautifulSoup(ebay_resp.text, "html.parser")
            # Find all eBay results
            items = soup.find_all("li", class_="s-item")
            for item in items[:3]:  # Top 3 results
                title_tag = item.find("h3", class_="s-item__title")
                price_tag = item.find("span", class_="s-item__price")
                img_tag = item.find("img", class_="s-item__image-img")
                link_tag = item.find("a", class_="s-item__link")
                subtitle_tag = item.find("div", class_="s-item__subtitle")
                brand = None
                brand_tag = item.find("span", class_="s-item__dynamic")
                if brand_tag:
                    brand = brand_tag.text.strip()
                # Only add results with a title, price, image, and link
                if title_tag and price_tag and img_tag and link_tag:
                    results.append({
                        "title": title_tag.text.strip(),
                        "price": price_tag.text.strip(),
                        "image_url": img_tag["src"],
                        "listing_url": link_tag["href"],
                        "brand": brand,
                        "compatibility": subtitle_tag.text.strip() if subtitle_tag else None,
                    })
    except Exception as e:
        results = []

    return JSONResponse(content={
        "part_number": part_number,
        "google_url": google_url,
        "ebay_url": ebay_url,
        "amazon_url": amazon_url,
        "ebay_results": results
    })
