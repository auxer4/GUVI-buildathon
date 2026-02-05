# Scam Detection Service (Person 2)

This service analyzes incoming messages and determines scam risk.

## Endpoint
POST /detect

## Input
{
  "message": "Your account is blocked! Click here"
}

## Output
{
  "risk_score": 75,
  "decision": "handoff_to_honeypot",
  "features": {...}
}
