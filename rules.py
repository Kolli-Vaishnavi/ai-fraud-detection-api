import re

# Multilingual + weighted fraud indicators
FRAUD_PATTERNS = {
    # English
    "otp": 0.4,
    "one time password": 0.4,
    "account blocked": 0.4,
    "bank": 0.2,
    "verify": 0.3,
    "urgent": 0.3,
    "immediately": 0.25,
    "click": 0.3,
    "transfer": 0.3,
    "upi": 0.3,
    "pin": 0.4,
    "kyc": 0.3,
    "refund": 0.3,
    "lottery": 0.4,
    "expire": 0.3,
    "cvv": 0.5,
    "credit card": 0.3,
    "debit card": 0.3,
    "download": 0.2,
    "anydesk": 0.5,
    "teamviewer": 0.5,
    "quicksupport": 0.5,

    # Hindi
    "turant": 0.25,
    "abhi": 0.2,
    "khata": 0.3,
    "bank se": 0.3,
    "otp batao": 0.5,
    "bhej": 0.2,
    "paise": 0.2,
    "block ho gaya": 0.4,

    # Tamil
    "vangi": 0.2,
    "kanakku": 0.2,
    "udane": 0.25,
    "kuriyeedu": 0.3,

    # Telugu
    "vente": 0.25,
    "pampandi": 0.2,
    "account block": 0.4
}

# Regex for sensitive data patterns
SENSITIVE_REGEX = {
    "OTP_Pattern": r"\b\d{4,6}\b",
    "Card_Pattern": r"\b\d{16}\b",
    "CVV_Pattern": r"\b\d{3}\b"
}

URGENCY_WORDS = [
    "urgent",
    "immediately",
    "now",
    "within",
    "last chance",
    "final warning",
    "turant",
    "udane"
]

def analyze_keywords(text: str):

    if not text:
        return {
            "rule_score": 0,
            "rule_label": "safe",
            "matched_keywords": []
        }

    text_lower = text.lower()
    score = 0.0
    matched = []

    # Keyword Analysis
    for phrase, weight in FRAUD_PATTERNS.items():
        if phrase in text_lower:
            score += weight
            matched.append(phrase)

    # Sensitive Data Regex Analysis
    for name, pattern in SENSITIVE_REGEX.items():
        if re.search(pattern, text):
            if "otp" in text_lower or "code" in text_lower or "pin" in text_lower:
                score += 0.3
                matched.append(f"RegEx:{name}")

    # Urgency Detection
    urgency_hits = sum(1 for word in URGENCY_WORDS if word in text_lower)
    if urgency_hits >= 2:
        score += 0.25
        matched.append("urgency-language")

    # Clamp score
    score = min(score, 1.0)

    # Risk Label
    if score >= 0.75:
        label = "high"
    elif score >= 0.35:
        label = "medium"
    elif score > 0.1:
        label = "low"
    else:
        label = "safe"

    return {
        "rule_score": round(score * 100),
        "rule_label": label,
        "matched_keywords": matched
    }