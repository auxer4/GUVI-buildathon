"""
Redis client for session and event persistence.
Handles singleton connection and pooling.
"""

import json
import logging
from typing import Any, Dict, Optional
import redis
from contextlib import contextmanager

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def get_redis_client(host: str = "localhost", port: int = 6379, db: int = 0) -> redis.Redis:
    """
    Get or create a Redis client (singleton).

    Args:
        host: Redis server host
        port: Redis server port
        db: Redis database number

    Returns:
        Redis client instance
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            _redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using in-memory fallback.")
            return None

    return _redis_client


class RedisSessionStore:
    """Persistent session storage using Redis."""

    def __init__(self, redis_client: Optional[redis.Redis] = None, ttl: int = 3600):
        """
        Initialize session store.

        Args:
            redis_client: Redis client instance
            ttl: Session TTL in seconds (default 1 hour)
        """
        self.redis_client = redis_client or get_redis_client()
        self.ttl = ttl
        self.prefix = "honeypot:session:"

    def create_session(self, session_id: str, conversation_id: str, sender_id: str) -> Dict[str, Any]:
        """
        Create a new honeypot session.

        Args:
            session_id: Unique session ID
            conversation_id: ID of the conversation being tracked
            sender_id: ID of the sender/scammer

        Returns:
            Session dict
        """
        session_data = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "created_at": __import__("datetime").datetime.utcnow().isoformat(),
            "messages": [],
            "engagement_score": 0.0,
            "status": "active",
        }

        if self.redis_client:
            try:
                key = f"{self.prefix}{session_id}"
                self.redis_client.setex(key, self.ttl, json.dumps(session_data))
                logger.debug(f"Session {session_id} created in Redis")
            except Exception as e:
                logger.warning(f"Failed to store session in Redis: {e}")

        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a honeypot session.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session dict or None if not found
        """
        if self.redis_client:
            try:
                key = f"{self.prefix}{session_id}"
                data = self.redis_client.get(key)
                if data:
                    logger.debug(f"Session {session_id} retrieved from Redis")
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Failed to retrieve session from Redis: {e}")

        return None

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID to update
            updates: Dictionary of fields to update

        Returns:
            True if successful
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.prefix}{session_id}"
            session = self.redis_client.get(key)
            if session:
                session_data = json.loads(session)
                session_data.update(updates)
                self.redis_client.setex(key, self.ttl, json.dumps(session_data))
                logger.debug(f"Session {session_id} updated in Redis")
                return True
        except Exception as e:
            logger.error(f"Failed to update session: {e}")

        return False

    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        Add a message to the session.

        Args:
            session_id: Session ID
            message: Message dict with role, content, timestamp

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if session:
            if "messages" not in session:
                session["messages"] = []
            session["messages"].append(message)
            return self.update_session(session_id, {"messages": session["messages"]})

        return False

    def close_session(self, session_id: str) -> bool:
        """
        Close/end a session.

        Args:
            session_id: Session ID to close

        Returns:
            True if successful
        """
        return self.update_session(session_id, {"status": "closed"})

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from Redis.

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.prefix}{session_id}"
            self.redis_client.delete(key)
            logger.debug(f"Session {session_id} deleted from Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")

        return False

    def get_all_sessions(self, sender_id: Optional[str] = None) -> list:
        """
        Get all active sessions, optionally filtered by sender.

        Args:
            sender_id: Optional sender ID to filter

        Returns:
            List of session dicts
        """
        if not self.redis_client:
            return []

        try:
            pattern = f"{self.prefix}*"
            keys = self.redis_client.keys(pattern)
            sessions = []

            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    session = json.loads(data)
                    if sender_id is None or session.get("sender_id") == sender_id:
                        sessions.append(session)

            return sessions
        except Exception as e:
            logger.error(f"Failed to retrieve sessions: {e}")

        return []


class RedisEventStore:
    """Persistent event storage using Redis."""

    def __init__(self, redis_client: Optional[redis.Redis] = None, ttl: int = 86400):
        """
        Initialize event store.

        Args:
            redis_client: Redis client instance
            ttl: Event TTL in seconds (default 24 hours)
        """
        self.redis_client = redis_client or get_redis_client()
        self.ttl = ttl
        self.prefix = "honeypot:event:"

    def store_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Store an event.

        Args:
            event_type: Type of event
            event_data: Event data dict

        Returns:
            True if successful
        """
        if not self.redis_client:
            return False

        try:
            event_id = event_data.get("event_id", __import__("uuid").uuid4().hex)
            key = f"{self.prefix}{event_type}:{event_id}"
            self.redis_client.setex(key, self.ttl, json.dumps(event_data))
            logger.debug(f"Event {event_id} stored in Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to store event: {e}")

        return False

    def get_events(self, event_type: str) -> list:
        """
        Get all events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of event dicts
        """
        if not self.redis_client:
            return []

        try:
            pattern = f"{self.prefix}{event_type}:*"
            keys = self.redis_client.keys(pattern)
            events = []

            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    events.append(json.loads(data))

            return sorted(events, key=lambda e: e.get("timestamp", ""), reverse=True)
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")

        return []
