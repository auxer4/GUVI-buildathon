from datetime import datetime
import uuid

def build_entity(
    entity_type: str,
    value: str,
    source_event_id: str,
    confidence: float,
    metadata: dict = None
) -> dict:
    return {
        "entity_id": str(uuid.uuid4()),
        "type": entity_type,
        "value": value,
        "confidence": round(confidence, 2),
        "source_event_id": source_event_id,
        "extracted_at": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }
