"""
Pydantic models for Honeypot Test API

Defines request and response schemas for validation and documentation.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Individual message in conversation"""
    sender: str = Field(..., description="Sender identifier (e.g., 'user', 'scammer')")
    text: str = Field(..., description="Message content")


class Metadata(BaseModel):
    """Optional metadata about the conversation"""
    source: Optional[str] = Field(None, description="Source of conversation (e.g., 'telegram', 'email')")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")


class HoneypotTestRequest(BaseModel):
    """Request model for honeypot test endpoint"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    messages: List[Message] = Field(..., description="List of messages in conversation")
    metadata: Optional[Metadata] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_12345",
                "messages": [
                    {"sender": "scammer", "text": "Hello, your account is at risk!"},
                    {"sender": "user", "text": "Really? What should I do?"}
                ],
                "metadata": {"source": "telegram"}
            }
        }


class HoneypotTestResponse(BaseModel):
    """Response model for honeypot test endpoint"""
    status: str = Field(..., description="API status (e.g., 'ok')")
    honeypot_active: bool = Field(..., description="Whether honeypot is active")
    scam_probability: float = Field(..., description="Scam score 0-100")
    handoff: bool = Field(..., description="Whether to trigger handoff to next agent")
    message: str = Field(..., description="Status message or explanation")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "honeypot_active": True,
                "scam_probability": 87.5,
                "handoff": True,
                "message": "Scam detected with high confidence. Handing off to Saachi."
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field(..., description="Error status")
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="HTTP status code")
