import re
from extraction.entity_builder import build_entity

UPI_REGEX = re.compile(
    r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"
)

URL_REGEX = re.compile(
    r"\bhttps?://[^\s<>\"']+\b"
)

PHONE_REGEX = re.compile(
    r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"
)

def extract_entities(event: dict):
    """
    Entry point called by listener.
    """
    text = event.get("text", "")
    event_id = event.get("event_id", "unknown")

    extracted = []

    extracted.extend(_extract_upi(text, event_id))
    extracted.extend(_extract_urls(text, event_id))
    extracted.extend(_extract_phones(text, event_id))

    for entity in extracted:
        print(f"[Extracted] {entity['type']} → {entity['value']} | conf={entity['confidence']}")

    return extracted


def _extract_upi(text: str, event_id: str):
    entities = []
    for match in UPI_REGEX.findall(text):
        confidence = 0.95
        entities.append(
            build_entity(
                entity_type="UPI_ID",
                value=match,
                source_event_id=event_id,
                confidence=confidence,
                metadata={"method": "regex"}
            )
        )
    return entities


def _extract_urls(text: str, event_id: str):
    entities = []
    for match in URL_REGEX.findall(text):
        confidence = 0.90
        entities.append(
            build_entity(
                entity_type="URL",
                value=match,
                source_event_id=event_id,
                confidence=confidence,
                metadata={"method": "regex"}
            )
        )
    return entities


def _extract_phones(text: str, event_id: str):
    entities = []
    for match in PHONE_REGEX.findall(text):
        confidence = 0.85
        entities.append(
            build_entity(
                entity_type="PHONE_NUMBER",
                value=match,
                source_event_id=event_id,
                confidence=confidence,
                metadata={"method": "regex"}
            )
        )
    return entities
