from validation.validation_router import validate_entities

def test_upi_validation_reduces_confidence():
    entities = [{
        "entity_id": "1",
        "type": "UPI_ID",
        "value": "test@upi",
        "confidence": 0.9,
        "source_event_id": "evt1",
        "metadata": {}
    }]

    validated = validate_entities(entities)

    assert validated[0]["confidence"] < 0.9
    assert "validation" in validated[0]["metadata"]


def test_phone_validation_rejects_fake():
    entities = [{
        "entity_id": "2",
        "type": "PHONE_NUMBER",
        "value": "0001234567",
        "confidence": 0.8,
        "source_event_id": "evt2",
        "metadata": {}
    }]

    validated = validate_entities(entities)

    assert validated[0]["confidence"] < 0.8
