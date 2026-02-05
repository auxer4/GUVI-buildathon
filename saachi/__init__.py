"""
Saachi: Honeypot Persona & Engagement Module
Person 2 responsibility for the Scam Intelligence Engine

Provides AI-driven honeypot engagement with configurable personas.
"""

from .conversation import handle_scammer_message
from .state_manager import ConversationState
from .safety import check_safety
from .extractor import extract_entities
from .persona import PERSONAS
from .api.honeypot import create_honeypot_router

__version__ = "1.0.0"
__author__ = "Saachi"

__all__ = [
    "handle_scammer_message",
    "ConversationState",
    "check_safety",
    "extract_entities",
    "PERSONAS",
    "create_honeypot_router",
]
