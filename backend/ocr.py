import os

USE_DEMO_OCR = os.getenv("USE_DEMO_OCR", "false").lower() == "true"

if not USE_DEMO_OCR:
    import easyocr
    reader = easyocr.Reader(["en"], gpu=False)


def extract_text(image_path):
    if USE_DEMO_OCR:
        return """
MALT & HOP
BREWERY
GOVERNMENT WARNING:
According to the Surgeon General,
women should not drink alcoholic beverages during pregnancy because of the risk of birth defects.
Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.
5% ALC/VOL
1 PINT
"""

    results = reader.readtext(image_path)
    return "\n".join([result[1] for result in results])