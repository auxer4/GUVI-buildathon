"""
Listener package for Person 4 Intelligence Service.

Responsibilities:
- Consume events from the event bus
- Route events to downstream intelligence modules
- Never mutate incoming data
"""

from listener.event_listener import start_listener
from listener.event_router import route_event

__all__ = [
    "start_listener",
    "route_event"
]
