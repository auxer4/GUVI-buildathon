from datetime import datetime
import uuid

def base_report(
    case_id: str,
    scam_type: str,
    confidence: float,
    entities: list,
    timeline: list
) -> dict:
    return {
        "report_id": str(uuid.uuid4()),
        "case_id": case_id,
        "generated_at": datetime.utcnow().isoformat(),
        "scam_type": scam_type,
        "confidence": confidence,
        "entities": entities,
        "timeline": timeline
    }
