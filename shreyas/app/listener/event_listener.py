import json
import logging
from app.storage.redis_client import redis_client
from app.schemas.event import Event

logger = logging.getLogger(__name__)

EVENT_QUEUE = "event_queue"


def start_event_listener():
    logger.info("🚀 Event listener started. Waiting for events...")

    while True:
        try:
            _, raw_event = redis_client.blpop(EVENT_QUEUE)
            event_data = json.loads(raw_event)

            event = Event(**event_data)
            handle_event(event)

        except Exception as e:
            logger.exception(f"❌ Listener error: {e}")


def handle_event(event: Event):
    logger.info(
        f"📥 Event received | type={event.event_type} | source={event.source}"
    )

    # TODO: route to classifier / timeline / storage
