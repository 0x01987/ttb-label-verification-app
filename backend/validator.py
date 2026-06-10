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
        "ML"
    ]

    candidates = []

    for line in lines[:8]:
        upper = line.upper()
        if any(word in upper for word in skip_words):
            continue
        if len(line) < 3:
            continue
        candidates.append(line)

    if candidates:
        return candidates[0]

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
        "abv": extract_abv(text),
        "net_contents": extract_net_contents(text),
        "government_warning": check_government_warning(text)
    }


def verify_label(text: str, expected: dict):
    analysis = analyze_label(text)

    brand_result = fuzzy_match(
        expected.get("brand_name", ""),
        analysis.get("brand_name") or "",
        threshold=75
    )

    abv_result = fuzzy_match(
        expected.get("abv", ""),
        analysis.get("abv") or "",
        threshold=90
    )

    net_contents_result = fuzzy_match(
        expected.get("net_contents", ""),
        analysis.get("net_contents") or "",
        threshold=85
    )

    warning_valid = analysis["government_warning"]["found"]

    checks = [
        brand_result["match"],
        abv_result["match"],
        net_contents_result["match"],
        warning_valid
    ]

    passed_count = sum(1 for check in checks if check)
    compliance_score = int((passed_count / len(checks)) * 100)

    return {
        "expected": expected,
        "found": analysis,
        "checks": {
            "brand_name": brand_result,
            "abv": abv_result,
            "net_contents": net_contents_result,
            "government_warning": {
                "match": warning_valid,
                "score": 100 if warning_valid else 0
            }
        },
        "compliance_score": compliance_score,
        "overall_status": "PASS" if compliance_score == 100 else "REVIEW"
    }