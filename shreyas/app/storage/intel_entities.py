from datetime import datetime
from storage.db import INTEL_ENTITY_STORE

def store_intel_entity(entity: dict) -> dict:
    """
    Stores extracted intelligence entity.
    """

    record = {
        "entity_id": entity["entity_id"],
        "type": entity["type"],
        "value": entity["value"],
        "confidence": entity["confidence"],
        "source_event_id": entity["source_event_id"],
        "metadata": entity.get("metadata", {}),
        "stored_at": datetime.utcnow().isoformat()
    }

    INTEL_ENTITY_STORE.append(record)

    print(
        f"[Storage] Intel stored | "
        f"type={record['type']} | value={record['value']}"
    )

    return record


def get_entities_by_type(entity_type: str) -> list:
    return [
        e for e in INTEL_ENTITY_STORE
        if e["type"] == entity_type
    ]


def get_all_entities() -> list:
    return list(INTEL_ENTITY_STORE)
