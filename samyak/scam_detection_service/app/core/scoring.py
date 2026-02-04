from app.core.config import MAX_RISK_SCORE


def calculate_risk_score(features: dict) -> int:
    score = 0

    score += features.get("keyword_hits", 0) * 10
    score += features.get("has_url", 0) * 15
    score += features.get("has_phone", 0) * 10
    score += features.get("has_upi", 0) * 15

    if features.get("sentiment", 0) < -0.4:
        score += 15

    if features.get("capital_ratio", 0) > 0.3:
        score += 10

    return min(score, MAX_RISK_SCORE)
