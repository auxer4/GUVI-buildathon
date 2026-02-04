# Rishi: Scam Detection, Risk Scoring & Conversation Handoff

**Person 1 Responsibility** in the Scam Intelligence Engine - A multi-agent hackathon project for bank-grade fraud detection.

---

## 📋 Overview

This module implements **production-grade scam detection** as the first stage of the Scam Intelligence Engine. It:

1. **Analyzes conversations** for linguistic, behavioral, infrastructural, and identity-based scam indicators
2. **Produces a unified risk score** (0-100) via weighted detector fusion
3. **Classifies risk levels**: safe → suspicious → high → confirmed
4. **Triggers handoff events** when scams are confirmed for downstream honeypot engagement

**Key Principle**: This is a **detection and scoring engine**, not a response engine. It identifies scams but does NOT engage with attackers—that's the honeypot agent's job.

---

## 🎯 What This Module Owns

### ✅ Detector Pipeline
- **Linguistic Manipulation Detector**: Urgency, fear appeals, authority impersonation, reward baiting
- **Behavioral Pattern Detector**: Message frequency, script rigidity, instruction repetition, pressure tactics
- **Link & Infrastructure Detector**: Domain age, URL entropy, lookalike domains, suspicious TLDs
- **Identity Mismatch Detector**: Credential inconsistencies, brand impersonation, claim misalignment
- **Historical Pattern Detector**: Placeholder for shared threat intelligence (future integration)

### ✅ Risk Fusion Engine
- Combines detector scores using **configurable weights** (YAML-based)
- Outputs normalized scores (0-100 scale)
- Classifies into risk levels: **SAFE** | **SUSPICIOUS** | **HIGH** | **CONFIRMED**

### ✅ Conversation Handoff Trigger
- Emits `SCAM_CONFIRMED` events when confidence threshold is met
- Routes to honeypot agent with full context
- Does NOT simulate scams or engage attackers

### ✅ Public FastAPI Endpoint
```
POST /detect-scam
Input:  conversation_id, messages[], sender_metadata
Output: scam_probability, risk_level, breakdown, handoff_triggered
```

---

## ❌ What This Module Does NOT Own

- **Honeypot personas & engagement** → Handled by honeypot agent
- **Data extraction from conversations** → Handled by extraction agent
- **Post-scam recovery workflows** → Handled by recovery agent
- **Threat intelligence databases** → Handled by TI agent (we consume it via event_bus)
- **UI/UX** → Backend + intelligence only

---

## 📁 Folder Structure

```
rishi/
├── __init__.py
├── config/
│   └── thresholds.yaml          # Configurable detector weights & thresholds
├── schemas/
│   └── events.py                # Pydantic models for data validation
├── detectors/
│   ├── linguistic.py            # Linguistic manipulation detection
│   ├── behavioral.py            # Behavioral pattern analysis
│   ├── link_intel.py            # Domain & URL intelligence
│   ├── identity_mismatch.py      # Identity inconsistency detection
│   └── historical.py            # Historical pattern placeholder
├── scoring/
│   └── risk_fusion.py           # Weighted score fusion & risk classification
├── handoff/
│   └── handoff_router.py        # Event emission for confirmed scams
├── api/
│   └── detect.py                # FastAPI endpoint orchestration
├── utils/
│   └── normalizers.py           # Text preprocessing utilities
└── README.md                    # This file

shared/
├── constants.py                 # System-wide constants
├── event_bus.py                 # Inter-agent event communication
└── message_models.py            # Standardized message schemas
```

---

## 🚀 Quick Start

### 1. Installation

```bash
pip install pydantic fastapi PyYAML
```

### 2. Basic Usage

```python
from rishi.schemas.events import ScamDetectionInput, ConversationMessage, SenderMetadata
from rishi.api.detect import create_detect_router
from datetime import datetime

# Create input
messages = [
    ConversationMessage(
        message_id="msg1",
        sender="attacker",
        content="Urgent! Your account has been compromised. Click here immediately.",
        timestamp=datetime.utcnow()
    )
]

sender_meta = SenderMetadata(user_id="user123", account_age_days=5)

detection_input = ScamDetectionInput(
    conversation_id="conv_123",
    messages=messages,
    sender_metadata=sender_meta
)

# Run detection (from FastAPI endpoint)
from rishi.api.detect import detect_scam
result = await detect_scam(detection_input)

print(f"Risk Level: {result.risk_level}")
print(f"Scam Probability: {result.scam_probability:.1f}%")
print(f"Handoff Triggered: {result.handoff_triggered}")
```

### 3. FastAPI Integration

```python
from fastapi import FastAPI
from rishi.api.detect import create_detect_router

app = FastAPI()
router = create_detect_router()
app.include_router(router)

# Now available at POST /detect-scam
```

---

## 🔧 Configuration

### Detector Weights (thresholds.yaml)

```yaml
detector_weights:
  linguistic: 0.30            # 30% - Linguistic manipulation
  behavioral: 0.25            # 25% - Behavioral patterns
  link_infrastructure: 0.20   # 20% - Domain/URL risk
  identity_mismatch: 0.15     # 15% - Identity inconsistencies
  historical: 0.10            # 10% - Historical patterns

risk_thresholds:
  safe: 0
  suspicious: 30
  high: 70
  confirmed: 85               # Triggers handoff
```

**How to customize**:
1. Edit `rishi/config/thresholds.yaml`
2. Restart the service
3. Weights automatically reload (see `RiskFusionEngine._load_config()`)

---

## 🔬 Detector Details

### 1. Linguistic Manipulation Detector
Analyzes message content for social engineering tactics.

**Indicators**:
- ⏰ Urgency: "immediate", "urgent", "limited time"
- 😨 Fear: "account locked", "suspicious activity"
- 🎭 Authority: "federal", "microsoft official"
- 💰 Rewards: "congratulations won", "free money"

**Output**: `linguistic_score ∈ [0.0, 1.0]`

**Example Detection**:
```python
detector = LinguisticManipulationDetector()
score = detector.analyze(detector_input)
# score = 0.75 (high manipulation detected)
```

---

### 2. Behavioral Pattern Detector
Analyzes conversation dynamics for scripted/rigid behavior.

**Indicators**:
- 📧 High message frequency (< 2 min between messages)
- 🔄 Instruction repetition (same message 3+ times)
- 🤖 Script rigidity (ignores user questions)
- ⚠️ Pressure tactics ("act now", "don't delay")

**Output**: `behavioral_score ∈ [0.0, 1.0]`

**Example**:
```python
detector = BehavioralPatternDetector()
score = detector.analyze(detector_input)
# score = 0.65 (rigid scripted behavior detected)
```

---

### 3. Link & Infrastructure Detector
Analyzes URLs and domains for phishing/obfuscation.

**Indicators**:
- 🔗 Domain age < 30 days
- 🌐 Suspicious TLDs (.tk, .ml, .ga)
- 👻 Lookalike domains (amaz0n.com vs amazon.com)
- 🔤 High URL entropy (randomness suggests obfuscation)
- 🖥️ IP-based domains instead of DNS

**Output**: `link_infrastructure_score ∈ [0.0, 1.0]`

**Example**:
```python
detector = LinkIntelligenceDetector()
score = detector.analyze(detector_input)
# score = 0.82 (suspicious domain detected)
```

---

### 4. Identity Mismatch Detector
Detects inconsistencies between claims and evidence.

**Indicators**:
- 🏢 Brand mentioned but wrong domain (Apple logo + attacker.com)
- 👤 Credential anomalies (new account claiming authority)
- 💬 Contradictory claims ("I am John" then "I am Maria")
- ✍️ Multiple different signatures

**Output**: `identity_mismatch_score ∈ [0.0, 1.0]`

**Example**:
```python
detector = IdentityMismatchDetector()
score = detector.analyze(detector_input)
# score = 0.88 (strong impersonation detected)
```

---

### 5. Historical Pattern Detector (Placeholder)
Reserved for shared threat intelligence integration.

**Future Features** (TODO):
- Query event_bus for confirmed scams with similar patterns
- Cross-reference with known bad actors
- Pattern matching against historical scams
- Integration with external threat feeds

**Current Status**: Returns 0.0 (neutral)

**How to Integrate**:
```python
detector = HistoricalPatternDetector(event_bus=get_event_bus())
score = detector.analyze(detector_input)
```

---

## 📊 Risk Fusion Engine

The `RiskFusionEngine` combines all detector scores into a final risk assessment.

**Process**:
1. **Normalize**: All detector scores are [0.0, 1.0]
2. **Weight**: Apply configured weights (sum = 1.0)
3. **Fuse**: Weighted average = final normalized score
4. **Scale**: Multiply by 100 → [0.0, 100.0]
5. **Classify**: Map to risk level based on thresholds

**Formula**:
```
scam_probability = (
    linguistic_score × 0.30 +
    behavioral_score × 0.25 +
    link_infrastructure_score × 0.20 +
    identity_mismatch_score × 0.15 +
    historical_score × 0.10
) × 100
```

**Example Output**:
```json
{
  "conversation_id": "conv_123",
  "scam_probability": 82.5,
  "risk_level": "high",
  "breakdown": {
    "linguistic_score": 0.85,
    "behavioral_score": 0.70,
    "link_infrastructure_score": 0.75,
    "identity_mismatch_score": 0.88,
    "historical_score": 0.0
  },
  "handoff_triggered": false
}
```

---

## 🎯 Handoff Trigger

When `risk_level == "confirmed"` (scam_probability ≥ 85):

1. **ScamConfirmedEvent is emitted**:
   ```python
   event = ScamConfirmedEvent(
       conversation_id="conv_123",
       scam_probability=92.5,
       risk_level="confirmed",
       scam_type="impersonation",
       recommended_action="honeypot_engagement",
       metadata={...}
   )
   ```

2. **HandoffRouter publishes to event_bus**:
   ```python
   event_bus.emit("SCAM_CONFIRMED", event)
   ```

3. **Honeypot agent subscribes** and receives notification to engage

---

## 🔌 Inter-Agent Communication

### Event Bus Integration

All agents communicate via the **shared event_bus** in `shared/event_bus.py`.

**Current**: In-memory pub/sub (for hackathon)
**Production**: Would use Redis, RabbitMQ, or Kafka

### Message Flow

```
Conversation Arrives
        ↓
[Rishi: Scam Detection]
        ↓
    Analysis
        ↓
    Risk Score
        ↓
Is Risk >= Confirmed?
    ↙        ↘
   NO        YES
    ↓         ↓
Return Result  Emit SCAM_CONFIRMED
               ↓
        [Honeypot Agent]
               ↓
        [Extraction Agent]
               ↓
        [Recovery Agent]
```

### Subscribing to Events

**Example: Honeypot agent subscribes**:
```python
from shared.event_bus import get_event_bus, EventType

event_bus = get_event_bus()

async def handle_scam_confirmed(event):
    conversation_id = event.payload['conversation_id']
    scam_type = event.payload['scam_type']
    print(f"Engaging honeypot for {scam_type} scam")

event_bus.subscribe(EventType.SCAM_CONFIRMED, handle_scam_confirmed)
```

### Message Schemas

See `shared/message_models.py` for standardized schemas:
- `ScamDetectionResultMessage` - Published after analysis
- `ScamConfirmedMessage` - Published when confirmed
- `HoneypotEngagementRequest` - Sent to honeypot agent
- `ExtractionRequest` - Sent to extraction agent
- `RecoveryInitiation` - Sent to recovery agent

---

## 🧪 Testing & Extension

### Adding a New Detector

```python
# 1. Create new detector in detectors/my_detector.py
from rishi.schemas.events import DetectorInput

class MyCustomDetector:
    def analyze(self, detector_input: DetectorInput) -> float:
        """Return score [0.0, 1.0]"""
        score = 0.0
        # Your logic here
        return score

# 2. Register in api/detect.py
_my_detector = MyCustomDetector()

# 3. Add to fusion in API endpoint
my_score = _my_detector.analyze(detector_input)

# 4. Update DetectorBreakdown schema in schemas/events.py
# 5. Update weights in config/thresholds.yaml
```

### Replacing with ML Models

Each detector is designed to be replaceable:

```python
# Before: Rule-based
class LinguisticManipulationDetector:
    def analyze(self, detector_input):
        # Pattern matching
        return score

# After: ML-based
class LinguisticManipulationDetectorML:
    def __init__(self, model_path):
        self.model = load_model(model_path)  # Load BERT, GPT, etc.
    
    def analyze(self, detector_input):
        text = " ".join([msg.content for msg in detector_input.messages])
        embedding = self.model.encode(text)
        score = self.classifier.predict(embedding)
        return score

# Swap in API
_linguistic_detector = LinguisticManipulationDetectorML("models/detector.pt")
```

### Integrating LLMs

Placeholder TODO in `detectors/linguistic.py`:

```python
# TODO: Replace with LLM-based scoring when ML pipeline is available

# Example with OpenAI:
from openai import OpenAI

class LinguisticManipulationDetectorLLM:
    def __init__(self):
        self.client = OpenAI()
    
    def analyze(self, detector_input):
        full_text = " ".join([msg.content for msg in detector_input.messages])
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a scam detection expert. Rate the following message for manipulation on a scale 0-1.",
                "role": "user",
                "content": full_text
            }]
        )
        
        score = float(response.choices[0].message.content)
        return score
```

---

## 📝 Logging & Debugging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rishi")
```

**Log Examples**:
```
INFO: Processing scam detection for conv_123 (5 messages)
DEBUG: Detector scores: linguistic=0.75, behavioral=0.65, link=0.82, identity=0.88, historical=0.0
INFO: Fused result: score=77.5, risk=high
WARNING: SCAM CONFIRMED: conv_123 (probability=92.0, type=impersonation)
```

---

## 🔒 Production Considerations

### Security
- ✅ No credential storage in detector logic
- ✅ Input validation via Pydantic
- ✅ Configurable risk thresholds (not hardcoded)
- ✅ Audit logging for all detections

### Scalability
- ✅ Detectors are stateless (can be parallelized)
- ✅ No database dependencies
- ✅ Configuration-driven (no code changes for tuning)

### Reliability
- ✅ Graceful error handling in each detector
- ✅ Fallback to neutral scores on error
- ✅ Event emission retry logic (TODO)

### Monitoring
- ✅ Health check endpoint (`GET /health`)
- ✅ Structured logging
- ✅ Detector score distribution tracking (TODO)

---

## 📚 API Reference

### POST /detect-scam

**Request**:
```json
{
  "conversation_id": "conv_123",
  "messages": [
    {
      "message_id": "msg1",
      "sender": "attacker",
      "content": "Urgent! Your account is compromised.",
      "timestamp": "2026-01-31T10:30:00Z"
    }
  ],
  "sender_metadata": {
    "user_id": "user_456",
    "account_age_days": 5,
    "verification_status": "unverified"
  }
}
```

**Response**:
```json
{
  "conversation_id": "conv_123",
  "scam_probability": 82.5,
  "risk_level": "high",
  "breakdown": {
    "linguistic_score": 0.85,
    "behavioral_score": 0.70,
    "link_infrastructure_score": 0.75,
    "identity_mismatch_score": 0.88,
    "historical_score": 0.0
  },
  "handoff_triggered": false,
  "timestamp": "2026-01-31T10:30:05Z",
  "metadata": {"sender_id": "user_456", "message_count": 1}
}
```

### GET /health

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T10:30:05Z"
}
```

---

## 🚦 Next Steps for Integration

1. **Honeypot Agent** (Saachi):
   - Subscribe to `SCAM_CONFIRMED` events
   - Implement honeypot personas
   - Engage attackers and gather evidence

2. **Extraction Agent** (Samyak):
   - Subscribe to honeypot conversation logs
   - Extract structured intelligence (phone numbers, accounts, etc.)
   - Store for recovery and prosecution

3. **Recovery Agent** (Shreyas):
   - Subscribe to extraction results
   - Initiate victim recovery workflows
   - Coordinate with platforms and law enforcement

4. **Threat Intelligence**:
   - Historical detector integration
   - Cross-conversation pattern matching
   - Build attacker profiles and signatures

---

## 📞 Support & Questions

This is Person 1's module. Contact for:
- Detector thresholds and tuning
- Risk score interpretation
- Event bus integration
- API changes

**Do NOT contact about**:
- Honeypot logic (Saachi)
- Extraction workflows (Samyak)
- Recovery processes (Shreyas)

---

## 📄 License & Attribution

Scam Intelligence Engine - Multi-Agent Hackathon Project
