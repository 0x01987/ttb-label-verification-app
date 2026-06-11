from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

from ocr import extract_text
from validator import analyze_label, verify_label

app = FastAPI(
    title="TTB Label Verify API",
    version="1.0.0"
)

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


def save_upload(file: UploadFile) -> Path:
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / safe_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def build_expected(
    brand_name: str,
    class_type: str,
    abv: str,
    net_contents: str,
    producer: str,
    country_of_origin: str
):
    return {
        "brand_name": brand_name,
        "class_type": class_type,
        "abv": abv,
        "net_contents": net_contents,
        "producer": producer,
        "country_of_origin": country_of_origin
    }


@app.get("/")
def root():
    return {"message": "TTB Label Verify API Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_label(file: UploadFile = File(...)):
    file_path = save_upload(file)

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
    brand_name: str = Form(""),
    class_type: str = Form(""),
    abv: str = Form(""),
    net_contents: str = Form(""),
    producer: str = Form(""),
    country_of_origin: str = Form("")
):
    file_path = save_upload(file)
    extracted_text = extract_text(str(file_path))

    expected = build_expected(
        brand_name,
        class_type,
        abv,
        net_contents,
        producer,
        country_of_origin
    )

    verification = verify_label(extracted_text, expected)

    return {
        "filename": file.filename,
        "ocr_text": extracted_text,
        "verification": verification
    }


@app.post("/batch-verify")
async def batch_verify_labels(
    files: list[UploadFile] = File(...),
    brand_name: str = Form(""),
    class_type: str = Form(""),
    abv: str = Form(""),
    net_contents: str = Form(""),
    producer: str = Form(""),
    country_of_origin: str = Form("")
):
    expected = build_expected(
        brand_name,
        class_type,
        abv,
        net_contents,
        producer,
        country_of_origin
    )

    results = []

    for file in files:
        try:
            file_path = save_upload(file)
            extracted_text = extract_text(str(file_path))
            verification = verify_label(extracted_text, expected)

            results.append({
                "filename": file.filename,
                "ocr_text": extracted_text,
                "overall_status": verification["overall_status"],
                "compliance_score": verification["compliance_score"],
                "missing_required_fields": verification.get("missing_required_fields", []),
                "verification": verification,
                "error": None
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "ocr_text": "",
                "overall_status": "REVIEW",
                "compliance_score": 0,
                "missing_required_fields": [
                    "Unable to process label image"
                ],
                "verification": None,
                "error": str(e)
            })

    return {
        "total_files": len(results),
        "results": results
    }