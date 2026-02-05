"""
Historical Pattern Detector.

Learns from confirmed scams via event_bus.
Tracks historical scam patterns and known bad actors.
"""

from typing import Dict, List, Optional, Set
import logging
from datetime import datetime
from collections import defaultdict

from ..schemas.events import DetectorInput

logger = logging.getLogger(__name__)


class HistoricalPatternDetector:
    """
    Analyzes conversation against historical scam patterns.
    Learns from SCAM_CONFIRMED events via event_bus.
    Output: normalized score [0.0, 1.0]
    """

    def __init__(self, event_bus=None):
        """
        Initialize detector.

        Args:
            event_bus: Optional reference to event_bus for learning
        """
        self.event_bus = event_bus
        self.historical_patterns: List[Dict] = []
        self.known_bad_actors: Set[str] = set()
        self.known_tactics: Dict[str, int] = defaultdict(int)  # tactic -> frequency
        self.known_keywords: Set[str] = set()
        
        if event_bus:
            self._subscribe_to_scam_events()
        
        logger.info("Historical detector initialized")

    def analyze(self, detector_input: DetectorInput) -> float:
        """
        Analyze conversation against historical patterns.

        Args:
            detector_input: Standardized input with messages and metadata

        Returns:
            Normalized score [0.0, 1.0]
        """
        try:
            # Check known bad actors
            bad_actor_score = self._check_known_bad_actors(detector_input)
            if bad_actor_score > 0:
                logger.info(
                    f"Known bad actor detected in {detector_input.conversation_id}: {bad_actor_score:.3f}"
                )
                return bad_actor_score

            # Check for known tactics
            tactic_score = self._check_known_tactics(detector_input)
            if tactic_score > 0:
                logger.debug(f"Known tactic detected: {tactic_score:.3f}")
                return tactic_score

            # Check for known keywords
            keyword_score = self._check_known_keywords(detector_input)
            if keyword_score > 0:
                logger.debug(f"Known scam keywords detected: {keyword_score:.3f}")
                return keyword_score

            # Check pattern similarity
            pattern_score = self._check_pattern_similarity(detector_input)
            if pattern_score > 0:
                logger.debug(f"Similar historical pattern detected: {pattern_score:.3f}")
                return pattern_score

            return 0.0

        except Exception as e:
            logger.error(f"Error in historical analysis: {e}")
            return 0.0

    def _check_known_bad_actors(self, detector_input: DetectorInput) -> float:
        """Check if conversation involves known bad actors."""
        sender_id = detector_input.sender_metadata.user_id
        if sender_id in self.known_bad_actors:
            return 0.95

        return 0.0

    def _check_known_tactics(self, detector_input: DetectorInput) -> float:
        """Check for patterns matching known attack tactics."""
        if not self.known_tactics:
            return 0.0

        messages = [m.text for m in detector_input.messages if hasattr(m, 'text')]
        full_text = " ".join(messages).lower()

        # Simple keyword matching for known tactics
        matched_tactics = []
        for tactic in self.known_tactics.keys():
            if tactic.lower() in full_text:
                matched_tactics.append(tactic)

        if matched_tactics:
            # Score based on number of tactics matched (max 0.8)
            return min(0.8, 0.3 * len(matched_tactics))

        return 0.0

    def _check_known_keywords(self, detector_input: DetectorInput) -> float:
        """Check for known scam keywords."""
        if not self.known_keywords:
            return 0.0

        messages = [m.text for m in detector_input.messages if hasattr(m, 'text')]
        full_text = " ".join(messages).lower()

        keyword_count = sum(1 for kw in self.known_keywords if kw.lower() in full_text)

        if keyword_count > 0:
            # Score based on keyword density (max 0.7)
            return min(0.7, 0.1 * keyword_count)

        return 0.0

    def _check_pattern_similarity(self, detector_input: DetectorInput) -> float:
        """Check similarity to historical scam patterns."""
        if not self.historical_patterns:
            return 0.0

        # Extract features from current conversation
        current_features = self._extract_pattern_features(detector_input)

        best_similarity = 0.0
        for pattern in self.historical_patterns:
            similarity = self._calculate_similarity(current_features, pattern.get('features', {}))
            if similarity > best_similarity:
                best_similarity = similarity

        return min(0.6, best_similarity)  # Cap at 0.6

    def _extract_pattern_features(self, detector_input: DetectorInput) -> Dict[str, any]:
        """Extract features for pattern matching."""
        messages = [m.text for m in detector_input.messages if hasattr(m, 'text')]
        full_text = " ".join(messages).lower()

        return {
            'message_count': len(messages),
            'total_length': len(full_text),
            'sender_id': detector_input.sender_metadata.user_id,
            'contains_urgency': any(w in full_text for w in ['urgent', 'asap', 'quick', 'now', 'immediately']),
            'contains_request': any(w in full_text for w in ['need', 'send', 'transfer', 'pay', 'click', 'verify']),
        }

    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two feature sets."""
        if not features2:
            return 0.0

        similarity = 0.0
        match_count = 0

        # Check boolean features
        for key in ['contains_urgency', 'contains_request']:
            if key in features1 and key in features2:
                if features1[key] == features2[key]:
                    similarity += 0.25
                match_count += 1

        # Check numeric similarity (message count, length)
        if 'message_count' in features1 and 'message_count' in features2:
            msg_ratio = min(features1['message_count'], features2['message_count']) / max(
                features1['message_count'], features2['message_count']
            )
            similarity += 0.25 * msg_ratio
            match_count += 1

        if match_count > 0:
            return similarity / match_count

        return 0.0

    def register_scam_pattern(self, pattern: Dict) -> None:
        """
        Register a confirmed scam pattern for future reference.
        Called when SCAM_CONFIRMED event is received.

        Args:
            pattern: Dictionary containing scam signature and metadata
        """
        # Extract and store pattern features
        if 'features' not in pattern:
            pattern['features'] = {}
        pattern['timestamp'] = datetime.utcnow().isoformat()

        self.historical_patterns.append(pattern)
        logger.info(f"Registered historical pattern: {pattern.get('id', 'unknown')}")

        # Extract tactics and keywords for faster lookup
        if 'tactics' in pattern:
            for tactic in pattern['tactics']:
                self.known_tactics[tactic] += 1
        
        if 'keywords' in pattern:
            self.known_keywords.update(pattern['keywords'])

    def register_bad_actor(self, actor_id: str) -> None:
        """
        Mark a sender as a known bad actor.

        Args:
            actor_id: User/sender ID to blacklist
        """
        if actor_id:
            self.known_bad_actors.add(actor_id)
            logger.warning(f"Registered bad actor: {actor_id}")

    def _subscribe_to_scam_events(self) -> None:
        """Subscribe to SCAM_CONFIRMED events from event_bus."""
        if not self.event_bus:
            return

        def on_scam_confirmed(event):
            """Handle SCAM_CONFIRMED event."""
            try:
                payload = event.payload if hasattr(event, 'payload') else event.get('payload', {})
                
                # Register the bad actor
                sender_id = payload.get('sender_id') or payload.get('user_id')
                if sender_id:
                    self.register_bad_actor(sender_id)

                # Register the scam pattern
                pattern = {
                    'id': payload.get('conversation_id', 'unknown'),
                    'sender_id': sender_id,
                    'tactics': payload.get('detection_result', {}).get('tactics', []),
                    'keywords': payload.get('keywords', []),
                    'features': self._extract_pattern_features_from_event(payload),
                }
                self.register_scam_pattern(pattern)

                logger.info(f"Learned from SCAM_CONFIRMED event: {pattern['id']}")
            except Exception as e:
                logger.error(f"Error processing SCAM_CONFIRMED event: {e}")

        from ..schemas.events import EventType

        self.event_bus.subscribe(EventType.SCAM_CONFIRMED, on_scam_confirmed)
        logger.info("Subscribed to SCAM_CONFIRMED events")

    def _extract_pattern_features_from_event(self, payload: Dict) -> Dict:
        """Extract pattern features from event payload."""
        return {
            'risk_score': payload.get('detection_result', {}).get('final_score', 0),
            'detector_types': list(payload.get('detection_result', {}).get('detector_results', {}).keys()),
            'timestamp': payload.get('timestamp', datetime.utcnow().isoformat()),
        }

    def get_statistics(self) -> Dict:
        """Return detector statistics."""
        return {
            'total_patterns': len(self.historical_patterns),
            'bad_actors': len(self.known_bad_actors),
            'known_tactics': dict(self.known_tactics),
            'known_keywords_count': len(self.known_keywords),
        }
