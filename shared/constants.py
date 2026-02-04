"""
Shared Constants used across the Scam Intelligence Engine.
"""

# Event Types
EVENT_SCAM_DETECTED = "SCAM_DETECTED"
EVENT_SCAM_CONFIRMED = "SCAM_CONFIRMED"
EVENT_HONEYPOT_ENGAGED = "HONEYPOT_ENGAGED"
EVENT_RECOVERY_INITIATED = "RECOVERY_INITIATED"

# Risk Levels
RISK_SAFE = "safe"
RISK_SUSPICIOUS = "suspicious"
RISK_HIGH = "high"
RISK_CONFIRMED = "confirmed"

# Scam Types
SCAM_TYPE_PHISHING = "phishing"
SCAM_TYPE_IMPERSONATION = "impersonation"
SCAM_TYPE_SOCIAL_ENGINEERING = "social_engineering"
SCAM_TYPE_ROMANCE = "romance_or_advance_fee"
SCAM_TYPE_TECH_SUPPORT = "tech_support"
SCAM_TYPE_UNKNOWN = "unknown"

# Detector Names
DETECTOR_LINGUISTIC = "linguistic"
DETECTOR_BEHAVIORAL = "behavioral"
DETECTOR_LINK_INFRASTRUCTURE = "link_infrastructure"
DETECTOR_IDENTITY_MISMATCH = "identity_mismatch"
DETECTOR_HISTORICAL = "historical"

# Service Names
SERVICE_SCAM_DETECTION = "scam_detection"
SERVICE_HONEYPOT = "honeypot"
SERVICE_RECOVERY = "recovery"

# Thresholds (0-100 scale)
THRESHOLD_SAFE = 0
THRESHOLD_SUSPICIOUS = 30
THRESHOLD_HIGH = 70
THRESHOLD_CONFIRMED = 85
