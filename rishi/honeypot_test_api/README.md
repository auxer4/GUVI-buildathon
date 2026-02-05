"""
# Honeypot Test API

This is a **standalone, minimal FastAPI application** designed for prototype testing submission. It provides a clean endpoint for external testers to validate honeypot functionality without requiring the full system setup.

---

## 📋 Purpose

This test API allows external testers (like the Honeypot API Endpoint Tester) to:
- ✅ Verify endpoint reachability
- ✅ Validate API key authentication
- ✅ Test JSON request/response validation
- ✅ Confirm correct HTTP status codes
- ✅ Validate basic honeypot behavior (scoring & handoff)

**Note:** This module is **isolated for testing only** and does **NOT affect** the main detection system. Core intelligence lives in `rishi/detectors/` with full ML capabilities.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r ../../requirements.txt
```

### 2. Set API Key (Optional)
```bash
export HONEYPOT_API_KEY="your-secret-key"
```

### 3. Run the Server
```bash
python -m uvicorn rishi.honeypot_test_api.app:app --reload --host 127.0.0.1 --port 8001
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### 4. Test the Endpoint
```bash
curl -X POST http://127.0.0.1:8001/honeypot/test \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "messages": [
      {"sender": "scammer", "text": "Your account is at risk! Urgent action needed."},
      {"sender": "user", "text": "What should I do?"}
    ],
    "metadata": {"source": "telegram"}
  }'
```

---

## 📡 API Endpoint

### `POST /honeypot/test`

Analyzes a conversation for scam indicators and returns probability score with handoff decision.

#### Authentication
**Header:** `X-API-Key` (required)
```
X-API-Key: test-api-key-12345
```

Default key: `test-api-key-12345` (from `config.py`)

#### Request Body

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "sender": "string",
      "text": "string"
    }
  ],
  "metadata": {
    "source": "string"
  }
}
```

**Fields:**
- `conversation_id` (required): Unique identifier for conversation
- `messages` (required): Array of message objects
  - `sender` (required): Who sent the message (e.g., "scammer", "user")
  - `text` (required): Message content
- `metadata` (optional): Context about the conversation
  - `source`: Where conversation came from (e.g., "telegram", "email")

#### Response Body (Success)

```json
{
  "status": "ok",
  "honeypot_active": true,
  "scam_probability": 87.5,
  "handoff": true,
  "message": "Scam confirmed (score: 87.5/100). Handing off to honeypot engagement."
}
```

**Fields:**
- `status`: Always "ok" on success
- `honeypot_active`: Whether honeypot system is operational
- `scam_probability`: Score from 0-100 (0=safe, 100=confirmed scam)
- `handoff`: Whether to trigger handoff to next agent (true if score >= 80)
- `message`: Human-readable explanation

#### Response Body (Error)

```json
{
  "status": "error",
  "error": "Invalid API key",
  "code": 401
}
```

#### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (missing/invalid API key) |
| 500 | Internal server error |

---

## 📝 Example Requests & Responses

### Example 1: Phishing Scam
**Request:**
```bash
curl -X POST http://127.0.0.1:8001/honeypot/test \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "phishing_001",
    "messages": [
      {"sender": "scammer", "text": "URGENT: Your bank account is suspended! Verify immediately at https://fake-bank.tk"},
      {"sender": "user", "text": "Oh no! What do I do?"},
      {"sender": "scammer", "text": "Click the link now! Use OTP: 123456"}
    ]
  }'
```

**Response:**
```json
{
  "status": "ok",
  "honeypot_active": true,
  "scam_probability": 89.3,
  "handoff": true,
  "message": "Scam confirmed (score: 89.3/100). Handing off to honeypot engagement."
}
```

---

### Example 2: Legitimate Conversation
**Request:**
```bash
curl -X POST http://127.0.0.1:8001/honeypot/test \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "legitimate_001",
    "messages": [
      {"sender": "customer_support", "text": "Hello! How can I help you today?"},
      {"sender": "user", "text": "I have a question about my order."},
      {"sender": "customer_support", "text": "I would be happy to assist. What is your order number?"}
    ]
  }'
```

**Response:**
```json
{
  "status": "ok",
  "honeypot_active": true,
  "scam_probability": 12.5,
  "handoff": false,
  "message": "Conversation appears safe (score: 12.5/100)"
}
```

---

### Example 3: Missing API Key
**Request:**
```bash
curl -X POST http://127.0.0.1:8001/honeypot/test \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "test", "messages": []}'
```

**Response:** (401)
```json
{
  "status": "error",
  "error": "Missing X-API-Key header",
  "code": 401
}
```

---

## 🧪 Testing with External Tester

This API is designed to pass the **Honeypot API Endpoint Tester** which validates:

1. ✅ **Endpoint Reachability**
   - Tester sends POST to `/honeypot/test`
   - API responds with 200/401 (not 404 or 500)

2. ✅ **Authentication**
   - Missing X-API-Key → 401 with error JSON
   - Invalid key → 401 with error JSON
   - Valid key → 200 with response JSON

3. ✅ **Request Validation**
   - Valid JSON accepted
   - Missing required fields → 400
   - Empty messages → 400

4. ✅ **Response Format**
   - Always returns valid JSON
   - Contains all required fields
   - Proper HTTP status codes

5. ✅ **Honeypot Behavior**
   - Calculates scam_probability (0-100)
   - Sets handoff = true when score >= 80
   - Includes explanatory message

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
HONEYPOT_API_KEY = "your-secret-key"      # API authentication
SCAM_THRESHOLD_FOR_HANDOFF = 80           # Score threshold for handoff
HONEYPOT_ENABLED = True                   # Enable/disable system
```

Or use environment variables:
```bash
export HONEYPOT_API_KEY="your-key"
export DEBUG="true"
```

---

## 📚 Implementation Notes

### Scoring Algorithm

The `logic.py` module implements a **stub scoring function** based on:
- Message volume (0-20 points)
- Urgency keywords detection (0-30 points)
- Suspicious patterns (URLs, phone, UPI) (0-25 points)
- Text length analysis (0-15 points)
- Sender pattern analysis (0-10 points)

**⚠️ This is a PROTOTYPE PLACEHOLDER.**

**In production, the actual scam detection uses:**
- `rishi/detectors/linguistic.py` - ML-ready linguistic analysis
- `rishi/detectors/behavioral.py` - Behavioral pattern detection
- `rishi/detectors/link_intel.py` - Infrastructure intelligence
- `rishi/detectors/identity_mismatch.py` - Brand verification
- `rishi/detectors/historical.py` - Threat intelligence integration

---

## 📂 File Structure

```
rishi/honeypot_test_api/
├── __init__.py          # Package initialization
├── app.py               # FastAPI application & endpoint
├── models.py            # Pydantic request/response schemas
├── logic.py             # Stub scoring logic
├── config.py            # Configuration & credentials
└── README.md            # This file
```

---

## 🚫 Isolation & Safety

This module:
- ✅ Runs completely independently
- ✅ Does NOT modify core rishi/ modules
- ✅ Does NOT touch detectors, scoring, or API modules
- ✅ Uses only standard libraries + FastAPI/Pydantic
- ✅ No external API calls or databases
- ✅ No ML models

---

## 🔗 Integration with Main System

When the full system runs (`python main.py`), the honeypot test API is **NOT loaded**. It exists purely for:
- External prototype validation
- Demonstrating API contract compliance
- Testing endpoint availability

The actual honeypot engagement (Person 2 - Saachi) lives in:
- `rishi/honeypot/` - Full honeypot system
- `saachi/` - Saachi's honeypot module

---

## ❓ FAQ

**Q: Why create a separate test API?**  
A: External testers need a minimal, isolated endpoint. This avoids requiring them to set up the full multi-agent system.

**Q: Does this replace the main honeypot system?**  
A: No. This is test-only. The real system lives in `rishi/honeypot/` and `saachi/`.

**Q: How is scoring different from the real system?**  
A: This uses stub scoring based on heuristics. The real system uses ML detectors in `rishi/detectors/`.

**Q: Can I customize the scoring?**  
A: Yes. Edit `logic.py` and adjust the factors in `calculate_scam_probability()`.

**Q: What's the default API key?**  
A: `test-api-key-12345`. Change it in `config.py` or via `HONEYPOT_API_KEY` environment variable.

---

## 📞 Support

For issues or questions:
- Check the example requests above
- Review `app.py` for endpoint logic
- See `logic.py` for scoring details
- Check `models.py` for validation rules
"""
