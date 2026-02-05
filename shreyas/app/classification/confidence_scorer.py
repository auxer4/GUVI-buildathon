def calculate_confidence(
    scam_type: str,
    entities: list,
    signals: dict
) -> float:
    """
    Returns confidence score between 0.0 and 1.0
    """

    base_confidence = {
        "UPI_REFUND_SCAM": 0.65,
        "PHISHING_SCAM": 0.70,
        "OTP_SCAM": 0.75,
        "JOB_SCAM": 0.60,
        "LOAN_SCAM": 0.60,
        "ROMANCE_SCAM": 0.55,
        "UNKNOWN": 0.30
    }.get(scam_type, 0.30)

    # Boosts from evidence
    entity_boost = min(len(entities) * 0.05, 0.20)

    signal_boost = 0.0
    if signals.get("urgency"):
        signal_boost += 0.05
    if signals.get("impersonation"):
        signal_boost += 0.05
    if signals.get("repeat_request"):
        signal_boost += 0.05

    confidence = base_confidence + entity_boost + signal_boost

    return round(min(confidence, 0.95), 2)
