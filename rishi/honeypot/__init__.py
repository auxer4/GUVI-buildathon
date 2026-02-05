"""
Honeypot Engagement Module - Person 1

Handles conversation simulation with scammers to:
- Engage confirmed scams after detection
- Simulate realistic victim responses
- Extract intelligence from scammer behavior
- Maintain safety constraints
"""

from .conversation import handle_scammer_message, generate_stub_reply
from .persona import PERSONAS
from .state_manager import ConversationState, determine_next_state
from .safety import check_safety
from .extractor import extract_entities
from .demo_runner import main as run_demo

__all__ = [
    "handle_scammer_message",
    "generate_stub_reply",
    "PERSONAS",
    "ConversationState",
    "determine_next_state",
    "check_safety",
    "extract_entities",
    "run_demo",
]
