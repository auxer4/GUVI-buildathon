"""
Risk Fusion Engine.

Combines detector scores using weighted fusion to produce final scam probability.
Configurable weights via YAML for experimentation and tuning.
"""

import yaml
from pathlib import Path
from typing import Dict, Tuple
import logging

from ..schemas.events import DetectorInput, DetectorBreakdown, ScamDetectionResult, RiskLevel

logger = logging.getLogger(__name__)


class RiskFusionEngine:
    """
    Fuses detector outputs into final scam probability and risk level.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize fusion engine with configuration.

        Args:
            config_path: Path to thresholds.yaml. If None, uses default weights.
        """
        self.config = self._load_config(config_path)
        self.detector_weights = self.config.get("detector_weights", {})
        self.risk_thresholds = self.config.get("risk_thresholds", {})

        logger.info(f"Risk Fusion Engine initialized with weights: {self.detector_weights}")

    def fuse(
        self,
        detector_input: DetectorInput,
        breakdown: DetectorBreakdown,
    ) -> ScamDetectionResult:
        """
        Fuse detector scores into final result.

        Args:
            detector_input: Original input for context
            breakdown: Normalized detector scores [0.0, 1.0]

        Returns:
            ScamDetectionResult with final score and risk level
        """
        try:
            # Weighted average of detector scores
            scam_probability_normalized = self._weighted_average(breakdown)

            # Convert to 0-100 scale
            scam_probability = scam_probability_normalized * 100

            # Determine risk level
            risk_level = self._classify_risk(scam_probability)

            # Determine if handoff is triggered
            handoff_triggered = risk_level == RiskLevel.CONFIRMED

            result = ScamDetectionResult(
                conversation_id=detector_input.conversation_id,
                scam_probability=scam_probability,
                risk_level=risk_level,
                breakdown=breakdown,
                handoff_triggered=handoff_triggered,
                metadata={
                    "sender_id": detector_input.sender_metadata.user_id,
                    "message_count": len(detector_input.messages),
                },
            )

            logger.info(
                f"Fused result for {detector_input.conversation_id}: "
                f"score={scam_probability:.1f}, risk={risk_level}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in risk fusion: {e}")
            # Return neutral result on error
            return ScamDetectionResult(
                conversation_id=detector_input.conversation_id,
                scam_probability=0.0,
                risk_level=RiskLevel.SAFE,
                breakdown=breakdown,
                handoff_triggered=False,
            )

    def _weighted_average(self, breakdown: DetectorBreakdown) -> float:
        """
        Calculate weighted average of detector scores.

        Args:
            breakdown: DetectorBreakdown with all scores [0.0, 1.0]

        Returns:
            Weighted average score [0.0, 1.0]
        """
        weighted_sum = 0.0
        weight_sum = 0.0

        # Map breakdown fields to weight keys
        score_map = {
            "linguistic": breakdown.linguistic_score,
            "behavioral": breakdown.behavioral_score,
            "link_infrastructure": breakdown.link_infrastructure_score,
            "identity_mismatch": breakdown.identity_mismatch_score,
            "historical": breakdown.historical_score,
        }

        for detector_name, score in score_map.items():
            weight = self.detector_weights.get(detector_name, 0.0)
            weighted_sum += score * weight
            weight_sum += weight

        # Normalize by sum of weights (in case not all weights sum to 1.0)
        if weight_sum > 0:
            return weighted_sum / weight_sum
        else:
            # Fallback: simple average if no weights defined
            return sum(score_map.values()) / len(score_map)

    def _classify_risk(self, scam_probability: float) -> RiskLevel:
        """
        Classify risk level based on scam probability.

        Args:
            scam_probability: Scam probability 0-100

        Returns:
            RiskLevel classification
        """
        thresholds = {
            RiskLevel.CONFIRMED: self.risk_thresholds.get("confirmed", 85),
            RiskLevel.HIGH: self.risk_thresholds.get("high", 70),
            RiskLevel.SUSPICIOUS: self.risk_thresholds.get("suspicious", 30),
            RiskLevel.SAFE: self.risk_thresholds.get("safe", 0),
        }

        if scam_probability >= thresholds[RiskLevel.CONFIRMED]:
            return RiskLevel.CONFIRMED
        elif scam_probability >= thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif scam_probability >= thresholds[RiskLevel.SUSPICIOUS]:
            return RiskLevel.SUSPICIOUS
        else:
            return RiskLevel.SAFE

    @staticmethod
    def _load_config(config_path: str = None) -> Dict:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to thresholds.yaml

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Default path relative to this file
            config_path = Path(__file__).parent.parent / "config" / "thresholds.yaml"

        try:
            if Path(config_path).exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    logger.debug(f"Loaded config from {config_path}")
                    return config or {}
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
