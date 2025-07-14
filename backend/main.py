from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is working."}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # For now, just confirm upload and echo filename
    content = await file.read()
    size_kb = round(len(content) / 1024, 2)
    return JSONResponse(content={
        "filename": file.filename,
        "size_kb": size_kb,
        "message": "Image uploaded successfully."
    })
