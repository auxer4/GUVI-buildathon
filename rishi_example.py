"""
Comprehensive example showing how to use the Rishi scam detection module.

This demonstrates:
1. Creating detection inputs with sample conversations
2. Running all detectors
3. Fusing scores for final risk assessment
4. Handling handoff to honeypot agent
"""

from datetime import datetime, timedelta
from rishi.schemas.events import (
    ScamDetectionInput,
    ConversationMessage,
    SenderMetadata,
    DetectorInput,
)
from rishi.detectors.linguistic import LinguisticManipulationDetector
from rishi.detectors.behavioral import BehavioralPatternDetector
from rishi.detectors.link_intel import LinkIntelligenceDetector
from rishi.detectors.identity_mismatch import IdentityMismatchDetector
from rishi.detectors.historical import HistoricalPatternDetector
from rishi.scoring.risk_fusion import RiskFusionEngine
from rishi.handoff.handoff_router import HandoffRouter
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_sample_phishing_conversation():
    """Create a sample phishing conversation."""
    base_time = datetime.utcnow()

    messages = [
        ConversationMessage(
            message_id="msg_1",
            sender="attacker@phishsite.tk",
            content="URGENT: Your Apple account has been locked due to suspicious activity. Click here immediately to verify your identity: http://apple-verify-secure.tk/login",
            timestamp=base_time,
        ),
        ConversationMessage(
            message_id="msg_2",
            sender="victim@gmail.com",
            content="I haven't done anything suspicious. Why is my account locked?",
            timestamp=base_time + timedelta(minutes=1),
        ),
        ConversationMessage(
            message_id="msg_3",
            sender="attacker@phishsite.tk",
            content="Don't delay! Act now or your account will be permanently closed. Verify immediately: http://apple-verify-secure.tk/login",
            timestamp=base_time + timedelta(minutes=2),
        ),
        ConversationMessage(
            message_id="msg_4",
            sender="attacker@phishsite.tk",
            content="This is Apple official support. Enter your credentials NOW to confirm your identity: http://apple-verify-secure.tk/login",
            timestamp=base_time + timedelta(minutes=3),
        ),
    ]

    sender_metadata = SenderMetadata(
        user_id="attacker@phishsite.tk",
        account_age_days=5,  # Brand new account
        previous_reports=0,
        verification_status="unverified",
    )

    return ScamDetectionInput(
        conversation_id="conv_phishing_001",
        messages=messages,
        sender_metadata=sender_metadata,
    )


def create_sample_romance_scam_conversation():
    """Create a sample romance/advance-fee scam conversation."""
    base_time = datetime.utcnow()

    messages = [
        ConversationMessage(
            message_id="msg_1",
            sender="romance_scammer@dating-site.fake",
            content="Hi! I'm Emma, a successful businessman working overseas. I love your profile!",
            timestamp=base_time,
        ),
        ConversationMessage(
            message_id="msg_2",
            sender="victim@gmail.com",
            content="Thanks! Nice to meet you. Where are you from?",
            timestamp=base_time + timedelta(hours=2),
        ),
        ConversationMessage(
            message_id="msg_3",
            sender="romance_scammer@dating-site.fake",
            content="I'm working on an oil rig in Nigeria. I've won a lottery of $500,000! But I need help transferring it. I trust you. Can you help me?",
            timestamp=base_time + timedelta(hours=3),
        ),
        ConversationMessage(
            message_id="msg_4",
            sender="romance_scammer@dating-site.fake",
            content="I need $2000 for transfer fees. It's urgent! Send it to this bank account immediately and I'll pay you back with interest!",
            timestamp=base_time + timedelta(hours=4),
        ),
    ]

    sender_metadata = SenderMetadata(
        user_id="scammer_123",
        account_age_days=3,
        previous_reports=2,  # Previous complaints
        verification_status="unverified",
    )

    return ScamDetectionInput(
        conversation_id="conv_romance_001",
        messages=messages,
        sender_metadata=sender_metadata,
    )


def create_sample_legitimate_conversation():
    """Create a sample legitimate conversation."""
    base_time = datetime.utcnow()

    messages = [
        ConversationMessage(
            message_id="msg_1",
            sender="support@amazon.com",
            content="Hello, thank you for contacting Amazon support. How can we help you today?",
            timestamp=base_time,
        ),
        ConversationMessage(
            message_id="msg_2",
            sender="customer@gmail.com",
            content="Hi, I have a question about my recent order.",
            timestamp=base_time + timedelta(minutes=5),
        ),
        ConversationMessage(
            message_id="msg_3",
            sender="support@amazon.com",
            content="I'd be happy to help! Could you please provide your order number?",
            timestamp=base_time + timedelta(minutes=10),
        ),
    ]

    sender_metadata = SenderMetadata(
        user_id="support@amazon.com",
        account_age_days=3650,  # 10 years old
        previous_reports=0,
        verification_status="verified",
    )

    return ScamDetectionInput(
        conversation_id="conv_legitimate_001",
        messages=messages,
        sender_metadata=sender_metadata,
    )


def run_scam_detection_pipeline(input_data: ScamDetectionInput):
    """
    Run the complete scam detection pipeline.

    Args:
        input_data: ScamDetectionInput with conversation

    Returns:
        Detection result
    """
    logger.info(f"\n{'=' * 70}")
    logger.info(f"Processing conversation: {input_data.conversation_id}")
    logger.info(f"Messages: {len(input_data.messages)}")
    logger.info(f"Sender: {input_data.sender_metadata.user_id}")
    logger.info(f"{'=' * 70}\n")

    # Create detector input
    detector_input = DetectorInput(
        conversation_id=input_data.conversation_id,
        messages=input_data.messages,
        sender_metadata=input_data.sender_metadata,
    )

    # Initialize detectors
    linguistic_detector = LinguisticManipulationDetector()
    behavioral_detector = BehavioralPatternDetector()
    link_detector = LinkIntelligenceDetector()
    identity_detector = IdentityMismatchDetector()
    historical_detector = HistoricalPatternDetector()

    # Run detectors
    logger.info("Running detectors...")
    linguistic_score = linguistic_detector.analyze(detector_input)
    behavioral_score = behavioral_detector.analyze(detector_input)
    link_score = link_detector.analyze(detector_input)
    identity_score = identity_detector.analyze(detector_input)
    historical_score = historical_detector.analyze(detector_input)

    logger.info(f"  Linguistic:            {linguistic_score:.3f}")
    logger.info(f"  Behavioral:            {behavioral_score:.3f}")
    logger.info(f"  Link/Infrastructure:   {link_score:.3f}")
    logger.info(f"  Identity Mismatch:     {identity_score:.3f}")
    logger.info(f"  Historical:            {historical_score:.3f}")

    # Create detector breakdown
    from rishi.schemas.events import DetectorBreakdown

    breakdown = DetectorBreakdown(
        linguistic_score=linguistic_score,
        behavioral_score=behavioral_score,
        link_infrastructure_score=link_score,
        identity_mismatch_score=identity_score,
        historical_score=historical_score,
    )

    # Fuse scores
    logger.info("\nFusing detector scores...")
    fusion_engine = RiskFusionEngine()
    result = fusion_engine.fuse(detector_input, breakdown)

    logger.info(f"\nFinal Result:")
    logger.info(f"  Scam Probability:      {result.scam_probability:.1f}/100")
    logger.info(f"  Risk Level:            {result.risk_level.value}")
    logger.info(f"  Handoff Triggered:     {result.handoff_triggered}")

    # Check for handoff
    if result.handoff_triggered:
        logger.warning("\n⚠️  SCAM DETECTED - Triggering handoff to honeypot agent...")
        handoff_router = HandoffRouter()
        event = handoff_router.process_detection_result(result, detector_input)
        if event:
            logger.warning(f"  Scam Type:             {event.scam_type}")
            logger.warning(f"  Recommended Action:    {event.recommended_action}")

    logger.info(f"\n{'=' * 70}\n")

    return result


if __name__ == "__main__":
    # Test with different conversation types
    print("\n" + "=" * 70)
    print("SCAM DETECTION PIPELINE - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    # Example 1: Phishing attempt
    print("\n[EXAMPLE 1: Phishing Attack]")
    phishing_conv = create_sample_phishing_conversation()
    phishing_result = run_scam_detection_pipeline(phishing_conv)

    # Example 2: Romance/Advance-Fee scam
    print("\n[EXAMPLE 2: Romance/Advance-Fee Scam]")
    romance_conv = create_sample_romance_scam_conversation()
    romance_result = run_scam_detection_pipeline(romance_conv)

    # Example 3: Legitimate conversation
    print("\n[EXAMPLE 3: Legitimate Conversation]")
    legit_conv = create_sample_legitimate_conversation()
    legit_result = run_scam_detection_pipeline(legit_conv)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Phishing:     {phishing_result.scam_probability:.1f}/100 ({phishing_result.risk_level.value})")
    print(f"Romance:      {romance_result.scam_probability:.1f}/100 ({romance_result.risk_level.value})")
    print(f"Legitimate:   {legit_result.scam_probability:.1f}/100 ({legit_result.risk_level.value})")
    print("=" * 70 + "\n")
