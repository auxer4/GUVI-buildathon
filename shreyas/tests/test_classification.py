from classification.scam_classifier import classify_scam

def test_upi_refund_scam_classification():
    entities = [
        {"type": "UPI_ID", "value": "fraud@upi", "confidence": 0.9}
    ]

    result = classify_scam(entities)

    assert result["scam_type"] == "UPI_REFUND_SCAM"
    assert result["confidence"] >= 0.65
