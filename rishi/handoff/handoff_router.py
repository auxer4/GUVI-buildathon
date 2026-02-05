"""
Handoff Router.

Emits SCAM_CONFIRMED event when a scam is detected with high confidence.
Routes to honeypot engagement pipeline.

This module communicates with other agents via shared/event_bus.
"""

import logging
from typing import Optional
from datetime import datetime

from ..schemas.events import (
    ScamDetectionResult,
    ScamConfirmedEvent,
    RiskLevel,
    DetectorInput,
)

logger = logging.getLogger(__name__)


class HandoffRouter:
    """
    Routes confirmed scams to honeypot engagement pipeline.
    """

    def __init__(self, event_bus=None):
        """
        Initialize router.

        Args:
            event_bus: Reference to shared event_bus for emitting events.
                      Injected from the detection API for event publishing.
        """
        self.event_bus = event_bus
        if event_bus is None:
            logger.warning("HandoffRouter initialized without event_bus; events will not be published")

    def process_detection_result(
        self,
        detection_result: ScamDetectionResult,
        detector_input: Optional[DetectorInput] = None,
    ) -> Optional[ScamConfirmedEvent]:
        """
        Process detection result and emit event if handoff is triggered.

        Args:
            detection_result: Result from risk fusion engine
            detector_input: Original input for additional context

        Returns:
            ScamConfirmedEvent if handoff triggered, None otherwise
        """
        if not detection_result.handoff_triggered:
            logger.debug(f"No handoff for {detection_result.conversation_id}")
            return None

        # Create and emit confirmation event
        event = ScamConfirmedEvent(
            conversation_id=detection_result.conversation_id,
            scam_probability=detection_result.scam_probability,
            risk_level=detection_result.risk_level,
            detector_breakdown=detection_result.breakdown,
            scam_type=self._infer_scam_type(detection_result, detector_input),
            recommended_action="honeypot_engagement",
            metadata={
                "original_sender": detector_input.sender_metadata.user_id
                if detector_input
                else None,
                "message_count": len(detector_input.messages) if detector_input else 0,
            },
        )

        # Emit to event_bus
        self._emit_event(event)

        logger.warning(
            f"SCAM CONFIRMED: {detection_result.conversation_id} "
            f"(probability={detection_result.scam_probability:.1f}, "
            f"type={event.scam_type})"
        )

        return event

    def _infer_scam_type(
        self,
        detection_result: ScamDetectionResult,
        detector_input: Optional[DetectorInput] = None,
    ) -> Optional[str]:
        """
        Infer scam type based on detector breakdown.

        Args:
            detection_result: Detection result with breakdown
            detector_input: Original input for additional context

        Returns:
            Inferred scam type or None
        """
        breakdown = detection_result.breakdown

        # Heuristics for scam type classification
        if breakdown.identity_mismatch_score > 0.7:
            return "impersonation"
        elif breakdown.linguistic_score > 0.7 and breakdown.behavioral_score > 0.7:
            return "social_engineering"
        elif breakdown.link_infrastructure_score > 0.7:
            return "phishing"
        elif breakdown.linguistic_score > 0.7:  # Reward baiting is detected through linguistic analysis
            return "romance_or_advance_fee"
        else:
            return "unknown"

    def _emit_event(self, event: ScamConfirmedEvent) -> None:
        """
        Emit event to event_bus for inter-agent communication.

        Args:
            event: ScamConfirmedEvent to emit

        This signals the honeypot agent to engage with the scammer.
        """
        if self.event_bus is None:
            logger.warning("event_bus not available; event not emitted")
            logger.debug(f"Event payload: {event.model_dump_json()}")
            return

        try:
            from shared.event_bus import Event, EventType
            from datetime import datetime

            # Convert ScamConfirmedEvent to Event for event_bus
            bus_event = Event(
                event_type=EventType.SCAM_CONFIRMED,
                conversation_id=event.conversation_id,
                timestamp=datetime.utcnow(),
                payload=event.model_dump(),
                source_service="scam_detection",
                metadata=event.metadata,
            )

            # Emit event asynchronously
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, create task
                    loop.create_task(self.event_bus.emit(bus_event))
                else:
                    # Otherwise run it directly
                    loop.run_until_complete(self.event_bus.emit(bus_event))
            except RuntimeError:
                # No event loop; try to create one
                asyncio.run(self.event_bus.emit(bus_event))

            logger.info(f"Event emitted: {event.event_type} for {event.conversation_id}")

        except Exception as e:
            logger.error(f"Error emitting event: {e}", exc_info=True)


class ConversationHandoffMetadata:
    """
    Stores metadata for conversation handoff.
    Useful for tracking handoff status and honeypot engagement.
    """

    def __init__(self, conversation_id: str):
        """Initialize metadata."""
        self.conversation_id = conversation_id
        self.handoff_time: Optional[datetime] = None
        self.honeypot_engaged: bool = False
        self.honeypot_session_id: Optional[str] = None
        self.initial_scam_score: Optional[float] = None
        self.engagement_status: str = "pending"  # pending, active, completed

    def mark_engaged(self, session_id: str) -> None:
        """Mark conversation as engaged by honeypot."""
        self.honeypot_engaged = True
        self.honeypot_session_id = session_id
        self.engagement_status = "active"
        self.handoff_time = datetime.utcnow()
        logger.info(
            f"Handoff engagement recorded: {self.conversation_id} -> {session_id}"
        )

    def mark_completed(self) -> None:
        """Mark honeypot engagement as completed."""
        self.engagement_status = "completed"
        logger.info(f"Honeypot engagement completed: {self.conversation_id}")
