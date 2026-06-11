import os
import requests

USE_OCR_SPACE = os.getenv("USE_OCR_SPACE", "false").lower() == "true"
USE_DEMO_OCR = os.getenv("USE_DEMO_OCR", "false").lower() == "true"
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")

if not USE_OCR_SPACE and not USE_DEMO_OCR:
    import easyocr
    reader = easyocr.Reader(["en"], gpu=False)


def demo_text():
    return """
MALT & HOP
BREWERY
GOVERNMENT WARNING:
According to the Surgeon General,
women should not drink alcoholic beverages during pregnancy because of the risk of birth defects.
Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.
5% ALC/VOL
1 PINT
Brewed by Malt & Hop Brewery
Product of United States
"""


def extract_text(image_path):
    if USE_OCR_SPACE:
        return extract_text_ocr_space(image_path)

    if USE_DEMO_OCR:
        return demo_text()

    results = reader.readtext(image_path)
    return "\n".join([result[1] for result in results])


def extract_text_ocr_space(image_path):
    if not OCR_SPACE_API_KEY:
        return demo_text()

    url = "https://api.ocr.space/parse/image"

    with open(image_path, "rb") as image_file:
        response = requests.post(
            url,
            files={"file": image_file},
            data={
                "apikey": OCR_SPACE_API_KEY,
                "language": "eng",
                "isOverlayRequired": False,
                "OCREngine": 2,
                "scale": True
            },
            timeout=60
        )

    response.raise_for_status()
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return ""

    parsed_results = result.get("ParsedResults", [])

    if not parsed_results:
        return ""

    return parsed_results[0].get("ParsedText", "")