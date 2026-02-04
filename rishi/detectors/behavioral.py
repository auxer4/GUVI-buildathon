"""
Behavioral Pattern Detector.

Analyzes conversation patterns for suspicious behaviors:
- Unusually high message frequency
- Repetitive instructions/patterns
- Script rigidity (ignoring user questions)
- Pressure tactics
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

from ..schemas.events import DetectorInput, ConversationMessage

logger = logging.getLogger(__name__)


class BehavioralPatternDetector:
    """
    Analyzes conversation dynamics and message patterns.
    Output: normalized score [0.0, 1.0]
    """

    def __init__(
        self,
        frequency_window_minutes: int = 10,
        high_frequency_threshold: int = 5,
        repetition_threshold: float = 0.6,
        rigidity_threshold: float = 0.7,
    ):
        """
        Initialize detector with behavioral thresholds.

        Args:
            frequency_window_minutes: Time window for frequency analysis
            high_frequency_threshold: Messages in window considered "high"
            repetition_threshold: Similarity score threshold for repetition
            rigidity_threshold: Threshold for detecting scripted behavior
        """
        self.frequency_window_minutes = frequency_window_minutes
        self.high_frequency_threshold = high_frequency_threshold
        self.repetition_threshold = repetition_threshold
        self.rigidity_threshold = rigidity_threshold

    def analyze(self, detector_input: DetectorInput) -> float:
        """
        Analyze conversation for suspicious behavioral patterns.

        Args:
            detector_input: Standardized input with messages and metadata

        Returns:
            Normalized score [0.0, 1.0]
        """
        try:
            messages = detector_input.messages
            if not messages:
                return 0.0

            # Calculate component scores
            frequency_score = self._analyze_message_frequency(messages)
            repetition_score = self._analyze_instruction_repetition(messages)
            rigidity_score = self._analyze_script_rigidity(messages)
            pressure_score = self._analyze_pressure_tactics(messages)

            # Weighted average
            final_score = (
                frequency_score * 0.30
                + repetition_score * 0.25
                + rigidity_score * 0.25
                + pressure_score * 0.20
            )

            logger.debug(
                f"Behavioral scores for {detector_input.conversation_id}: "
                f"frequency={frequency_score:.3f}, repetition={repetition_score:.3f}, "
                f"rigidity={rigidity_score:.3f}, pressure={pressure_score:.3f}"
            )

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return 0.0

    def _analyze_message_frequency(self, messages: List[ConversationMessage]) -> float:
        """
        Detect unnaturally high message frequency.
        Scammers often spam repeated messages.
        """
        if len(messages) < 2:
            return 0.0

        # Group messages by sender
        sender_messages = {}
        for msg in messages:
            if msg.sender not in sender_messages:
                sender_messages[msg.sender] = []
            sender_messages[msg.sender].append(msg)

        # Check frequency for each sender
        frequency_scores = []
        for sender, sender_msgs in sender_messages.items():
            if len(sender_msgs) < 2:
                continue

            # Calculate intervals between consecutive messages
            intervals = []
            for i in range(1, len(sender_msgs)):
                diff = (
                    sender_msgs[i].timestamp - sender_msgs[i - 1].timestamp
                ).total_seconds() / 60  # minutes
                intervals.append(diff)

            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                # Score: if avg interval < 2 min, likely high frequency
                if avg_interval < 2:
                    frequency_scores.append(0.8)
                elif avg_interval < 5:
                    frequency_scores.append(0.5)
                else:
                    frequency_scores.append(0.1)

        return max(frequency_scores) if frequency_scores else 0.0

    def _analyze_instruction_repetition(
        self, messages: List[ConversationMessage]
    ) -> float:
        """
        Detect repetitive instruction patterns.
        Scammers often repeat the same steps/phrases.
        """
        if len(messages) < 3:
            return 0.0

        contents = [msg.content.lower() for msg in messages]

        # Simple similarity: check for exact or near-duplicate messages
        duplicate_count = 0
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                similarity = self._string_similarity(contents[i], contents[j])
                if similarity > self.repetition_threshold:
                    duplicate_count += 1

        # Normalize: more repetitions = higher score
        # Max possible pairs: n*(n-1)/2
        max_pairs = len(contents) * (len(contents) - 1) / 2
        if max_pairs == 0:
            return 0.0

        repetition_ratio = duplicate_count / max_pairs
        return min(1.0, repetition_ratio)

    def _analyze_script_rigidity(self, messages: List[ConversationMessage]) -> float:
        """
        Detect scripted behavior: sender ignores user questions,
        continues with predetermined script.
        """
        if len(messages) < 3:
            return 0.0

        # Heuristic: look for question marks from one sender followed by
        # unrelated responses from another
        rigidity_count = 0
        response_pairs = 0

        for i in range(len(messages) - 1):
            current_msg = messages[i]
            next_msg = messages[i + 1]

            # Different senders
            if current_msg.sender != next_msg.sender:
                response_pairs += 1
                # If current is a question but next doesn't address it
                if "?" in current_msg.content:
                    similarity = self._string_similarity(
                        current_msg.content, next_msg.content
                    )
                    if similarity < 0.3:  # Low similarity = didn't address question
                        rigidity_count += 1

        if response_pairs == 0:
            return 0.0

        rigidity_ratio = rigidity_count / response_pairs
        return min(1.0, rigidity_ratio)

    def _analyze_pressure_tactics(self, messages: List[ConversationMessage]) -> float:
        """
        Detect pressure tactics: demanding immediate action, threats, etc.
        """
        pressure_keywords = [
            "immediately",
            "urgent",
            "now",
            "must",
            "required",
            "don't delay",
            "act fast",
        ]

        pressure_count = 0
        for msg in messages:
            content_lower = msg.content.lower()
            for keyword in pressure_keywords:
                if keyword in content_lower:
                    pressure_count += 1
                    break

        # Normalize by message count
        pressure_ratio = pressure_count / len(messages) if messages else 0
        return min(1.0, pressure_ratio)

    @staticmethod
    def _string_similarity(s1: str, s2: str) -> float:
        """
        Simple similarity metric using token overlap (Jaccard).
        Returns score [0.0, 1.0].
        """
        tokens1 = set(s1.split())
        tokens2 = set(s2.split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0
