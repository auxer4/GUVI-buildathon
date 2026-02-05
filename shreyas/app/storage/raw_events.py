from datetime import datetime
from security.hashing import sha256_from_dict
from storage.db import RAW_EVENT_STORE

def store_raw_event(event: dict) -> dict:
    """
    Stores raw incoming event with hash and timestamp.
    This data MUST NEVER be mutated.
    """

    event_hash = sha256_from_dict(event)

    record = {
        "event_hash": event_hash,
        "event": event,
        "stored_at": datetime.utcnow().isoformat()
    }

    RAW_EVENT_STORE.append(record)

    print(f"[Storage] Raw event stored | hash={event_hash}")

    return record


def get_raw_events() -> list:
    """
    Returns all raw events.
    Read-only usage only.
    """
    return list(RAW_EVENT_STORE)
