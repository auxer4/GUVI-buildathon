"""
Main Detection API Endpoint.

FastAPI endpoint that orchestrates the scam detection pipeline.
POST /detect-scam

Input:
- conversation_id: str
- messages: List[ConversationMessage]
- sender_metadata: SenderMetadata

Output:
- scam_probability: float (0-100)
- risk_level: str (safe|suspicious|high|confirmed)
- breakdown: Dict[str, float]
- handoff_triggered: bool
"""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..schemas.events import (
    ScamDetectionInput,
    ScamDetectionResult,
    DetectorBreakdown,
    DetectorInput,
)
from ..detectors.linguistic import LinguisticManipulationDetector
from ..detectors.behavioral import BehavioralPatternDetector
from ..detectors.link_intel import LinkIntelligenceDetector
from ..detectors.identity_mismatch import IdentityMismatchDetector
from ..detectors.historical import HistoricalPatternDetector
from ..scoring.risk_fusion import RiskFusionEngine
from ..handoff.handoff_router import HandoffRouter

logger = logging.getLogger(__name__)

# Initialize detectors (singleton-like pattern)
_linguistic_detector = LinguisticManipulationDetector()
_behavioral_detector = BehavioralPatternDetector()
_link_detector = LinkIntelligenceDetector()
_identity_detector = IdentityMismatchDetector()
_historical_detector = HistoricalPatternDetector()
_fusion_engine = RiskFusionEngine()
_handoff_router = HandoffRouter()


def create_detect_router() -> APIRouter:
    """Create and return the detection API router."""
    router = APIRouter()

    @router.post("/detect-scam", response_model=ScamDetectionResult)
    async def detect_scam(input_data: ScamDetectionInput) -> ScamDetectionResult:
        """
        Main scam detection endpoint.

        Args:
            input_data: ScamDetectionInput with conversation and metadata

        Returns:
            ScamDetectionResult with probability, risk level, and breakdown

        Raises:
            HTTPException: If input is invalid or processing fails
        """
        try:
            # Validate input
            if not input_data.conversation_id:
                raise HTTPException(status_code=400, detail="Missing conversation_id")

            if not input_data.messages:
                raise HTTPException(status_code=400, detail="No messages provided")

            logger.info(
                f"Processing scam detection for {input_data.conversation_id} "
                f"({len(input_data.messages)} messages)"
            )

            # Create detector input
            detector_input = DetectorInput(
                conversation_id=input_data.conversation_id,
                messages=input_data.messages,
                sender_metadata=input_data.sender_metadata,
            )

            # Run all detectors in parallel (conceptually - can be optimized with asyncio)
            linguistic_score = _linguistic_detector.analyze(detector_input)
            behavioral_score = _behavioral_detector.analyze(detector_input)
            link_score = _link_detector.analyze(detector_input)
            identity_score = _identity_detector.analyze(detector_input)
            historical_score = _historical_detector.analyze(detector_input)

            logger.debug(
                f"Detector scores for {input_data.conversation_id}: "
                f"linguistic={linguistic_score:.3f}, behavioral={behavioral_score:.3f}, "
                f"link={link_score:.3f}, identity={identity_score:.3f}, "
                f"historical={historical_score:.3f}"
            )

            # Create breakdown
            breakdown = DetectorBreakdown(
                linguistic_score=linguistic_score,
                behavioral_score=behavioral_score,
                link_infrastructure_score=link_score,
                identity_mismatch_score=identity_score,
                historical_score=historical_score,
            )

            # Fuse scores
            detection_result = _fusion_engine.fuse(detector_input, breakdown)

            # Check if handoff is needed
            if detection_result.handoff_triggered:
                handoff_event = _handoff_router.process_detection_result(
                    detection_result, detector_input
                )
                logger.warning(
                    f"Handoff triggered for {input_data.conversation_id}: {handoff_event}"
                )

            return detection_result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in scam detection: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    return router


# For standalone usage or testing
if __name__ == "__main__":
    from fastapi import FastAPI

    app = FastAPI(title="Scam Intelligence Engine - Rishi Module")
    router = create_detect_router()
    app.include_router(router)

    logger.info("Scam Detection API initialized")
