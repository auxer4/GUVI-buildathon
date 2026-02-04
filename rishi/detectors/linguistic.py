"""
Linguistic Manipulation Detector.

Detects:
- Urgency and time-pressure tactics
- Fear appeals and emotional manipulation
- Authority impersonation
- Reward baiting and unrealistic promises
"""

import re
from typing import Dict, List, Tuple
import logging

from ..schemas.events import DetectorInput

logger = logging.getLogger(__name__)


class LinguisticManipulationDetector:
    """
    Analyzes conversation content for linguistic markers of scam tactics.
    Output: normalized score [0.0, 1.0]
    """

    def __init__(self):
        """Initialize detector with pattern library."""
        self.urgency_patterns = [
            r"urgent|immediately|right now|asap|don't wait",
            r"limited time|act now|expires? (today|tonight|this week)",
            r"hurry|quickly|rush",
        ]

        self.fear_patterns = [
            r"account (locked|closed|compromised|suspended)",
            r"action required|verify|confirm identity|update payment",
            r"suspicious activity|unauthorized|fraud|hacked",
            r"click here|verify now|confirm immediately",
        ]

        self.authority_patterns = [
            r"(federal|irs|fbi|bank|microsoft|apple|google|amazon|paypal)",
            r"official|authorized|representative|agent",
            r"on behalf of|department of",
        ]

        self.reward_patterns = [
            r"congratulations|won|prize|claim|reward",
            r"free (money|cash|gift|payment)",
            r"unclaimed|inheritance|settlement",
            r"instant (approval|cash|reward)",
            r"$\d{4,}|millions? dollars",
        ]

        # TODO: Replace with LLM-based scoring when ML pipeline is available
        self.use_llm = False

    def analyze(self, detector_input: DetectorInput) -> float:
        """
        Analyze conversation for linguistic manipulation tactics.

        Args:
            detector_input: Standardized input with messages and metadata

        Returns:
            Normalized score [0.0, 1.0]
        """
        try:
            messages = detector_input.messages
            if not messages:
                return 0.0

            # Aggregate all message content
            full_text = " ".join([msg.content for msg in messages]).lower()

            # Calculate component scores
            urgency_score = self._calculate_urgency_score(full_text)
            fear_score = self._calculate_fear_score(full_text)
            authority_score = self._calculate_authority_score(full_text)
            reward_score = self._calculate_reward_score(full_text)

            # Weighted average
            final_score = (
                urgency_score * 0.35
                + fear_score * 0.30
                + authority_score * 0.20
                + reward_score * 0.15
            )

            logger.debug(
                f"Linguistic scores for {detector_input.conversation_id}: "
                f"urgency={urgency_score:.3f}, fear={fear_score:.3f}, "
                f"authority={authority_score:.3f}, reward={reward_score:.3f}"
            )

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"Error in linguistic analysis: {e}")
            return 0.0

    def _calculate_urgency_score(self, text: str) -> float:
        """Detect urgency and time-pressure tactics."""
        matches = sum(
            1 for pattern in self.urgency_patterns if re.search(pattern, text)
        )
        # Scale: each match adds ~0.2 to score, max 1.0
        return min(1.0, matches * 0.25)

    def _calculate_fear_score(self, text: str) -> float:
        """Detect fear appeals and social engineering."""
        matches = sum(1 for pattern in self.fear_patterns if re.search(pattern, text))
        return min(1.0, matches * 0.20)

    def _calculate_authority_score(self, text: str) -> float:
        """Detect impersonation of legitimate entities."""
        matches = sum(
            1 for pattern in self.authority_patterns if re.search(pattern, text)
        )
        return min(1.0, matches * 0.25)

    def _calculate_reward_score(self, text: str) -> float:
        """Detect unrealistic reward/prize baiting."""
        matches = sum(
            1 for pattern in self.reward_patterns if re.search(pattern, text)
        )
        return min(1.0, matches * 0.30)
