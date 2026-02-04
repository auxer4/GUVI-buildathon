"""
Identity Mismatch Detector.

Detects inconsistencies between claimed identity and evidence:
- Claimed vs. actual sender credentials
- Brand claims vs. domain/contact info
- Inconsistent use of names/titles
"""

import re
from typing import Dict, List, Tuple
import logging

from ..schemas.events import DetectorInput

logger = logging.getLogger(__name__)


class IdentityMismatchDetector:
    """
    Detects identity inconsistencies and brand impersonation.
    Output: normalized score [0.0, 1.0]
    """

    def __init__(self):
        """Initialize detector with brand signatures."""
        # Known brand patterns and their expected characteristics
        self.brand_patterns = {
            "apple": {
                "domains": ["apple.com", "appleid.apple.com"],
                "names": ["apple", "apple support", "apple store"],
                "email_pattern": r"@apple\.com$",
            },
            "microsoft": {
                "domains": ["microsoft.com", "outlook.microsoft.com"],
                "names": ["microsoft", "microsoft support", "windows"],
                "email_pattern": r"@microsoft\.com$",
            },
            "amazon": {
                "domains": ["amazon.com", "aws.amazon.com"],
                "names": ["amazon", "amazon support", "aws"],
                "email_pattern": r"@amazon\.com$",
            },
            "paypal": {
                "domains": ["paypal.com"],
                "names": ["paypal", "paypal support"],
                "email_pattern": r"@paypal\.com$",
            },
            "google": {
                "domains": ["google.com", "gmail.com"],
                "names": ["google", "google support"],
                "email_pattern": r"@google\.com$",
            },
        }

    def analyze(self, detector_input: DetectorInput) -> float:
        """
        Analyze for identity mismatches and inconsistencies.

        Args:
            detector_input: Standardized input with messages and metadata

        Returns:
            Normalized score [0.0, 1.0]
        """
        try:
            messages = detector_input.messages
            sender_metadata = detector_input.sender_metadata
            if not messages:
                return 0.0

            # Calculate component scores
            brand_impersonation_score = self._check_brand_impersonation(messages)
            credential_anomaly_score = self._check_credential_anomalies(
                messages, sender_metadata
            )
            claim_consistency_score = self._check_claim_consistency(messages)

            # Weighted average
            final_score = (
                brand_impersonation_score * 0.35
                + credential_anomaly_score * 0.35
                + claim_consistency_score * 0.30
            )

            logger.debug(
                f"Identity scores for {detector_input.conversation_id}: "
                f"brand_impersonation={brand_impersonation_score:.3f}, "
                f"credential_anomaly={credential_anomaly_score:.3f}, "
                f"claim_consistency={claim_consistency_score:.3f}"
            )

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"Error in identity analysis: {e}")
            return 0.0

    def _check_brand_impersonation(self, messages: List) -> float:
        """
        Detect impersonation of known brands.
        Returns score [0.0, 1.0].
        """
        full_text = " ".join([msg.content for msg in messages]).lower()

        impersonation_score = 0.0

        for brand, patterns in self.brand_patterns.items():
            # Check if brand is mentioned
            for name in patterns["names"]:
                if name in full_text:
                    # Check if domain is inconsistent with brand mention
                    domain_found = False
                    for legit_domain in patterns["domains"]:
                        if legit_domain.lower() in full_text:
                            domain_found = True
                            break

                    # If brand mentioned but no legitimate domain, likely impersonation
                    if not domain_found:
                        impersonation_score = max(impersonation_score, 0.75)
                    break

        return impersonation_score

    def _check_credential_anomalies(self, messages: List, sender_metadata) -> float:
        """
        Detect anomalies in sender credentials.
        E.g., claims to be from established company but account is new.
        """
        score = 0.0

        full_text = " ".join([msg.content for msg in messages]).lower()

        # Check for company claims with new account
        company_keywords = [
            "bank",
            "government",
            "federal",
            "official",
            "authorized",
            "representative",
        ]

        has_company_claim = any(keyword in full_text for keyword in company_keywords)

        if has_company_claim:
            # If account is new, this is suspicious
            if sender_metadata.account_age_days is not None:
                if sender_metadata.account_age_days < 30:
                    score += 0.7

            # If unverified, suspicious
            if sender_metadata.verification_status == "unverified":
                score += 0.5

        # Check for credential inconsistencies in message signatures
        signatures = self._extract_signatures(messages)
        if len(set(signatures)) > 1:
            # Multiple different signatures = inconsistent credentials
            score += 0.4

        return min(1.0, score)

    def _check_claim_consistency(self, messages: List) -> float:
        """
        Check consistency of claims across messages.
        Scammers often contradict themselves.
        """
        if len(messages) < 2:
            return 0.0

        # Extract claims from each message
        claims = []
        for msg in messages:
            extracted = self._extract_claims(msg.content)
            claims.extend(extracted)

        if not claims:
            return 0.0

        # Check for contradictions
        contradiction_count = 0
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                if self._are_contradictory(claims[i], claims[j]):
                    contradiction_count += 1

        # Normalize
        max_comparisons = len(claims) * (len(claims) - 1) / 2
        if max_comparisons == 0:
            return 0.0

        return min(1.0, contradiction_count / max_comparisons)

    @staticmethod
    def _extract_signatures(messages: List) -> List[str]:
        """Extract sender signatures/names from messages."""
        signatures = []
        for msg in messages:
            # Look for common signature patterns
            lines = msg.content.split("\n")
            if lines:
                # Last line often contains signature
                last_line = lines[-1].strip()
                if len(last_line) < 50 and len(last_line) > 2:
                    signatures.append(last_line)
        return signatures

    @staticmethod
    def _extract_claims(text: str) -> List[str]:
        """Extract claims/assertions from message text."""
        claims = []

        # Look for "I am" statements
        i_am_pattern = r"i\s+(am|\'m)\s+([a-zA-Z\s]+?)(?:\.|,|;|\n|$)"
        matches = re.findall(i_am_pattern, text, re.IGNORECASE)
        claims.extend([m[1] for m in matches])

        # Look for "this is" statements
        this_is_pattern = r"this\s+is\s+([a-zA-Z\s]+?)(?:\.|,|;|\n|$)"
        matches = re.findall(this_is_pattern, text, re.IGNORECASE)
        claims.extend([m for m in matches])

        return claims

    @staticmethod
    def _are_contradictory(claim1: str, claim2: str) -> bool:
        """
        Check if two claims are contradictory.
        Simple heuristic: if they both start with same person/entity
        but have different assertions.
        """
        # This is a placeholder for more sophisticated contradiction detection
        # In production, would use NLP/semantic similarity
        if not claim1 or not claim2:
            return False

        # Simple check: if 80%+ similar, they should be the same
        # If they diverge, might be contradictory
        similarity = IdentityMismatchDetector._simple_similarity(claim1, claim2)
        return 0.3 < similarity < 0.8

    @staticmethod
    def _simple_similarity(s1: str, s2: str) -> float:
        """Simple token overlap similarity."""
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0
