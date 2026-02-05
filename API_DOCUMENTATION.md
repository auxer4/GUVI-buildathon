# Scam Intelligence Engine - API Documentation

## Overview

The Scam Intelligence Engine is a multi-agent system designed to:
1. **Detect scams** using linguistic, behavioral, and link intelligence analysis
2. **Engage scammers** safely using AI personas in honeypot conversations
3. **Extract intelligence** (UPI IDs, phone numbers, URLs, tactics)
4. **Assist victims** with personalized recovery guidance
5. **Generate reports** for law enforcement, banks, and internal analysis

---

## Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up Redis for persistence
redis-server
```

### 2. Run the Application

```bash
# Method 1: Direct Python
python main.py

# Method 2: Uvicorn with auto-reload
uvicorn main:app --reload --port 8000

# Method 3: VS Code Debug
Press F5 to start debugging
```

### 3. Access Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## API Endpoints

### System Endpoints

#### GET `/`
Root endpoint with system status.

```bash
curl -X GET http://localhost:8000/
```

**Response:**
```json
{
  "service": "Scam Intelligence Engine",
  "version": "1.0.0",
  "status": "operational",
  "modules": {
    "detection": "Rishi - ACTIVE",
    "honeypot": "Saachi - ACTIVE",
    "extraction": "Shreyas - ACTIVE",
    "recovery": "Shreyas Recovery - ACTIVE"
  }
}
```

#### GET `/health`
Health check endpoint.

```bash
curl -X GET http://localhost:8000/health
```

#### GET `/system/info`
Comprehensive system information.

```bash
curl -X GET http://localhost:8000/system/info
```

---

### Detection Endpoints (Rishi Module)

#### POST `/detect-scam`
Analyze text for scam indicators.

**Request:**
```json
{
  "text": "Hey! This is your bank. Verify your account by clicking this link: https://fake-bank.com",
  "metadata": {
    "sender_id": "unknown_sender",
    "platform": "whatsapp",
    "contact_method": "message"
  }
}
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "is_scam": true,
  "scam_probability": 0.92,
  "scam_type": "phishing",
  "detection_result": {
    "final_score": 0.92,
    "detector_results": {
      "linguistic": 0.88,
      "behavioral": 0.85,
      "link_intel": 0.98,
      "identity_mismatch": 0.75,
      "historical": 0.50
    },
    "tactics": ["phishing", "credential harvesting"],
    "risk_level": "critical"
  }
}
```

---

### Honeypot Endpoints (Saachi Module)

#### POST `/honeypot/engage`
Initiate honeypot engagement with a detected scammer.

**Request:**
```json
{
  "conversation_id": "conv_abc123",
  "original_sender_id": "scammer_001",
  "scam_probability": 0.92,
  "scam_type": "phishing",
  "persona_key": "elderly_pensioner"
}
```

**Response:**
```json
{
  "status": "engaged",
  "session_id": "honeypot_sess_xyz789",
  "conversation_id": "conv_abc123",
  "persona": "elderly_pensioner",
  "initial_response": "Hello! Thank you for reaching out. I need help with my bank account...",
  "engagement_started_at": "2025-02-05T10:30:00"
}
```

#### POST `/honeypot/message`
Send message in active honeypot session.

**Request:**
```json
{
  "session_id": "honeypot_sess_xyz789",
  "message": "Can you help me verify my account?"
}
```

**Response:**
```json
{
  "session_id": "honeypot_sess_xyz789",
  "response": "Of course! I can help you. Can you tell me your account number?",
  "engagement_score": 0.78,
  "scammer_still_engaged": true
}
```

#### GET `/honeypot/session/{session_id}`
Get active session information.

```bash
curl -X GET http://localhost:8000/honeypot/session/honeypot_sess_xyz789
```

#### POST `/honeypot/health`
Health check for honeypot module.

```bash
curl -X POST http://localhost:8000/honeypot/health
```

---

## Event Bus Architecture

The system uses an in-memory event bus for inter-agent communication. Events flow as follows:

```
Detection Pipeline
        ↓
   SCAM_CONFIRMED Event
        ↓
    Event Bus
        ↓
   Honeypot Engagement
        ↓
   HONEYPOT_ENGAGED Event
        ↓
    Intelligence Extraction
        ↓
   Victim Recovery Assistance
```

### Event Types

- **SCAM_CONFIRMED**: Emitted when scam is detected with high confidence
- **HONEYPOT_ENGAGED**: Emitted when honeypot session starts and receives messages
- **EXTRACTION_COMPLETE**: Emitted when intelligence is extracted
- **REPORT_GENERATED**: Emitted when reports are created

---

## Module Architecture

### 1. Rishi (Detection)
- **Path**: `rishi/`
- **Components**:
  - Linguistic Detector: Analyzes language patterns
  - Behavioral Detector: Detects conversation patterns
  - Link Intelligence: Analyzes URLs for malicious content
  - Identity Mismatch: Detects impersonation attempts
  - Historical Detector: Learns from past scams
  - Risk Fusion Engine: Combines scores from all detectors

### 2. Saachi (Honeypot)
- **Path**: `saachi/`
- **Components**:
  - Persona Manager: Manages AI personas
  - Conversation Engine: Generates contextual responses
  - Safety Checker: Ensures victim protection
  - Session Manager: Tracks engagement sessions
  - State Machine: Manages conversation states

### 3. Shreyas (Extraction & Recovery)
- **Path**: `shreyas/`
- **Components**:
  - Regex Extractors: Extracts UPI, phone, URLs
  - LLM Extractors: Uses language models for complex extraction
  - Entity Builder: Structures extracted entities
  - Intelligence Reporter: Generates formatted reports
  - Victim Recovery: Provides recovery guidance

### 4. Shared Utilities
- **Path**: `shared/`
- **Components**:
  - Event Bus: In-memory pub/sub system
  - Message Models: Pydantic data models
  - Redis Client: Persistence layer
  - Constants: Shared configuration

---

## Configuration

### Detector Thresholds

Edit `rishi/config/thresholds.yaml` to adjust:
- Detector weights
- Risk thresholds
- Confidence cutoffs

**Example:**
```yaml
weights:
  linguistic: 0.20
  behavioral: 0.20
  link_intel: 0.30
  identity_mismatch: 0.15
  historical: 0.15

risk_thresholds:
  low: 0.3
  medium: 0.6
  high: 0.8
  critical: 0.95
```

### Environment Variables

Create `.env` file:
```
REDIS_HOST=localhost
REDIS_PORT=6379
OPENAI_API_KEY=sk-...  # Optional, for LLM extraction
ANTHROPIC_API_KEY=sk-... # Optional, for Claude extraction
```

---

## Testing

### Run All Tests
```bash
pytest shreyas/tests -v
```

### Run Specific Test
```bash
pytest shreyas/tests/test_historical_detector.py -v
```

### With Coverage
```bash
pytest shreyas/tests --cov=rishi --cov=saachi --cov=shreyas
```

---

## Logging

Logs are written to `logs/` directory:
- `scam_engine.log`: All INFO and above messages
- `errors.log`: ERROR and above messages

**Log Levels:**
- INFO: Normal operation
- WARNING: Recoverable issues
- ERROR: Failures
- DEBUG: Detailed diagnostics (enable in settings)

---

## Common Use Cases

### 1. Detect and Engage Scammer

```bash
# Step 1: Send message to detection endpoint
curl -X POST http://localhost:8000/detect-scam \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click here to verify your UPI: https://fake-bank.com",
    "metadata": {
      "sender_id": "scammer_001",
      "platform": "whatsapp"
    }
  }'

# Step 2: If scam detected, honeypot engages automatically
# Scammer receives response from AI persona
```

### 2. Extract Intelligence

```bash
# Messages in honeypot session are automatically analyzed
# Extracted entities include:
# - UPI IDs
# - Phone numbers
# - URLs
# - Bank account info
# - Relationships/tactics
```

### 3. Generate Reports

```python
from shreyas.app.reporting.intelligence_reporter import IntelligenceReporter

reporter = IntelligenceReporter()
report = reporter.generate_law_enforcement_report(
    conversation_id="conv_123",
    sender_info={"sender_id": "scammer_001"},
    extracted_entities=[...],
    detection_results={...}
)

# Export report
json_export = reporter.export_report(report, format="json")
```

### 4. Generate Recovery Plan

```python
from shreyas.app.reporting.victim_recovery import VictimRecoveryAssistant

assistant = VictimRecoveryAssistant()
assessment = assistant.assess_victim_situation(
    scam_type=ScamType.UPI_FRAUD,
    extracted_entities=[...],
    detection_results={...}
)

plan = assistant.generate_recovery_plan(assessment)
# Contains immediate, short-term, and long-term actions
```

---

## Troubleshooting

### Issue: Detection not working
- **Check**: Is the text clear and in English?
- **Check**: Are detector weights properly configured?
- **Solution**: Review `rishi/config/thresholds.yaml`

### Issue: Honeypot not engaging
- **Check**: Is SCAM_CONFIRMED event being emitted?
- **Check**: Are event bus subscribers registered?
- **Solution**: Check logs in `logs/errors.log`

### Issue: Redis connection failed
- **Check**: Is Redis running? (`redis-server` or `redis-cli`)
- **Solution**: System falls back to in-memory storage (OK for testing)

### Issue: Tests failing
- **Check**: All dependencies installed? (`pip install -r requirements.txt`)
- **Solution**: Run `pytest --lf` to run last failed tests in verbose mode

---

## Performance Considerations

- **Detection**: ~100-200ms per message
- **Honeypot engagement**: ~50-100ms
- **Intelligence extraction**: ~200-500ms (depends on entity count)
- **Report generation**: ~100-200ms

For high-volume scenarios, consider:
- Async message processing
- Caching detector results
- Using Redis for session persistence
- Load balancing multiple instances

---

## Security Notes

⚠️ **Important**: This system handles sensitive data:
- Never log full UPI IDs, passwords, OTPs
- Use HTTPS in production
- Enable Redis authentication
- Implement rate limiting on endpoints
- Use API keys for external access
- Sanitize all user inputs

---

## Future Enhancements

- [ ] Machine learning model for improved detection
- [ ] Multi-language support
- [ ] Real-time dashboard
- [ ] API key authentication
- [ ] Webhook integrations
- [ ] Advanced reporting with analytics
- [ ] Mobile app integration
- [ ] Automated response to law enforcement queries

---

## Support & Contribution

For issues, feature requests, or contributions:
1. Check existing documentation
2. Review test cases
3. Open an issue with detailed description
4. Submit pull request with tests

---

**Last Updated**: February 5, 2025
**Version**: 1.0.0
**Status**: Production Ready ✓
