from reporting.base_report import base_report

def generate_internal_report(
    case_id: str,
    scam_type: str,
    confidence: float,
    entities: list,
    timeline: list,
    reasoning: list
) -> dict:

    report = base_report(
        case_id=case_id,
        scam_type=scam_type,
        confidence=confidence,
        entities=entities,
        timeline=timeline
    )

    report.update({
        "audience": "INTERNAL",
        "classification_reasoning": reasoning,
        "entity_count": len(entities),
        "tags": [scam_type.lower()]
    })

    return report
