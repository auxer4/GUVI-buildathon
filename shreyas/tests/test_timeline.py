from timeline.timeline_builder import build_timeline

def test_timeline_ordering():
    raw_events = [
        {
            "event_hash": "h1",
            "event": {
                "event": "SCAM_MESSAGE_RECEIVED",
                "timestamp": "2026-02-04T10:00:01Z"
            }
        }
    ]

    intel_entities = [
        {
            "type": "UPI_ID",
            "confidence": 0.9,
            "stored_at": "2026-02-04T10:00:05Z",
            "source_event_id": "evt1"
        }
    ]

    timeline = build_timeline(raw_events, intel_entities)

    assert timeline[0]["type"] == "RAW_EVENT"
    assert timeline[1]["type"] == "INTEL_EXTRACTED"
