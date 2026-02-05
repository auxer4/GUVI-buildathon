import re

UPI_REGEX = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def redact_text(text: str) -> str:
    """
    Redacts sensitive identifiers from free text.
    """

    if not text:
        return text

    text = UPI_REGEX.sub("[REDACTED_UPI]", text)
    text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)

    return text


def redact_entity(entity: dict) -> dict:
    """
    Redacts entity value but keeps type & metadata.
    """

    redacted = entity.copy()
    redacted["value"] = "[REDACTED]"
    return redacted


def redact_entities(entities: list) -> list:
    """
    Redacts a list of extracted entities.
    """
    return [redact_entity(e) for e in entities]
