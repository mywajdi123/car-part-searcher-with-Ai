from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from PIL import Image
import numpy as np
import io

app = FastAPI()

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

    # OCR processing
    image = Image.open(io.BytesIO(content)).convert("RGB")
    np_img = np.array(image)

    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np_img)
    detected_texts = [text for (_, text, _) in result]

    return JSONResponse(content={
        "filename": file.filename,
        "size_kb": size_kb,
        "message": "Image uploaded successfully.",
        "detected_texts": detected_texts
    })
