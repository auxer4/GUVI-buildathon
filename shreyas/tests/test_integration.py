"""
Integration tests for the complete scam intelligence pipeline.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from shared.event_bus import get_event_bus, EventType, Event


client = TestClient(app)


@pytest.fixture
def event_bus():
    """Get event bus instance."""
    return get_event_bus()


class TestSystemEndpoints:
    """Test system endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "modules" in data

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_system_info_endpoint(self):
        """Test system info endpoint."""
        response = client.get("/system/info")
        assert response.status_code == 200
        data = response.json()
        assert "modules" in data
        assert "communication" in data


class TestDetectionEndpoint:
    """Test detection endpoint."""

    def test_detect_scam_endpoint_exists(self):
        """Test that detection endpoint exists."""
        # Try to detect a test message
        payload = {
            "text": "Hey, I'm from your bank. Verify your account by clicking here.",
            "metadata": {
                "sender_id": "unknown",
                "platform": "whatsapp",
            },
        }
        response = client.post("/detect-scam", json=payload)
        # Should not return 404
        assert response.status_code != 404


class TestHoneypotEndpoint:
    """Test honeypot endpoint."""

    def test_honeypot_endpoint_exists(self):
        """Test that honeypot endpoint exists."""
        payload = {
            "conversation_id": "test_conv_001",
            "sender_id": "test_scammer",
            "initial_message": "Hello, can you help me?",
        }
        response = client.post("/honeypot/engage", json=payload)
        # Should not return 404
        assert response.status_code != 404


class TestEventBus:
    """Test event bus functionality."""

    def test_event_bus_subscription(self, event_bus):
        """Test event bus subscription."""
        received_events = []

        def on_test_event(event):
            received_events.append(event)

        event_bus.subscribe(EventType.SCAM_CONFIRMED, on_test_event)

        # Emit test event
        test_event = Event(
            event_type=EventType.SCAM_CONFIRMED,
            conversation_id="test_123",
            payload={"test": "data"},
        )
        event_bus.emit(test_event)

        # Check if event was received
        assert len(received_events) > 0

    def test_multiple_subscribers(self, event_bus):
        """Test multiple subscribers to same event."""
        received_1 = []
        received_2 = []

        def handler_1(event):
            received_1.append(event)

        def handler_2(event):
            received_2.append(event)

        event_bus.subscribe(EventType.HONEYPOT_ENGAGED, handler_1)
        event_bus.subscribe(EventType.HONEYPOT_ENGAGED, handler_2)

        test_event = Event(
            event_type=EventType.HONEYPOT_ENGAGED,
            conversation_id="test_456",
            payload={},
        )
        event_bus.emit(test_event)

        assert len(received_1) > 0
        assert len(received_2) > 0


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_malformed_request(self):
        """Test malformed request handling."""
        response = client.post("/detect-scam", json={"invalid": "data"})
        # Should handle gracefully (either 400 or process with defaults)
        assert response.status_code in [400, 422, 200]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
