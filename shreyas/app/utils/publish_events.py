import json
from datetime import datetime
from app.storage.redis_client import redis_client

EVENT_QUEUE = "event_queue"


def publish_event(event: dict):
    redis_client.rpush(EVENT_QUEUE, json.dumps(event))


if __name__ == "__main__":
    publish_event({
        "event_id": "1",
        "event_type": "TEST_EVENT",
        "source": "manual",
        "payload": {"message": "Hello team"},
        "timestamp": datetime.utcnow().isoformat()
    })
