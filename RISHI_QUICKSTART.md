"""
RISHI QUICK START GUIDE

Run this to test the complete scam detection pipeline.

Requirements:
- Python 3.10+
- FastAPI, Pydantic, PyYAML (from requirements.txt)

Three ways to use Rishi:
1. Direct Python: Run rishi_example.py
2. FastAPI: Start main.py and POST to /detect-scam
3. Integration: Import in your code
"""

# ============================================================================
# METHOD 1: DIRECT PYTHON (RECOMMENDED FOR TESTING)
# ============================================================================

# Run the example:
# python rishi_example.py

# This will:
# 1. Create 3 sample conversations (phishing, romance, legitimate)
# 2. Run them through all detectors
# 3. Print detailed scores and analysis
# 4. Show which ones trigger handoff

# Expected output:
# [EXAMPLE 1: Phishing Attack]
# Scam Probability: 84.5/100
# Risk Level: high
# ⚠️  SCAM DETECTED - Triggering handoff...
#
# [EXAMPLE 2: Romance/Advance-Fee Scam]
# Scam Probability: 91.2/100
# Risk Level: confirmed
# ⚠️  SCAM DETECTED - Triggering handoff...
#
# [EXAMPLE 3: Legitimate Conversation]
# Scam Probability: 2.3/100
# Risk Level: safe

# ============================================================================
# METHOD 2: FASTAPI SERVER
# ============================================================================

# Start the server:
# cd GUVI-buildathon
# python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Then test with curl or Postman:
# curl -X POST http://127.0.0.1:8000/detect-scam \
#   -H "Content-Type: application/json" \
#   -d '{
#     "conversation_id": "test_123",
#     "messages": [
#       {
#         "message_id": "msg1",
#         "sender": "attacker@suspicious.tk",
#         "content": "URGENT! Click here immediately to verify your account",
#         "timestamp": "2026-02-04T10:00:00Z"
#       }
#     ],
#     "sender_metadata": {
#       "user_id": "user_123",
#       "account_age_days": 2,
#       "verification_status": "unverified"
#     }
#   }'

# Expected response:
# {
#   "conversation_id": "test_123",
#   "scam_probability": 75.3,
#   "risk_level": "high",
#   "breakdown": {
#     "linguistic_score": 0.85,
#     "behavioral_score": 0.40,
#     "link_infrastructure_score": 0.90,
#     "identity_mismatch_score": 0.60,
#     "historical_score": 0.0
#   },
#   "handoff_triggered": false,
#   "timestamp": "2026-02-04T10:00:05Z"
# }

# Check health:
# curl http://127.0.0.1:8000/health
# {"status": "healthy", "timestamp": "2026-02-04T10:00:05Z"}

# ============================================================================
# METHOD 3: PYTHON INTEGRATION
# ============================================================================

# from rishi.schemas.events import ScamDetectionInput, ConversationMessage, SenderMetadata
# from rishi.detectors.linguistic import LinguisticManipulationDetector
# from rishi.scoring.risk_fusion import RiskFusionEngine
# from datetime import datetime
#
# # Create input
# messages = [
#     ConversationMessage(
#         message_id="msg1",
#         sender="attacker",
#         content="Congratulations! You won $1,000,000! Click here NOW!",
#         timestamp=datetime.utcnow()
#     )
# ]
#
# input_data = ScamDetectionInput(
#     conversation_id="conv_123",
#     messages=messages,
#     sender_metadata=SenderMetadata(user_id="attacker", account_age_days=1)
# )
#
# # Run detector
# detector = LinguisticManipulationDetector()
# from rishi.schemas.events import DetectorInput
# detector_input = DetectorInput(
#     conversation_id=input_data.conversation_id,
#     messages=input_data.messages,
#     sender_metadata=input_data.sender_metadata
# )
# score = detector.analyze(detector_input)
# print(f"Linguistic Score: {score:.2f}")

# ============================================================================
# UNDERSTANDING THE OUTPUT
# ============================================================================

# Scam Probability Scale (0-100):
# - 0-30:   SAFE (very likely legitimate)
# - 30-70:  SUSPICIOUS (needs investigation)
# - 70-85:  HIGH (likely scam, monitor closely)
# - 85-100: CONFIRMED (definitely scam, trigger handoff)

# Risk Levels:
# - safe: No scam indicators
# - suspicious: Some indicators present, verify with human
# - high: Strong scam indicators, block account
# - confirmed: Overwhelming indicators, engage honeypot

# Detector Breakdown (0.0-1.0 scale):
# - linguistic_score: Language manipulation detected
# - behavioral_score: Suspicious conversation patterns
# - link_infrastructure_score: Malicious URLs/domains
# - identity_mismatch_score: Impersonation detected
# - historical_score: Known attacker patterns

# ============================================================================
# CONFIGURATION
# ============================================================================

# Adjust detector weights:
# Edit: rishi/config/thresholds.yaml
# 
# Example: Increase behavioral weight
# detector_weights:
#   linguistic: 0.25        # Reduced
#   behavioral: 0.35        # Increased
#   link_infrastructure: 0.20
#   identity_mismatch: 0.15
#   historical: 0.05        # Reduced

# Adjust risk thresholds:
# Edit: rishi/config/thresholds.yaml
#
# Example: Lower confirmation threshold
# risk_thresholds:
#   safe: 0
#   suspicious: 30
#   high: 65          # Lowered from 70
#   confirmed: 80     # Lowered from 85

# ============================================================================
# DEBUGGING
# ============================================================================

# Enable verbose logging:
# import logging
# logging.basicConfig(level=logging.DEBUG)

# Check which detector is triggering high scores:
# Look at detector scores in breakdown
# Adjust relevant detector thresholds in config

# Test individual detectors:
# from rishi.detectors.linguistic import LinguisticManipulationDetector
# detector = LinguisticManipulationDetector()
# score = detector.analyze(detector_input)

# ============================================================================
# NEXT STEPS
# ============================================================================

# 1. Run: python rishi_example.py
# 2. Review: RISHI_COMPLETION.md
# 3. Read: rishi/README.md for full documentation
# 4. Start: main.py for FastAPI server
# 5. Integrate: Other agents subscribe to SCAM_CONFIRMED events
# 6. Customize: Adjust weights for your use case
# 7. Deploy: Set up production event bus (Redis/RabbitMQ)

# ============================================================================
# COMMON ISSUES & SOLUTIONS
# ============================================================================

# Issue: "Module not found: rishi"
# Solution: Ensure you're running from GUVI-buildathon directory
#          or add to PYTHONPATH: export PYTHONPATH=$PYTHONPATH:/path/to/GUVI-buildathon

# Issue: "Config file not found"
# Solution: Check that rishi/config/thresholds.yaml exists
#          Script will use defaults if missing

# Issue: All scams getting low scores
# Solution: Increase detector weights in thresholds.yaml
#          Lower risk thresholds
#          Check detector logic matches your scam patterns

# Issue: All messages getting high scores
# Solution: Decrease detector weights
#          Raise risk thresholds
#          Review detector patterns - may be too aggressive

# ============================================================================
"""

if __name__ == "__main__":
    print(__doc__)
    print("\nTo run the example pipeline:")
    print("  python rishi_example.py")
    print("\nTo start the FastAPI server:")
    print("  python -m uvicorn main:app --reload")
    print("\nFor full documentation:")
    print("  cat rishi/README.md")
    print("\nFor completion status:")
    print("  cat RISHI_COMPLETION.md")
