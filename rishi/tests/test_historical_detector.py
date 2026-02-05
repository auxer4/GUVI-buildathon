"""
Unit tests for historical detector module.
"""

import pytest
from rishi.detectors.historical import HistoricalPatternDetector
from rishi.schemas.events import DetectorInput, SenderMetadata, Message
from shared.event_bus import EventBus, Event, EventType


@pytest.fixture
def detector():
    """Create a detector instance."""
    return HistoricalPatternDetector(event_bus=None)


@pytest.fixture
def mock_input():
    """Create mock detector input."""
    messages = [
        Message(sender="scammer", text="Hello, can you send me some money?", timestamp="2025-02-05T10:00:00"),
        Message(sender="victim", text="Who are you?", timestamp="2025-02-05T10:01:00"),
    ]
    return DetectorInput(
        conversation_id="conv_123",
        messages=messages,
        sender_metadata=SenderMetadata(
            user_id="user_456",
            phone="+91-XXXXXXXXXX",
            email="unknown@email.com",
            platform="whatsapp",
        ),
    )


def test_detector_initialization(detector):
    """Test detector initialization."""
    assert detector is not None
    assert len(detector.historical_patterns) == 0
    assert len(detector.known_bad_actors) == 0


def test_analyze_neutral_conversation(detector, mock_input):
    """Test analyzing a neutral conversation."""
    score = detector.analyze(mock_input)
    assert 0 <= score <= 1.0
    assert score == 0.0  # No bad actors or patterns


def test_register_bad_actor(detector):
    """Test registering a bad actor."""
    actor_id = "bad_guy_123"
    detector.register_bad_actor(actor_id)

    assert actor_id in detector.known_bad_actors
    assert len(detector.known_bad_actors) == 1


def test_register_scam_pattern(detector):
    """Test registering a scam pattern."""
    pattern = {
        "id": "pattern_1",
        "sender_id": "scammer_001",
        "tactics": ["phishing", "social_engineering"],
        "keywords": ["urgent", "verify", "click"],
    }
    detector.register_scam_pattern(pattern)

    assert len(detector.historical_patterns) == 1
    assert "phishing" in detector.known_tactics
    assert "urgent" in detector.known_keywords


def test_check_known_bad_actors(detector, mock_input):
    """Test detection of known bad actors."""
    # Register bad actor
    detector.register_bad_actor("user_456")

    # Analyze conversation with bad actor
    score = detector.analyze(mock_input)
    assert score > 0.9  # High confidence


def test_get_statistics(detector):
    """Test getting detector statistics."""
    detector.register_bad_actor("actor_1")
    detector.register_scam_pattern({
        "id": "p1",
        "tactics": ["phishing"],
        "keywords": ["click", "verify"],
    })

    stats = detector.get_statistics()
    assert stats["bad_actors"] == 1
    assert stats["total_patterns"] == 1
    assert "phishing" in stats["known_tactics"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
