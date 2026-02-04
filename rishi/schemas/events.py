"""
Event Schemas for Scam Detection System.
Pydantic models for structured communication with event_bus and other agents.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk assessment levels for scam detection."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH = "high"
    CONFIRMED = "confirmed"


class DetectorBreakdown(BaseModel):
    """Normalized detector scores (0.0-1.0)."""
    linguistic_score: float = Field(..., ge=0.0, le=1.0)
    behavioral_score: float = Field(..., ge=0.0, le=1.0)
    link_infrastructure_score: float = Field(..., ge=0.0, le=1.0)
    identity_mismatch_score: float = Field(..., ge=0.0, le=1.0)
    historical_score: float = Field(..., ge=0.0, le=1.0)


class ScamDetectionResult(BaseModel):
    """Final scam detection output."""
    conversation_id: str
    scam_probability: float = Field(..., ge=0.0, le=100.0, description="0-100 scale")
    risk_level: RiskLevel
    breakdown: DetectorBreakdown
    handoff_triggered: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""
    message_id: str
    sender: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class SenderMetadata(BaseModel):
    """Metadata about the message sender."""
    user_id: str
    account_age_days: Optional[int] = None
    previous_reports: Optional[int] = None
    verification_status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScamDetectionInput(BaseModel):
    """Input schema for scam detection endpoint."""
    conversation_id: str
    messages: List[ConversationMessage]
    sender_metadata: SenderMetadata


class ScamConfirmedEvent(BaseModel):
    """Event emitted when scam is confirmed for handoff to honeypot agent."""
    event_type: str = "SCAM_CONFIRMED"
    conversation_id: str
    scam_probability: float
    risk_level: RiskLevel
    detector_breakdown: DetectorBreakdown
    scam_type: Optional[str] = None  # e.g., "financial", "romance", "tech_support"
    recommended_action: str = "honeypot_engagement"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectorInput(BaseModel):
    """Standard input for any detector module."""
    conversation_id: str
    messages: List[ConversationMessage]
    sender_metadata: SenderMetadata
    context: Optional[Dict[str, Any]] = None
