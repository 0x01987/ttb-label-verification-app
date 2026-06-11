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

COUNTRIES = [
    "CANADA",
    "UNITED STATES",
    "UNITED STATES OF AMERICA",
    "USA",
    "U.S.A.",
    "MEXICO",
    "FRANCE",
    "ITALY",
    "GERMANY",
    "SPAIN",
    "PORTUGAL",
    "IRELAND",
    "SCOTLAND",
    "ENGLAND",
    "JAPAN",
    "AUSTRALIA",
    "NEW ZEALAND",
    "CHILE",
    "ARGENTINA"
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


def compare_or_required(expected: str, found: str, threshold: int = 85):
    if not found:
        return {
            "match": False,
            "score": 0
        }

    if not expected:
        return {
            "match": True,
            "score": 100
        }

    return fuzzy_match(expected, found, threshold)


def clean_country(value: str):
    if not value:
        return None

    value = value.upper().strip()

    value = re.sub(
        r"\b(BY|FOR|UNDER|WITH|AT|AND|FROM|BOTTLED|PRODUCED|BREWED|DISTILLED|IMPORTED)\b.*",
        "",
        value
    ).strip()

    for country in COUNTRIES:
        if country in value:
            if country in ["USA", "U.S.A.", "UNITED STATES OF AMERICA"]:
                return "United States"
            return country.title()

    return value.title() if value else None


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
        "PRODUCED IN",
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
    upper = text.upper()

    patterns = [
        r"PRODUCT OF\s+([A-Z .]+)",
        r"MADE IN\s+([A-Z .]+)",
        r"IMPORTED FROM\s+([A-Z .]+)",
        r"PRODUCED IN\s+([A-Z .]+)",
        r"BREWED IN\s+([A-Z .]+)",
        r"DISTILLED IN\s+([A-Z .]+)",
        r"CRAFTED IN\s+([A-Z .]+)",
        r"COUNTRY OF ORIGIN[:\s]+([A-Z .]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, upper)

        if match:
            country = clean_country(match.group(1))
            if country:
                return country

    for country in COUNTRIES:
        if f" {country} " in f" {upper} ":
            if country in ["USA", "U.S.A.", "UNITED STATES OF AMERICA"]:
                return "United States"
            return country.title()

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


def get_missing_required_fields(analysis: dict):
    missing = []

    if not analysis.get("brand_name"):
        missing.append("Brand Name")

    if not analysis.get("class_type"):
        missing.append("Class / Type Designation")

    if not analysis.get("abv"):
        missing.append("Alcohol Content (ABV)")

    if not analysis.get("net_contents"):
        missing.append("Net Contents")

    if not analysis.get("producer"):
        missing.append("Producer / Bottler Information")

    if not analysis.get("country_of_origin"):
        missing.append("Country of Origin")

    if not analysis.get("government_warning", {}).get("found"):
        missing.append("Government Health Warning Statement")

    return missing


def verify_label(text: str, expected: dict):
    analysis = analyze_label(text)

    checks = {
        "brand_name": compare_or_required(
            expected.get("brand_name", ""),
            analysis.get("brand_name") or "",
            75
        ),
        "class_type": compare_or_required(
            expected.get("class_type", ""),
            analysis.get("class_type") or "",
            75
        ),
        "abv": compare_or_required(
            expected.get("abv", ""),
            analysis.get("abv") or "",
            90
        ),
        "net_contents": compare_or_required(
            expected.get("net_contents", ""),
            analysis.get("net_contents") or "",
            85
        ),
        "producer": compare_or_required(
            expected.get("producer", ""),
            analysis.get("producer") or "",
            75
        ),
        "country_of_origin": compare_or_required(
            expected.get("country_of_origin", ""),
            analysis.get("country_of_origin") or "",
            75
        ),
        "government_warning": {
            "match": analysis["government_warning"]["found"],
            "score": 100 if analysis["government_warning"]["found"] else 0
        }
    }

    missing_required_fields = get_missing_required_fields(analysis)

    passed_count = sum(1 for check in checks.values() if check["match"])
    compliance_score = int((passed_count / len(checks)) * 100)

    overall_status = (
        "PASS"
        if len(missing_required_fields) == 0 and compliance_score == 100
        else "REVIEW"
    )

    return {
        "expected": expected,
        "found": analysis,
        "checks": checks,
        "missing_required_fields": missing_required_fields,
        "compliance_score": compliance_score,
        "overall_status": overall_status
    }