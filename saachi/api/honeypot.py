"""
Honeypot Engagement API Endpoint.

FastAPI router for honeypot persona engagement.
Receives SCAM_CONFIRMED events and engages with scammers using persona-based responses.

POST /honeypot/engage
Input: HoneypotEngagementRequest
Output: HoneypotEngagementResponse
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from ..conversation import handle_scammer_message
from ..state_manager import ConversationState
from ..safety import check_safety
from ..extractor import extract_entities
from shared.event_bus import get_event_bus, Event, EventType
from shared.redis_client import RedisSessionStore, get_redis_client

logger = logging.getLogger(__name__)

# Initialize Redis session store
redis_client = get_redis_client()
session_store = RedisSessionStore(redis_client)

# In-memory session storage (backed by Redis when available)
_active_sessions = {}


class HoneypotSession:
    """Tracks an active honeypot engagement session."""

    def __init__(self, session_id: str, conversation_id: str, original_sender_id: str, persona_key: str):
        """Initialize session."""
        self.session_id = session_id
        self.conversation_id = conversation_id
        self.original_sender_id = original_sender_id
        self.persona_key = persona_key
        self.state = ConversationState.INITIAL
        self.messages = []
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

    def add_message(self, sender: str, content: str) -> None:
        """Add message to session history."""
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

        # Store in Redis
        session_store.add_message(self.session_id, message)
        self.last_activity = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "original_sender_id": self.original_sender_id,
            "persona_key": self.persona_key,
            "state": self.state.value,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


def create_honeypot_router() -> APIRouter:
    """Create and return the honeypot engagement router."""
    router = APIRouter()

    @router.post("/honeypot/engage")
    async def engage_honeypot(
        conversation_id: str,
        original_sender_id: str,
        scam_probability: float,
        scam_type: Optional[str] = None,
        initial_message: Optional[str] = None,
        persona_key: str = "elderly_pensioner",
    ):
        """
        Engage honeypot with scammer.

        Args:
            conversation_id: ID of the conversation to engage
            original_sender_id: ID of the original scammer
            scam_probability: Probability score from detection
            scam_type: Type of scam detected (optional)
            initial_message: First message to respond to (optional)
            persona_key: Which persona to use (elderly_pensioner, middle_class_employee, student)

        Returns:
            {
                "session_id": str,
                "status": "accepted",
                "message": str,
                "conversation_id": str
            }
        """
        try:
            # Validate persona
            if persona_key not in ["elderly_pensioner", "middle_class_employee", "student"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid persona: {persona_key}. Must be one of: elderly_pensioner, middle_class_employee, student"
                )

            # Create session
            session_id = f"honeypot_{uuid.uuid4().hex[:12]}"
            session = HoneypotSession(
                session_id=session_id,
                conversation_id=conversation_id,
                original_sender_id=original_sender_id,
                persona_key=persona_key,
            )

            logger.info(
                f"Honeypot engagement initiated: session={session_id}, "
                f"conversation={conversation_id}, scam_prob={scam_probability:.1f}, "
                f"type={scam_type}, persona={persona_key}"
            )

            # If initial message provided, generate response
            if initial_message:
                # Safety check first
                is_safe, refusal = check_safety(initial_message)
                if not is_safe:
                    logger.warning(f"Safety violation detected: {refusal}")
                    session.add_message("scammer", initial_message)
                    session.add_message("honeypot", refusal or "")
                    session.state = ConversationState.EXIT
                    _active_sessions[session_id] = session
                    return {
                        "status": "safety_exit",
                        "session_id": session_id,
                        "conversation_id": conversation_id,
                        "honeypot_session_id": session_id,
                        "message": refusal,
                        "details": {"reason": "Forbidden keyword detected"},
                    }

                # Extract entities (intelligence)
                entities = extract_entities(initial_message)
                logger.debug(f"Extracted entities: {entities}")

                # Generate honeypot response
                response, new_state = handle_scammer_message(
                    initial_message,
                    session.state,
                    persona_key,
                )

                session.add_message("scammer", initial_message or "")
                session.add_message("honeypot", response or "")
                session.state = new_state

                logger.info(
                    f"Generated honeypot response: session={session_id}, "
                    f"state={new_state.value}, entities={list(entities.keys())}"
                )
            else:
                # No initial message; just initialize the session
                response = f"Hello, this is {persona_key.replace('_', ' ')}. How can I help you?"
                session.add_message("honeypot", response)

            # Store session
            _active_sessions[session_id] = session

            return {
                "status": "accepted",
                "session_id": session_id,
                "conversation_id": conversation_id,
                "honeypot_session_id": session_id,
                "message": response,
                "state": session.state.value,
                "details": session.to_dict(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in honeypot engagement: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Engagement error: {str(e)}")

    @router.post("/honeypot/message")
    async def send_honeypot_message(session_id: str, message: str):
        """
        Send a message to an active honeypot session.

        Args:
            session_id: Active session ID
            message: Message from scammer

        Returns:
            {"message": str, "state": str, "entities": dict}
        """
        try:
            if session_id not in _active_sessions:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            session = _active_sessions[session_id]

            # Safety check
            is_safe, refusal = check_safety(message)
            if not is_safe:
                logger.warning(f"Safety violation in session {session_id}: {refusal}")
                session.add_message("scammer", message or "")
                session.add_message("honeypot", refusal or "")
                session.state = ConversationState.EXIT
                return {
                    "message": refusal,
                    "state": "exit",
                    "session_id": session_id,
                    "reason": "Forbidden keyword detected",
                }

            # Extract entities
            entities = extract_entities(message)

            # Generate response
            response, new_state = handle_scammer_message(
                message,
                session.state,
                session.persona_key,
            )

            session.add_message("scammer", message or "")
            session.add_message("honeypot", response or "")
            session.state = new_state

            logger.info(
                f"Honeypot message processed: session={session_id}, "
                f"state={new_state.value}, entities={list(entities.keys())}"
            )

            return {
                "message": response,
                "state": new_state.value,
                "session_id": session_id,
                "entities": entities,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing honeypot message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Message error: {str(e)}")

    @router.get("/honeypot/session/{session_id}")
    async def get_session(session_id: str):
        """Get session details and history."""
        try:
            if session_id not in _active_sessions:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            session = _active_sessions[session_id]
            return {
                "session": session.to_dict(),
                "message_count": len(session.messages),
                "last_message": session.messages[-1] if session.messages else None,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    @router.get("/honeypot/health")
    async def honeypot_health():
        """Health check for honeypot service."""
        return {
            "status": "healthy",
            "service": "honeypot",
            "active_sessions": len(_active_sessions),
        }

    return router


def engage_session(
    conversation_id: str,
    original_sender_id: str,
    scam_probability: float,
    scam_type: Optional[str] = None,
    initial_message: Optional[str] = None,
    persona_key: str = "elderly_pensioner",
):
    """
    Programmatic helper to create a honeypot session and emit a HONEYPOT_ENGAGED event.

    Returns the same dictionary payload as the HTTP endpoint.
    """
    try:
        # Validate persona
        if persona_key not in ["elderly_pensioner", "middle_class_employee", "student"]:
            raise ValueError(f"Invalid persona: {persona_key}")

        # Create session
        session_id = f"honeypot_{uuid.uuid4().hex[:12]}"
        session = HoneypotSession(
            session_id=session_id,
            conversation_id=conversation_id,
            original_sender_id=original_sender_id,
            persona_key=persona_key,
        )

        # If initial message provided, process it (safety, extraction, reply)
        response = None
        if initial_message:
            is_safe, refusal = check_safety(initial_message)
            if not is_safe:
                session.add_message("scammer", initial_message or "")
                session.add_message("honeypot", refusal or "")
                session.state = ConversationState.EXIT
                _active_sessions[session_id] = session

                # Emit HONEYPOT_ENGAGED event for downstream extraction/processing
                try:
                    bus = get_event_bus()
                    payload = {
                        "conversation_id": conversation_id,
                        "honeypot_session_id": session_id,
                        "original_sender_id": original_sender_id,
                        "persona_key": persona_key,
                        "message": initial_message,
                        "scam_probability": scam_probability,
                        "scam_type": scam_type,
                    }
                    bus_event = Event(
                        event_type=EventType.HONEYPOT_ENGAGED,
                        conversation_id=conversation_id,
                        timestamp=datetime.utcnow(),
                        payload=payload,
                        source_service="honeypot",
                    )
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(bus.emit(bus_event))
                        else:
                            loop.run_until_complete(bus.emit(bus_event))
                    except RuntimeError:
                        asyncio.run(bus.emit(bus_event))
                except Exception:
                    logger.exception("Failed to emit HONEYPOT_ENGAGED event")

                return {
                    "status": "safety_exit",
                    "session_id": session_id,
                    "conversation_id": conversation_id,
                    "honeypot_session_id": session_id,
                    "message": refusal,
                    "details": {"reason": "Forbidden keyword detected"},
                }

            entities = extract_entities(initial_message)
            response, new_state = handle_scammer_message(
                initial_message,
                session.state,
                persona_key,
            )

            session.add_message("scammer", initial_message or "")
            session.add_message("honeypot", response or "")
            session.state = new_state

        else:
            response = f"Hello, this is {persona_key.replace('_', ' ')}. How can I help you?"
            session.add_message("honeypot", response)

        # Store session
        _active_sessions[session_id] = session

        # Emit HONEYPOT_ENGAGED for downstream consumers
        try:
            bus = get_event_bus()
            payload = {
                "conversation_id": conversation_id,
                "honeypot_session_id": session_id,
                "original_sender_id": original_sender_id,
                "persona_key": persona_key,
                "message": initial_message or response,
                "scam_probability": scam_probability,
                "scam_type": scam_type,
            }
            bus_event = Event(
                event_type=EventType.HONEYPOT_ENGAGED,
                conversation_id=conversation_id,
                timestamp=datetime.utcnow(),
                payload=payload,
                source_service="honeypot",
            )
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(bus.emit(bus_event))
                else:
                    loop.run_until_complete(bus.emit(bus_event))
            except RuntimeError:
                asyncio.run(bus.emit(bus_event))
        except Exception:
            logger.exception("Failed to emit HONEYPOT_ENGAGED event")

        return {
            "status": "accepted",
            "session_id": session_id,
            "conversation_id": conversation_id,
            "honeypot_session_id": session_id,
            "message": response,
            "state": session.state.value,
            "details": session.to_dict(),
        }
