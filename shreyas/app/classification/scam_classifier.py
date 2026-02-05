from classification.confidence_scorer import calculate_confidence

# Canonical scam types (DO NOT RENAME casually)
SCAM_TYPES = {
    "UPI_REFUND_SCAM",
    "PHISHING_SCAM",
    "OTP_SCAM",
    "JOB_SCAM",
    "LOAN_SCAM",
    "ROMANCE_SCAM",
    "UNKNOWN"
}


def classify_scam(entities: list, conversation_signals: dict = None) -> dict:
    """
    entities: list of extracted entity dicts
    conversation_signals: optional metadata from other services
    """

    conversation_signals = conversation_signals or {}
    entity_types = {e["type"] for e in entities}

    reasoning = []
    scam_type = "UNKNOWN"

    # ---- RULE SETS ----

    # UPI Refund / Payment Scam
    if "UPI_ID" in entity_types:
        scam_type = "UPI_REFUND_SCAM"
        reasoning.append("UPI ID requested/shared")

    # Phishing Scam
    if "URL" in entity_types:
        scam_type = "PHISHING_SCAM"
        reasoning.append("Suspicious URL shared")

    # OTP Scam
    if conversation_signals.get("otp_requested"):
        scam_type = "OTP_SCAM"
        reasoning.append("OTP request detected")

    # Job Scam
    if conversation_signals.get("job_offer"):
        scam_type = "JOB_SCAM"
        reasoning.append("Job offer lure detected")

    # Loan Scam
    if conversation_signals.get("loan_offer"):
        scam_type = "LOAN_SCAM"
        reasoning.append("Instant loan lure detected")

    # Romance Scam
    if conversation_signals.get("emotional_manipulation"):
        scam_type = "ROMANCE_SCAM"
        reasoning.append("Emotional manipulation patterns")

    confidence = calculate_confidence(
        scam_type=scam_type,
        entities=entities,
        signals=conversation_signals
    )

    return {
        "scam_type": scam_type,
        "confidence": confidence,
        "reasoning": reasoning
    }
