"""
Shared Message Models for inter-agent communication.

These models define the contract between different agents in the system.
Each agent produces and consumes messages following these schemas.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system."""
    SCAM_DETECTION = "scam_detection"
    HONEYPOT = "honeypot"
    EXTRACTOR = "extractor"
    RECOVERY = "recovery"
    THREAT_INTELLIGENCE = "threat_intelligence"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH = "high"
    CONFIRMED = "confirmed"


class MessageType(str, Enum):
    """Types of inter-agent messages."""
    SCAM_DETECTION_REQUEST = "scam_detection_request"
    SCAM_DETECTION_RESULT = "scam_detection_result"
    SCAM_CONFIRMED = "scam_confirmed"
    HONEYPOT_ENGAGEMENT_REQUEST = "honeypot_engagement_request"
    HONEYPOT_ENGAGEMENT_RESPONSE = "honeypot_engagement_response"
    EXTRACTION_REQUEST = "extraction_request"
    EXTRACTION_RESULT = "extraction_result"
    RECOVERY_INITIATION = "recovery_initiation"
    THREAT_INTELLIGENCE_UPDATE = "threat_intelligence_update"


class DetectorResult(BaseModel):
    """Result from a single detector."""
    detector_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    details: Optional[Dict[str, Any]] = None


class ScamDetectionResultMessage(BaseModel):
    """Message published when scam detection completes."""
    message_type: MessageType = MessageType.SCAM_DETECTION_RESULT
    conversation_id: str
    scam_probability: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevel
    detector_breakdown: Dict[str, DetectorResult]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"
    metadata: Optional[Dict[str, Any]] = None


class ScamConfirmedMessage(BaseModel):
    """Message published when a scam is confirmed."""
    message_type: MessageType = MessageType.SCAM_CONFIRMED
    conversation_id: str
    scam_probability: float
    risk_level: RiskLevel
    scam_type: Optional[str] = None
    detector_breakdown: Dict[str, DetectorResult]
    recommended_action: str = "honeypot_engagement"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"
    metadata: Optional[Dict[str, Any]] = None


class HoneypotEngagementRequest(BaseModel):
    """Request sent to honeypot agent."""
    message_type: MessageType = MessageType.HONEYPOT_ENGAGEMENT_REQUEST
    conversation_id: str
    original_sender_id: str
    scam_probability: float
    scam_type: Optional[str] = None
    initial_context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"


class HoneypotEngagementResponse(BaseModel):
    """Response from honeypot agent."""
    message_type: MessageType = MessageType.HONEYPOT_ENGAGEMENT_RESPONSE
    conversation_id: str
    honeypot_session_id: str
    status: str  # "accepted", "rejected", "pending"
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "honeypot"


class ExtractionRequest(BaseModel):
    """Request sent to extraction agent."""
    message_type: MessageType = MessageType.EXTRACTION_REQUEST
    conversation_id: str
    scam_type: Optional[str] = None
    message_history: List[Dict[str, str]]
    priority: str = "normal"  # "low", "normal", "high"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"


class ExtractionResult(BaseModel):
    """Result from extraction agent."""
    message_type: MessageType = MessageType.EXTRACTION_RESULT
    conversation_id: str
    extracted_data: Dict[str, Any]
    confidence_scores: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "extractor"


class RecoveryInitiation(BaseModel):
    """Initiation of recovery process."""
    message_type: MessageType = MessageType.RECOVERY_INITIATION
    conversation_id: str
    victim_id: str
    scam_type: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"


class ThreatIntelligenceUpdate(BaseModel):
    """Update to threat intelligence database."""
    message_type: MessageType = MessageType.THREAT_INTELLIGENCE_UPDATE
    conversation_id: str
    threat_signature: Dict[str, Any]
    severity: RiskLevel
    indicators: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "scam_detection"


# Type alias for any inter-agent message
InterAgentMessage = (
    ScamDetectionResultMessage
    | ScamConfirmedMessage
    | HoneypotEngagementRequest
    | HoneypotEngagementResponse
    | ExtractionRequest
    | ExtractionResult
    | RecoveryInitiation
    | ThreatIntelligenceUpdate
)
