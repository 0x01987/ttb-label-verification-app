from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from ocr import extract_text
from validator import analyze_label, verify_label

app = FastAPI(
    title="TTB Label Verify API",
    version="1.0.0"
)

# Allow Next.js frontend to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://ttb-label-verification-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "TTB Label Verify API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_label(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(str(file_path))
    analysis = analyze_label(extracted_text)

    return {
        "filename": file.filename,
        "ocr_text": extracted_text,
        "analysis": analysis
    }


@app.post("/verify")
async def verify_uploaded_label(
    file: UploadFile = File(...),
    brand_name: str = Form(...),
    abv: str = Form(...),
    net_contents: str = Form(...)
):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(str(file_path))

    expected = {
        "brand_name": brand_name,
        "abv": abv,
        "net_contents": net_contents
    }

    verification = verify_label(extracted_text, expected)

    return {
        "filename": file.filename,
        "ocr_text": extracted_text,
        "verification": verification
    }
