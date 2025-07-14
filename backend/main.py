from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from PIL import Image
import numpy as np
import io
import re

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
    # Generate URLs for Google, eBay, Amazon searches
    google_url = f"https://www.google.com/search?q={part_number}"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={part_number}"
    amazon_url = f"https://www.amazon.com/s?k={part_number}"

    return JSONResponse(content={
        "part_number": part_number,
        "google_url": google_url,
        "ebay_url": ebay_url,
        "amazon_url": amazon_url
    })
