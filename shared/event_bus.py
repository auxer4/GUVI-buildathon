"""
Event Bus for inter-agent communication.

Placeholder for event publishing and subscription system.
Will be implemented as part of system integration.

TODO:
- Implement pub/sub with Redis or RabbitMQ
- Define event subscriptions for each agent
- Add event filtering and routing logic
- Implement backoff and retry logic
- Add event persistence
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standard event types in the system."""
    SCAM_DETECTED = "SCAM_DETECTED"
    SCAM_CONFIRMED = "SCAM_CONFIRMED"
    HONEYPOT_ENGAGED = "HONEYPOT_ENGAGED"
    RECOVERY_INITIATED = "RECOVERY_INITIATED"
    THREAT_INTELLIGENCE_UPDATE = "THREAT_INTELLIGENCE_UPDATE"


@dataclass
class Event:
    """Standard event structure."""
    event_type: EventType
    conversation_id: str
    timestamp: datetime
    payload: Dict[str, Any]
    source_service: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EventBus:
    """
    In-memory event bus for inter-agent communication.
    
    In production, this would be replaced with:
    - Redis Streams
    - RabbitMQ
    - Apache Kafka
    - AWS EventBridge
    """

    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 10000

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async callable that handles the event
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type.value}: {handler.__name__}")

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe from events.

        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            logger.info(f"Unsubscribed from {event_type.value}: {handler.__name__}")

    async def emit(self, event: Event) -> None:
        """
        Emit an event to all subscribers.

        Args:
            event: Event to emit
        """
        logger.debug(f"Emitting event: {event.event_type.value} "
                    f"(conversation: {event.conversation_id})")

        # Store in history
        self._add_to_history(event)

        # Notify subscribers
        if event.event_type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__}: {e}")

            # Run async handlers concurrently
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        else:
            logger.debug(f"No subscribers for {event.event_type.value}")

    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size management."""
        self.event_history.append(event)

        # Keep history size manageable
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

    def get_events_for_conversation(self, conversation_id: str) -> List[Event]:
        """
        Retrieve all events for a specific conversation.

        Args:
            conversation_id: Conversation ID to filter

        Returns:
            List of events matching the conversation
        """
        return [e for e in self.event_history if e.conversation_id == conversation_id]

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """
        Retrieve all events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of events matching the type
        """
        return [e for e in self.event_history if e.event_type == event_type]

    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")


# Global event bus instance
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create global event bus instance."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


def reset_event_bus() -> None:
    """Reset event bus (useful for testing)."""
    global _event_bus_instance
    _event_bus_instance = None
