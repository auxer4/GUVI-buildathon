"""
Shared utilities and models for inter-agent communication.

This package contains:
- event_bus.py: Event publication/subscription system
- message_models.py: Standardized inter-agent message schemas
- constants.py: System-wide constants and enums
"""

from .event_bus import EventBus, Event, EventType, get_event_bus, reset_event_bus
from .message_models import (
    AgentType,
    RiskLevel,
    MessageType,
    ScamDetectionResultMessage,
    ScamConfirmedMessage,
    HoneypotEngagementRequest,
    HoneypotEngagementResponse,
    ExtractionRequest,
    ExtractionResult,
    RecoveryInitiation,
    ThreatIntelligenceUpdate,
)

__all__ = [
    "EventBus",
    "Event",
    "EventType",
    "get_event_bus",
    "reset_event_bus",
    "AgentType",
    "RiskLevel",
    "MessageType",
    "ScamDetectionResultMessage",
    "ScamConfirmedMessage",
    "HoneypotEngagementRequest",
    "HoneypotEngagementResponse",
    "ExtractionRequest",
    "ExtractionResult",
    "RecoveryInitiation",
    "ThreatIntelligenceUpdate",
]
