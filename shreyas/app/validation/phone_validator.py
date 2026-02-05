def validate_phone(entity: dict) -> dict:
    value = entity["value"]
    confidence = entity["confidence"]
    metadata = entity.get("metadata", {})

    valid = True
    reasons = []

    if not value.isdigit() or len(value) != 10:
        valid = False
        reasons.append("Invalid phone number format")

    if value.startswith("000") or value.startswith("123"):
        confidence -= 0.30
        reasons.append("Common fake phone pattern")

    metadata["validation"] = {
        "valid": valid,
        "reasons": reasons
    }

    entity["confidence"] = round(max(confidence, 0.0), 2)
    entity["metadata"] = metadata

    return entity
