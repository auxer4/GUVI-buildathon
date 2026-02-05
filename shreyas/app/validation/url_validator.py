from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".loan", ".tk"
}

def validate_url(entity: dict) -> dict:
    value = entity["value"]
    confidence = entity["confidence"]
    metadata = entity.get("metadata", {})

    valid = True
    reasons = []

    parsed = urlparse(value)

    if not parsed.scheme or not parsed.netloc:
        valid = False
        reasons.append("Malformed URL")

    for tld in SUSPICIOUS_TLDS:
        if parsed.netloc.endswith(tld):
            confidence -= 0.25
            reasons.append(f"Suspicious TLD: {tld}")

    metadata["validation"] = {
        "valid": valid,
        "reasons": reasons
    }

    entity["confidence"] = round(max(confidence, 0.0), 2)
    entity["metadata"] = metadata

    return entity
