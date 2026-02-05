import re

UPI_REGEX = re.compile(r"^[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}$")

KNOWN_FAKE_HANDLES = {
    "test", "demo", "fake", "sample"
}

def validate_upi(entity: dict) -> dict:
    """
    Validates UPI entity and adjusts confidence.
    """

    value = entity["value"]
    confidence = entity["confidence"]
    metadata = entity.get("metadata", {})

    valid = True
    reasons = []

    if not UPI_REGEX.match(value):
        valid = False
        reasons.append("Invalid UPI format")

    handle = value.split("@")[0].lower()
    if handle in KNOWN_FAKE_HANDLES:
        confidence -= 0.30
        reasons.append("Suspicious handle name")

    metadata["validation"] = {
        "valid": valid,
        "reasons": reasons
    }

    entity["confidence"] = round(max(confidence, 0.0), 2)
    entity["metadata"] = metadata

    return entity
