from datetime import datetime

def build_timeline(
    raw_events: list,
    intel_entities: list,
    classification_result: dict = None
) -> list:
    """
    Builds a chronological timeline of scam activity.
    """

    timeline = []

    # ---- RAW EVENTS ----
    for record in raw_events:
        event = record["event"]
        timeline.append({
            "timestamp": event.get("timestamp"),
            "type": "RAW_EVENT",
            "description": _describe_raw_event(event),
            "event_hash": record.get("event_hash")
        })

    # ---- INTEL ENTITIES ----
    for entity in intel_entities:
        timeline.append({
            "timestamp": entity.get("stored_at"),
            "type": "INTEL_EXTRACTED",
            "description": _describe_entity(entity),
            "source_event_id": entity.get("source_event_id")
        })

    # ---- CLASSIFICATION ----
    if classification_result:
        timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "SCAM_CLASSIFIED",
            "description": (
                f"Scam classified as {classification_result['scam_type']} "
                f"(confidence {classification_result['confidence']})"
            )
        })

    # ---- SORT TIMELINE ----
    timeline.sort(key=lambda x: x["timestamp"])

    return timeline


def _describe_raw_event(event: dict) -> str:
    event_type = event.get("event", "UNKNOWN_EVENT")

    if event_type == "SCAM_MESSAGE_RECEIVED":
        return "Message received from external party"

    if event_type == "BOT_REPLY_SENT":
        return "Automated response sent to external party"

    return f"Event occurred: {event_type}"


def _describe_entity(entity: dict) -> str:
    return (
        f"Extracted {entity['type']} "
        f"(confidence {entity['confidence']})"
    )
