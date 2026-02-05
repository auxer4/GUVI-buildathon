from reporting.base_report import base_report

def generate_law_enforcement_report(
    case_id: str,
    scam_type: str,
    confidence: float,
    entities: list,
    timeline: list
) -> dict:

    report = base_report(
        case_id=case_id,
        scam_type=scam_type,
        confidence=confidence,
        entities=entities,
        timeline=timeline
    )

    report.update({
        "audience": "LAW_ENFORCEMENT",
        "recommended_actions": [
            "Preserve evidence",
            "Initiate financial trail analysis",
            "Request UPI / bank freeze if applicable"
        ],
        "legal_notes": [
            "All timestamps are UTC",
            "Raw events are hash-preserved",
            "No victim PII exposed"
        ]
    })

    return report
