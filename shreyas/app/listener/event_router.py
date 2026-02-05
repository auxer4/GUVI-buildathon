from storage.raw_events import store_raw_event
from extraction.regex_extractors import extract_entities

def route_event(event: dict):
    print(f"[Router] Event received → {event.get('event')}")

    # Step 1: Store raw event for legal safety
    store_raw_event(event)

    # Step 2: Extract intelligence
    extract_entities(event)
