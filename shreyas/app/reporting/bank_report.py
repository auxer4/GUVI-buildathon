from reporting.base_report import base_report

def generate_bank_report(
    case_id: str,
    scam_type: str,
    confidence: float,
    entities: list,
    timeline: list
) -> dict:

    risky_entities = [
        e for e in entities if e["type"] in {"UPI_ID", "BANK_ACCOUNT", "CARD_NUMBER"}
    ]

    report = base_report(
        case_id=case_id,
        scam_type=scam_type,
        confidence=confidence,
        entities=risky_entities,
        timeline=timeline
    )

    report.update({
        "audience": "BANK",
        "risk_level": "HIGH" if confidence >= 0.75 else "MEDIUM",
        "recommended_actions": [
            "Monitor listed identifiers",
            "Apply transaction velocity limits",
            "Freeze accounts if corroborated"
        ]
    })

    return report
