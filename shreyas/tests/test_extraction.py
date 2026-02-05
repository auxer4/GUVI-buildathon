from extraction.regex_extractors import extract_entities

def test_upi_extraction():
    event = {
        "event_id": "evt1",
        "text": "Send money to testuser@upi"
    }

    entities = extract_entities(event)

    assert len(entities) == 1
    assert entities[0]["type"] == "UPI_ID"
    assert entities[0]["value"] == "testuser@upi"
    assert entities[0]["confidence"] > 0.9


def test_url_extraction():
    event = {
        "event_id": "evt2",
        "text": "Login at https://fakebank-login.xyz"
    }

    entities = extract_entities(event)

    assert any(e["type"] == "URL" for e in entities)
