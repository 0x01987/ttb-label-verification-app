import re
from rapidfuzz import fuzz

GOV_WARNING_KEYWORDS = [
    "GOVERNMENT WARNING",
    "according to the surgeon general",
    "women should not drink alcoholic",
    "pregnancy",
    "birth defects",
    "impairs your ability to drive",
    "operate machinery",
    "health problems"
]


def normalize(value: str):
    if not value:
        return ""
    value = value.upper()
    value = re.sub(r"[^A-Z0-9%]+", " ", value)
    return value.strip()


def fuzzy_match(expected: str, found: str, threshold: int = 85):
    if not expected:
        return {"match": True, "score": 100}

    score = fuzz.ratio(normalize(expected), normalize(found))
    return {
        "match": score >= threshold,
        "score": score
    }


def extract_abv(text: str):
    patterns = [
        r"(\d{1,2}(?:\.\d+)?)\s*%\s*(?:ALC|ALCOHOL|ABV)?",
        r"(\d{1,2}(?:\.\d+)?)\s*(?:PERCENT|ABV|ALC)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) + "%"

    return None


def extract_net_contents(text: str):
    upper_text = text.upper()

    if "PINT" in upper_text:
        return "1 PINT"

    patterns = [
        r"\b(750|375|1000|500|200|50)\s*(ML|MILLILITER|MILLILITERS)\b",
        r"\b(1\.75|1|0\.75|0\.375)\s*(L|LITER|LITERS)\b",
        r"\b(12|16|24|32)\s*(OZ|FL OZ|FL\. OZ\.)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, upper_text, re.IGNORECASE)
        if match:
            return match.group(0)

    return None


def extract_brand_name(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    skip_words = [
        "GOVERNMENT WARNING",
        "SURGEON GENERAL",
        "ALCOHOLIC",
        "PREGNANCY",
        "BIRTH DEFECTS",
        "IMPAIRS",
        "MACHINERY",
        "HEALTH PROBLEMS",
        "ALC",
        "VOL",
        "PINT",
        "ML",
        "BOTTLED BY",
        "PRODUCED BY",
        "IMPORTED BY",
        "PRODUCT OF",
        "MADE IN"
    ]

    candidates = []

    for line in lines[:10]:
        upper = line.upper()
        if any(word in upper for word in skip_words):
            continue
        if len(line) < 3:
            continue
        candidates.append(line)

    return candidates[0] if candidates else None


def extract_class_type(text: str):
    class_types = [
        "KENTUCKY STRAIGHT BOURBON WHISKEY",
        "BOURBON WHISKEY",
        "STRAIGHT BOURBON",
        "WHISKEY",
        "WHISKY",
        "VODKA",
        "RUM",
        "GIN",
        "TEQUILA",
        "BRANDY",
        "IPA",
        "ALE",
        "LAGER",
        "PILSNER",
        "CABERNET SAUVIGNON",
        "CABERNET",
        "MERLOT",
        "CHARDONNAY",
        "SAUVIGNON BLANC"
    ]

    upper = text.upper()

    for item in class_types:
        if item in upper:
            return item.title()

    return None


def extract_producer(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    keywords = [
        "BOTTLED BY",
        "PRODUCED BY",
        "PRODUCED AND BOTTLED BY",
        "IMPORTED BY",
        "MANUFACTURED BY",
        "BREWED BY"
    ]

    for line in lines:
        upper = line.upper()
        for keyword in keywords:
            if keyword in upper:
                return line

    return None


def extract_country_of_origin(text: str):
    patterns = [
        r"PRODUCT OF\s+([A-Z ]+)",
        r"MADE IN\s+([A-Z ]+)",
        r"IMPORTED FROM\s+([A-Z ]+)"
    ]

    upper = text.upper()

    for pattern in patterns:
        match = re.search(pattern, upper)
        if match:
            return match.group(1).strip().title()

    return None


def check_government_warning(text: str):
    normalized = text.lower()

    matches = [
        keyword for keyword in GOV_WARNING_KEYWORDS
        if keyword.lower() in normalized
    ]

    return {
        "found": len(matches) >= 4,
        "matched_parts": matches
    }


def analyze_label(text: str):
    return {
        "brand_name": extract_brand_name(text),
        "class_type": extract_class_type(text),
        "abv": extract_abv(text),
        "net_contents": extract_net_contents(text),
        "producer": extract_producer(text),
        "country_of_origin": extract_country_of_origin(text),
        "government_warning": check_government_warning(text)
    }


def verify_label(text: str, expected: dict):
    analysis = analyze_label(text)

    checks = {
        "brand_name": fuzzy_match(expected.get("brand_name", ""), analysis.get("brand_name") or "", 75),
        "class_type": fuzzy_match(expected.get("class_type", ""), analysis.get("class_type") or "", 75),
        "abv": fuzzy_match(expected.get("abv", ""), analysis.get("abv") or "", 90),
        "net_contents": fuzzy_match(expected.get("net_contents", ""), analysis.get("net_contents") or "", 85),
        "producer": fuzzy_match(expected.get("producer", ""), analysis.get("producer") or "", 75),
        "country_of_origin": fuzzy_match(expected.get("country_of_origin", ""), analysis.get("country_of_origin") or "", 75),
        "government_warning": {
            "match": analysis["government_warning"]["found"],
            "score": 100 if analysis["government_warning"]["found"] else 0
        }
    }

    passed_count = sum(1 for check in checks.values() if check["match"])
    compliance_score = int((passed_count / len(checks)) * 100)

    return {
        "expected": expected,
        "found": analysis,
        "checks": checks,
        "compliance_score": compliance_score,
        "overall_status": "PASS" if compliance_score == 100 else "REVIEW"
    }
