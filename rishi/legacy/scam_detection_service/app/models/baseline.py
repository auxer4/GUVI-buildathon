from app.features.text_features import extract_text_features
from app.features.metadata_features import extract_metadata_features
from app.core.scoring import calculate_risk_score
from app.core.config import WARNING_THRESHOLD, HONEYPOT_THRESHOLD


def analyze_message(message: str) -> dict:
    text_features = extract_text_features(message)
    metadata_features = extract_metadata_features(message)

    features = {**text_features, **metadata_features}
    risk_score = calculate_risk_score(features)

    if risk_score >= HONEYPOT_THRESHOLD:
        decision = "handoff_to_honeypot"
    elif risk_score >= WARNING_THRESHOLD:
        decision = "warn_user"
    else:
        decision = "safe"

    return {
        "risk_score": risk_score,
        "decision": decision,
        "features": features
    }
