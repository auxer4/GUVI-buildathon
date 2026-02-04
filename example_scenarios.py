"""
Example usage and test scenarios for the Scam Intelligence Engine.

This demonstrates how to use the scam detection pipeline with real-world scenarios.
Run with: python -m pytest example_scenarios.py
"""

from datetime import datetime, timedelta
from typing import List

from rishi.schemas.events import (
    ScamDetectionInput,
    ConversationMessage,
    SenderMetadata,
    RiskLevel,
)
from rishi.detectors.linguistic import LinguisticManipulationDetector
from rishi.detectors.behavioral import BehavioralPatternDetector
from rishi.detectors.link_intel import LinkIntelligenceDetector
from rishi.detectors.identity_mismatch import IdentityMismatchDetector
from rishi.detectors.historical import HistoricalPatternDetector
from rishi.scoring.risk_fusion import RiskFusionEngine


class ScamScenarios:
    """Real-world scam detection scenarios."""

    @staticmethod
    def scenario_1_urgent_account_compromise() -> ScamDetectionInput:
        """
        Scenario 1: Classic phishing - urgent account compromise
        Expected Risk: CONFIRMED (high score)
        """
        messages = [
            ConversationMessage(
                message_id="msg1",
                sender="attacker",
                content="URGENT! Your Apple ID account has been compromised. "
                "Click here immediately to verify your identity.",
                timestamp=datetime.utcnow(),
            ),
            ConversationMessage(
                message_id="msg2",
                sender="attacker",
                content="DO NOT IGNORE THIS MESSAGE. Your account will be permanently suspended. "
                "Click: http://apple-verify.tk/login.php",
                timestamp=datetime.utcnow() + timedelta(seconds=30),
            ),
        ]

        return ScamDetectionInput(
            conversation_id="scenario_1_phishing",
            messages=messages,
            sender_metadata=SenderMetadata(
                user_id="attacker_001",
                account_age_days=2,
                verification_status="unverified",
            ),
        )

    @staticmethod
    def scenario_2_romance_scam() -> ScamDetectionInput:
        """
        Scenario 2: Romance scam - reward baiting
        Expected Risk: HIGH to CONFIRMED
        """
        messages = [
            ConversationMessage(
                message_id="msg1",
                sender="attacker",
                content="Hi there! I'm so glad we met. I have a special offer for you - "
                "a free cryptocurrency investment opportunity worth $50,000!",
                timestamp=datetime.utcnow(),
            ),
            ConversationMessage(
                message_id="msg2",
                sender="attacker",
                content="Congratulations! You've been selected as the winner of our exclusive settlement. "
                "Please send $500 to verify your identity and claim your prize.",
                timestamp=datetime.utcnow() + timedelta(minutes=5),
            ),
        ]

        return ScamDetectionInput(
            conversation_id="scenario_2_romance",
            messages=messages,
            sender_metadata=SenderMetadata(
                user_id="attacker_002",
                account_age_days=1,
            ),
        )

    @staticmethod
    def scenario_3_tech_support_scam() -> ScamDetectionInput:
        """
        Scenario 3: Tech support scam - authority impersonation with behavior rigidity
        Expected Risk: HIGH
        """
        base_time = datetime.utcnow()
        messages = [
            ConversationMessage(
                message_id="msg1",
                sender="attacker",
                content="Microsoft Support here. Your computer has been infected with malware. "
                "You must immediately download our fix from: http://microsft-support.ga/download",
                timestamp=base_time,
            ),
            ConversationMessage(
                message_id="msg2",
                sender="attacker",
                content="Microsoft Support here. Your computer has been infected with malware. "
                "You must immediately download our fix from: http://microsft-support.ga/download",
                timestamp=base_time + timedelta(seconds=10),  # Repetition
            ),
            ConversationMessage(
                message_id="msg3",
                sender="user",
                content="Wait, I have questions about this. Is this legitimate?",
                timestamp=base_time + timedelta(seconds=20),
            ),
            ConversationMessage(
                message_id="msg4",
                sender="attacker",
                content="Download the file NOW. Click here immediately: http://microsft-support.ga/download",
                timestamp=base_time + timedelta(seconds=30),  # Ignores user question
            ),
        ]

        return ScamDetectionInput(
            conversation_id="scenario_3_tech_support",
            messages=messages,
            sender_metadata=SenderMetadata(
                user_id="attacker_003",
                account_age_days=7,
                verification_status="unverified",
            ),
        )

    @staticmethod
    def scenario_4_legitimate_message() -> ScamDetectionInput:
        """
        Scenario 4: Legitimate message - should be SAFE
        Expected Risk: SAFE (low score)
        """
        messages = [
            ConversationMessage(
                message_id="msg1",
                sender="support@company.com",
                content="Hi there! Thank you for contacting our support team. "
                "How can we help you today?",
                timestamp=datetime.utcnow(),
            ),
            ConversationMessage(
                message_id="msg2",
                sender="user",
                content="Hi! I have a question about my account.",
                timestamp=datetime.utcnow() + timedelta(hours=1),
            ),
            ConversationMessage(
                message_id="msg3",
                sender="support@company.com",
                content="Of course! Please let me know what you need. "
                "I'll be happy to assist.",
                timestamp=datetime.utcnow() + timedelta(hours=1, minutes=5),
            ),
        ]

        return ScamDetectionInput(
            conversation_id="scenario_4_legitimate",
            messages=messages,
            sender_metadata=SenderMetadata(
                user_id="verified_support_123",
                account_age_days=365,
                verification_status="verified",
            ),
        )

    @staticmethod
    def scenario_5_mixed_signals() -> ScamDetectionInput:
        """
        Scenario 5: Mixed signals - some indicators but not conclusive
        Expected Risk: SUSPICIOUS
        """
        messages = [
            ConversationMessage(
                message_id="msg1",
                sender="attacker",
                content="Hello! We noticed unusual activity on your bank account. "
                "Please verify your details at our secure portal.",
                timestamp=datetime.utcnow(),
            ),
            ConversationMessage(
                message_id="msg2",
                sender="user",
                content="I'm concerned about this. Can you provide more details?",
                timestamp=datetime.utcnow() + timedelta(minutes=2),
            ),
            ConversationMessage(
                message_id="msg3",
                sender="attacker",
                content="Yes, we take your security seriously. Click here to verify: "
                "https://bank-security-check.com/verify",
                timestamp=datetime.utcnow() + timedelta(minutes=5),
            ),
        ]

        return ScamDetectionInput(
            conversation_id="scenario_5_mixed",
            messages=messages,
            sender_metadata=SenderMetadata(
                user_id="attacker_005",
                account_age_days=15,
            ),
        )


def run_scenario(scenario: ScamDetectionInput, scenario_name: str) -> None:
    """Run a single scenario and print results."""
    print("\n" + "=" * 70)
    print(f"📋 {scenario_name}")
    print("=" * 70)

    # Initialize detectors
    linguistic = LinguisticManipulationDetector()
    behavioral = BehavioralPatternDetector()
    link_intel = LinkIntelligenceDetector()
    identity = IdentityMismatchDetector()
    historical = HistoricalPatternDetector()
    fusion = RiskFusionEngine()

    # Create detector input
    detector_input = scenario

    # Run all detectors
    from rishi.schemas.events import DetectorBreakdown

    print(f"\n📨 Input: {len(detector_input.messages)} messages")
    print(f"👤 Sender: {detector_input.sender_metadata.user_id}")
    print(f"   Account Age: {detector_input.sender_metadata.account_age_days} days")
    print(f"   Verification: {detector_input.sender_metadata.verification_status}")

    # Run detectors
    print("\n🔍 Running detectors...")
    linguistic_score = linguistic.analyze(detector_input)
    behavioral_score = behavioral.analyze(detector_input)
    link_score = link_intel.analyze(detector_input)
    identity_score = identity.analyze(detector_input)
    historical_score = historical.analyze(detector_input)

    print(f"  • Linguistic:     {linguistic_score:.2f}")
    print(f"  • Behavioral:     {behavioral_score:.2f}")
    print(f"  • Link/Infra:     {link_score:.2f}")
    print(f"  • Identity:       {identity_score:.2f}")
    print(f"  • Historical:     {historical_score:.2f}")

    # Fuse scores
    breakdown = DetectorBreakdown(
        linguistic_score=linguistic_score,
        behavioral_score=behavioral_score,
        link_infrastructure_score=link_score,
        identity_mismatch_score=identity_score,
        historical_score=historical_score,
    )

    result = fusion.fuse(detector_input, breakdown)

    # Print results
    print("\n📊 Final Result:")
    print(f"  • Scam Probability: {result.scam_probability:.1f}%")
    print(f"  • Risk Level: {result.risk_level.value.upper()}")
    print(f"  • Handoff Triggered: {result.handoff_triggered}")

    # Color-coded risk level
    emoji = {
        "safe": "✅",
        "suspicious": "⚠️",
        "high": "🚨",
        "confirmed": "🛑",
    }
    print(
        f"\n{emoji.get(result.risk_level.value, '❓')} Risk: {result.risk_level.value.upper()}"
    )


def main():
    """Run all scenarios."""
    print("\n" + "=" * 70)
    print("🎯 SCAM INTELLIGENCE ENGINE - EXAMPLE SCENARIOS")
    print("=" * 70)

    scenarios = [
        (ScamScenarios.scenario_1_urgent_account_compromise(), "Scenario 1: Phishing - Account Compromise"),
        (ScamScenarios.scenario_2_romance_scam(), "Scenario 2: Romance/Advance Fee Scam"),
        (ScamScenarios.scenario_3_tech_support_scam(), "Scenario 3: Tech Support Scam"),
        (ScamScenarios.scenario_4_legitimate_message(), "Scenario 4: Legitimate Message"),
        (ScamScenarios.scenario_5_mixed_signals(), "Scenario 5: Mixed Signals"),
    ]

    for scenario, name in scenarios:
        run_scenario(scenario, name)

    print("\n" + "=" * 70)
    print("✅ All scenarios completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
