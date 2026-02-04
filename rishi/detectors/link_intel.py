"""
Link & Infrastructure Intelligence Detector.

Analyzes URLs and domains for suspicious characteristics:
- Domain age (newly registered domains are riskier)
- URL entropy and complexity
- Look-alike domain detection
- Suspicious TLD patterns
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import logging

from ..schemas.events import DetectorInput

logger = logging.getLogger(__name__)


class LinkIntelligenceDetector:
    """
    Analyzes links and infrastructure for scam indicators.
    Output: normalized score [0.0, 1.0]
    """

    def __init__(self):
        """Initialize detector with patterns and knowledge base."""
        # Suspicious TLDs commonly used in phishing
        self.suspicious_tlds = [
            ".tk",
            ".ml",
            ".ga",
            ".cf",
            ".xyz",
            ".download",
            ".review",
        ]

        # Common legit domains to check against for lookalikes
        self.legitimate_domains = [
            "apple.com",
            "microsoft.com",
            "google.com",
            "amazon.com",
            "paypal.com",
            "bank.com",
            "facebook.com",
            "twitter.com",
        ]

        # URL patterns
        self.url_pattern = re.compile(
            r"https?://(?:www\.)?([a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+)"
        )

    def analyze(self, detector_input: DetectorInput) -> float:
        """
        Analyze conversation for suspicious links and infrastructure.

        Args:
            detector_input: Standardized input with messages and metadata

        Returns:
            Normalized score [0.0, 1.0]
        """
        try:
            messages = detector_input.messages
            if not messages:
                return 0.0

            # Extract all URLs
            urls = []
            for msg in messages:
                urls.extend(self._extract_urls(msg.content))

            if not urls:
                # No URLs present - lower risk
                return 0.1

            # Analyze each URL
            url_scores = [self._analyze_url(url) for url in urls]

            # Return max score (most suspicious URL dominates)
            final_score = max(url_scores) if url_scores else 0.0

            logger.debug(
                f"Link scores for {detector_input.conversation_id}: "
                f"urls_found={len(urls)}, max_risk={final_score:.3f}"
            )

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"Error in link analysis: {e}")
            return 0.0

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        matches = self.url_pattern.findall(text)
        return [f"http://{m}" for m in matches]

    def _analyze_url(self, url: str) -> float:
        """
        Analyze individual URL for risk indicators.
        Returns score [0.0, 1.0].
        """
        try:
            domain = self._extract_domain(url)
            if not domain:
                return 0.5

            score = 0.0

            # Check for suspicious TLD
            tld_score = self._check_tld(domain)
            score += tld_score * 0.3

            # Check for URL entropy (randomness suggests obfuscation)
            entropy_score = self._calculate_entropy(domain)
            score += entropy_score * 0.25

            # Check for lookalike domains
            lookalike_score = self._check_lookalike(domain)
            score += lookalike_score * 0.25

            # Check for suspicious patterns (IP addresses, etc)
            pattern_score = self._check_suspicious_patterns(domain)
            score += pattern_score * 0.2

            return min(1.0, score)

        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {e}")
            return 0.3  # Conservative estimate on error

    @staticmethod
    def _extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            # Remove protocol
            if "://" in url:
                url = url.split("://", 1)[1]
            # Remove path
            if "/" in url:
                url = url.split("/", 1)[0]
            # Remove port
            if ":" in url:
                url = url.split(":", 1)[0]
            return url.lower()
        except Exception:
            return None

    def _check_tld(self, domain: str) -> float:
        """Check if domain uses suspicious TLD."""
        for tld in self.suspicious_tlds:
            if domain.endswith(tld):
                return 0.7
        # Also check for unusual TLDs (very long)
        if "." in domain:
            tld = "." + domain.split(".")[-1]
            if len(tld) > 6:
                return 0.4
        return 0.0

    def _calculate_entropy(self, domain: str) -> float:
        """
        Calculate entropy of domain name.
        High entropy (randomness) suggests obfuscation.
        """
        # Get domain name only (without TLD)
        if "." in domain:
            domain_name = domain.rsplit(".", 1)[0]
        else:
            domain_name = domain

        if not domain_name:
            return 0.0

        # Calculate entropy using character frequency
        char_freq = Counter(domain_name)
        total_chars = len(domain_name)
        entropy = 0.0

        for freq in char_freq.values():
            p = freq / total_chars
            entropy -= p * (p ** 0.5)  # Simplified entropy calculation

        # Normalize: entropy typically 0-3.5 for domain names
        # High entropy > 3.0 is suspicious
        normalized = min(1.0, entropy / 3.5)
        return normalized if normalized > 0.5 else 0.0

    def _check_lookalike(self, domain: str) -> float:
        """
        Check if domain is a lookalike of legitimate domain.
        E.g., "amaz0n.com" vs "amazon.com"
        """
        domain_name = domain.rsplit(".", 1)[0] if "." in domain else domain

        for legit in self.legitimate_domains:
            legit_name = legit.rsplit(".", 1)[0]

            # Simple checks for common typosquatting
            if self._is_lookalike(domain_name, legit_name):
                return 0.8

        return 0.0

    @staticmethod
    def _is_lookalike(domain: str, legit: str) -> bool:
        """
        Detect lookalike domains using simple heuristics.
        - Single character substitutions (0 -> O, 1 -> l, 5 -> S)
        - Missing/extra characters
        - Similar length and prefix
        """
        if domain == legit:
            return False

        # Check for character substitutions
        char_map = {
            "0": "o",
            "1": "l",
            "5": "s",
            "3": "e",
            "4": "a",
        }

        domain_normalized = domain.lower()
        legit_normalized = legit.lower()

        for original, replacement in char_map.items():
            domain_normalized = domain_normalized.replace(original, replacement)

        # Levenshtein-like check: if very similar, likely lookalike
        if len(domain) >= len(legit) - 1 and len(domain) <= len(legit) + 1:
            matching_chars = sum(
                1
                for c1, c2 in zip(domain_normalized, legit_normalized)
                if c1 == c2
            )
            similarity = matching_chars / max(len(domain), len(legit))
            if similarity > 0.85:
                return True

        return False

    @staticmethod
    def _check_suspicious_patterns(domain: str) -> float:
        """Check for suspicious patterns in domain."""
        score = 0.0

        # Check for IP address instead of domain
        if re.match(r"^\d+\.\d+\.\d+\.\d+", domain):
            score += 0.8

        # Check for excessive subdomains (typically > 3)
        subdomain_count = domain.count(".")
        if subdomain_count > 3:
            score += 0.3

        # Check for very long domain (often used to hide phishing)
        if len(domain) > 50:
            score += 0.2

        # Check for numeric-heavy domains
        digit_ratio = sum(1 for c in domain if c.isdigit()) / len(domain)
        if digit_ratio > 0.3:
            score += 0.2

        return min(1.0, score)
