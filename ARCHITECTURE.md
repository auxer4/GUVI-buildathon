# Scam Intelligence Engine - Architecture Document

## System Overview

The Scam Intelligence Engine is a **multi-agent system** for detecting, containing, extracting intelligence from, and recovering victims of scams. This document describes the overall architecture and Rishi's (Person 1) role within it.

```
┌──────────────────────────────────────────────────────────────────────┐
│                   SCAM INTELLIGENCE ENGINE                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Incoming Conversation                                              │
│         │                                                            │
│         ↓                                                            │
│  ┌─────────────────────────────────────────┐                       │
│  │ RISHI: Scam Detection & Risk Scoring    │ (Person 1)            │
│  │                                         │                       │
│  │ • Linguistic Analysis                   │                       │
│  │ • Behavioral Analysis                   │                       │
│  │ • Link/Infrastructure Analysis          │                       │
│  │ • Identity Mismatch Detection           │                       │
│  │ • Historical Pattern Matching           │                       │
│  │                                         │                       │
│  │ Output: Scam Probability (0-100)        │                       │
│  │ Risk Level: SAFE|SUSPICIOUS|HIGH|CONFIRMED│                    │
│  └─────────────────────────────────────────┘                       │
│         │                                                            │
│         └─→ Risk < Confirmed? → Return Result                      │
│         │                                                            │
│         └─→ Risk >= Confirmed? → Emit SCAM_CONFIRMED               │
│             │                                                       │
│             ↓                                                       │
│  ┌─────────────────────────────────────────┐                       │
│  │ SAACHI: Honeypot Engagement             │ (Person 2) - TODO    │
│  │                                         │                       │
│  │ • Create honeypot persona               │                       │
│  │ • Engage attacker in conversation       │                       │
│  │ • Build rapport & gather context        │                       │
│  │ • Record all interactions               │                       │
│  └─────────────────────────────────────────┘                       │
│             │                                                       │
│             ↓                                                       │
│  ┌─────────────────────────────────────────┐                       │
│  │ SAMYAK: Data Extraction                 │ (Person 3) - TODO    │
│  │                                         │                       │
│  │ • Extract structured intelligence       │                       │
│  │ • Identify payment methods              │                       │
│  │ • Extract personal information          │                       │
│  │ • Build attacker profile                │                       │
│  └─────────────────────────────────────────┘                       │
│             │                                                       │
│             ↓                                                       │
│  ┌─────────────────────────────────────────┐                       │
│  │ SHREYAS: Victim Recovery                │ (Person 4) - TODO    │
│  │                                         │                       │
│  │ • Notify potential victims              │                       │
│  │ • Provide recovery resources            │                       │
│  │ • Coordinate with platforms             │                       │
│  │ • Support prosecution efforts           │                       │
│  └─────────────────────────────────────────┘                       │
│                                                                      │
│  All agents communicate via: shared/event_bus.py                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Rishi Module Architecture

### High-Level Design

```
Input: Conversation
  │
  ├─→ [Linguistic Detector]   → linguistic_score [0,1]
  │
  ├─→ [Behavioral Detector]   → behavioral_score [0,1]
  │
  ├─→ [Link Detector]         → link_score [0,1]
  │
  ├─→ [Identity Detector]     → identity_score [0,1]
  │
  └─→ [Historical Detector]   → historical_score [0,1]
      │
      ↓
  [Risk Fusion Engine]
  Weighted Average of Scores
      │
      ↓
  Final Score [0, 100]
      │
      ├─→ SAFE (0-29)        → Return Result
      ├─→ SUSPICIOUS (30-69) → Return Result
      ├─→ HIGH (70-84)       → Return Result
      └─→ CONFIRMED (85+)    → Emit Event + Return Result
```

### Module Decomposition

#### 1. Detectors (Independent, Stateless)

Each detector:
- Accepts `DetectorInput` (conversation + metadata)
- Performs independent analysis
- Returns normalized score [0.0, 1.0]
- Never calls other detectors
- Has no side effects

**Detectors**:
- `linguistic.py` - Pattern-based analysis (future: LLM-based)
- `behavioral.py` - Conversation dynamics analysis
- `link_intel.py` - URL/domain reputation
- `identity_mismatch.py` - Credential inconsistency detection
- `historical.py` - Threat intelligence integration

**Extension Point**: Replace any detector with ML model:
```python
# Before: Rule-based
class LinguisticDetector:
    def analyze(self, input):
        score = sum(patterns_matched) * 0.2  # Simple heuristic
        return score

# After: ML-based
class LinguisticDetectorML:
    def __init__(self, model):
        self.model = load_model(model)
    
    def analyze(self, input):
        features = extract_features(input)
        score = self.model.predict(features)
        return score
```

#### 2. Risk Fusion Engine (Configurable Weighting)

```
Input: All detector scores [0,1]
  │
  ├─→ linguistic_score × 0.30
  ├─→ behavioral_score × 0.25
  ├─→ link_score × 0.20
  ├─→ identity_score × 0.15
  └─→ historical_score × 0.10
      │
      ↓
  Sum = fused_score [0, 1]
      │
      ↓
  fused_score × 100 = probability [0, 100]
      │
      ↓
  Risk Classification:
  - < 30  → SAFE
  - 30-69 → SUSPICIOUS
  - 70-84 → HIGH
  - 85+   → CONFIRMED
```

**Configuration**: `config/thresholds.yaml`
- Weights are **not hardcoded** - easily tunable
- Thresholds can be adjusted without code changes

#### 3. Handoff Router (Event Emission)

```
If risk_level == CONFIRMED:
  │
  ├─→ Create ScamConfirmedEvent
  ├─→ Infer scam_type (impersonation|phishing|romance|etc.)
  ├─→ Attach full context & metadata
  └─→ Emit to event_bus
      │
      └─→ [Event Bus] broadcasts to subscribers
          │
          └─→ [Honeypot Agent] receives & engages
```

#### 4. API Endpoint (Orchestration)

```
FastAPI POST /detect-scam
  │
  ├─→ Validate input
  ├─→ Instantiate all detectors
  ├─→ Run detectors (can be parallelized)
  ├─→ Create DetectorBreakdown
  ├─→ Call RiskFusionEngine.fuse()
  ├─→ Check if handoff needed
  ├─→ If yes: HandoffRouter.process()
  └─→ Return ScamDetectionResult
```

---

## Data Flow Diagrams

### Single Conversation Analysis

```
┌─────────────────────┐
│  Conversation       │
│  • msg1: user       │
│  • msg2: attacker   │
│  • msg3: attacker   │
│  Metadata: sender   │
└──────────┬──────────┘
           │
           ↓
    ┌──────────────────────────────────────┐
    │     DetectorInput Created            │
    └──────────┬───────────────────────────┘
               │
    ┌──────────┴────────────────────────────────────────┐
    │                                                   │
    ↓                    ↓                 ↓            ↓
┌────────┐        ┌──────────┐      ┌──────────┐  ┌────────┐
│Linguistic   │        │Behavioral    │      │Link/Infra│  │Identity│
│0.75         │        │0.65          │      │0.82      │  │0.88    │
└────────┘        └──────────┘      └──────────┘  └────────┘
    │                    │                 │            │
    └──────────┬─────────┴─────────────────┴────────────┘
               │
               ↓
        ┌─────────────────┐
        │ Risk Fusion     │
        │ (Weighted Avg)  │
        └────────┬────────┘
                 │
          score = 0.79
          prob = 79%
                 │
                 ↓
        ┌─────────────────┐
        │ HIGH Risk       │
        │ (70-84 range)   │
        └────────┬────────┘
                 │
                 ↓
        Result Returned
        (No Handoff)
```

### Confirmed Scam with Handoff

```
┌─────────────────────┐
│  Conversation       │
│  • Urgent msg       │
│  • Phishing link    │
│  • Authority claim  │
└──────────┬──────────┘
           │
    ┌──────┴────────────────────────────┐
    ↓       ↓        ↓        ↓        ↓
   0.85    0.78    0.92    0.90    0.0
            │
            ↓
       score = 0.86
       prob = 86%
            │
            ↓
    CONFIRMED Risk
    (>= 85)
            │
            ↓
    ┌───────────────────────────────┐
    │ HandoffRouter:                │
    │ • Infer scam_type: phishing   │
    │ • Create event                │
    │ • Emit SCAM_CONFIRMED         │
    └───────────────────┬───────────┘
                        │
                        ↓
            ┌─────────────────────────────┐
            │ [Event Bus]                 │
            │ EventType: SCAM_CONFIRMED   │
            │ Payload: {context...}       │
            └────────────┬────────────────┘
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
        ┌─────────────┐      ┌──────────────┐
        │Honeypot Subs│      │Extraction Sub│
        │Process Event│      │Process Event │
        └─────────────┘      └──────────────┘
```

---

## Data Structures

### Input: ScamDetectionInput
```python
{
    "conversation_id": "conv_123",
    "messages": [
        {
            "message_id": "msg1",
            "sender": "attacker",
            "content": "Urgent: Your account is compromised!",
            "timestamp": "2026-01-31T10:30:00Z"
        },
        ...
    ],
    "sender_metadata": {
        "user_id": "attacker_001",
        "account_age_days": 2,
        "verification_status": "unverified"
    }
}
```

### Output: ScamDetectionResult
```python
{
    "conversation_id": "conv_123",
    "scam_probability": 86.5,
    "risk_level": "confirmed",
    "breakdown": {
        "linguistic_score": 0.85,
        "behavioral_score": 0.78,
        "link_infrastructure_score": 0.92,
        "identity_mismatch_score": 0.90,
        "historical_score": 0.0
    },
    "handoff_triggered": true,
    "timestamp": "2026-01-31T10:30:05Z",
    "metadata": {
        "sender_id": "attacker_001",
        "message_count": 2
    }
}
```

### Event: ScamConfirmedEvent
```python
{
    "event_type": "SCAM_CONFIRMED",
    "conversation_id": "conv_123",
    "scam_probability": 86.5,
    "risk_level": "confirmed",
    "detector_breakdown": {...},
    "scam_type": "phishing",
    "recommended_action": "honeypot_engagement",
    "timestamp": "2026-01-31T10:30:05Z",
    "metadata": {...}
}
```

---

## Inter-Agent Communication

### Event Bus Protocol

```python
# Agent subscribes to events
event_bus.subscribe(EventType.SCAM_CONFIRMED, handler)

# When event occurs, all subscribers notified
# Handlers are called asynchronously (non-blocking)

# Example: Honeypot agent receives event
async def handle_scam(event):
    conversation_id = event.conversation_id
    scam_type = event.payload['scam_type']
    
    # Create honeypot session
    honeypot.engage(conversation_id, scam_type)
```

### Message Flow Between Agents

```
RISHI (Detection)
    ↓ Emits: SCAM_CONFIRMED
    └─→ [Event Bus]
        │
        ├─→ SAACHI (Honeypot)
        │   └─→ Engages attacker
        │       └─→ Emits: HONEYPOT_ENGAGED
        │           └─→ [Event Bus]
        │               └─→ SAMYAK (Extraction)
        │                   └─→ Extracts intel
        │                       └─→ Emits: EXTRACTION_COMPLETE
        │                           └─→ [Event Bus]
        │                               └─→ SHREYAS (Recovery)
        │                                   └─→ Initiates recovery
        │
        └─→ Historical DB
            └─→ Update threat patterns
```

---

## Design Principles

### 1. Separation of Concerns
- **Detection** (Rishi): Identify scams
- **Engagement** (Saachi): Interact with attackers
- **Extraction** (Samyak): Get intelligence
- **Recovery** (Shreyas): Help victims

### 2. Modularity
- Each detector is independent
- Each module has single responsibility
- Easy to test and replace

### 3. Extensibility
- Detectors can be added without modifying others
- Weights configurable without code changes
- ML models can replace rule-based logic

### 4. Statelessness
- Detectors don't maintain state
- No side effects
- Easily parallelizable

### 5. No Hardcoding
- Configuration in YAML
- No entity names hardcoded
- Risk thresholds tunable

---

## Future Enhancements

### Phase 2: ML Integration
```python
# Replace detectors with fine-tuned models
LinguisticDetectorML (using BERT/GPT)
BehavioralDetectorRL (using sequence models)
LinkDetectorGNN (using graph neural networks)
```

### Phase 3: Real-time Event Streaming
```
In-Memory Event Bus
    ↓ (for hackathon)
    ↓
Production Replacements:
- Redis Streams
- RabbitMQ
- Apache Kafka
- AWS EventBridge
```

### Phase 4: Distributed Analysis
```
Detector A on Node 1 ─┐
Detector B on Node 2 ─┼─→ Central Fusion Engine
Detector C on Node 3 ─┘
```

### Phase 5: Threat Intelligence Integration
```
Historical Detector
    ↓
    Subscribe to SCAM_CONFIRMED events
    ↓
    Build attacker graph
    ↓
    Match patterns across conversations
    ↓
    Feed back into historical scoring
```

---

## Testing Strategy

### Unit Tests
```python
# Each detector has unit tests
test_linguistic_urgency()
test_behavioral_frequency()
test_link_entropy()
test_identity_mismatch()

# Risk fusion has tests
test_weighted_average()
test_risk_classification()
```

### Integration Tests
```python
# Full pipeline tests
test_scenario_phishing()
test_scenario_romance()
test_scenario_tech_support()

# Event emission tests
test_handoff_triggering()
test_event_bus_integration()
```

### Example Scenarios
- See `example_scenarios.py` for real-world test cases
- Run: `python example_scenarios.py`

---

## Deployment

### Development
```bash
python main.py
# Server at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Production
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## Monitoring & Observability

### Metrics to Track
- Detector score distributions
- Risk level frequencies
- Handoff trigger rate
- Event bus throughput
- False positive rate (calibration)

### Logs
- All detections logged with full breakdown
- Event emissions logged
- Errors logged with context

### Dashboards
- Scam probability histogram
- Risk level distribution
- Detector performance comparison
- Event flow visualization

---

## Security Considerations

### Input Validation
- All inputs validated with Pydantic
- No injection vulnerabilities
- Message length limits

### Output Safety
- Scores are normalized (0-100)
- No credential leakage
- No sensitive data in logs

### Event Bus Security
- In-memory for hackathon (safe)
- Production: require authentication
- Audit all event emissions

---

## Conclusion

This architecture enables:
- ✅ Clean separation of concerns
- ✅ Easy testing and debugging
- ✅ Configuration-driven behavior
- ✅ Extensible detector pipeline
- ✅ Scalable inter-agent communication
- ✅ Bank-grade fraud detection capability

All while maintaining clarity and maintainability for a hackathon team project.
