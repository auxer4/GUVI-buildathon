"""
Configuration for Honeypot Test API

This module stores API configuration, credentials, and thresholds.
"""

import os
from typing import Optional

# API Authentication
# In production, this should come from environment variables
HONEYPOT_API_KEY: str = os.getenv("HONEYPOT_API_KEY", "test-api-key-12345")

# Honeypot Configuration
HONEYPOT_ENABLED: bool = True
SCAM_THRESHOLD_FOR_HANDOFF: int = 80  # Score >= 80 triggers handoff

# Service Configuration
SERVICE_NAME: str = "Honeypot Test API"
SERVICE_VERSION: str = "1.0.0"

# Feature Flags
ALLOW_DEBUG_LOGGING: bool = os.getenv("DEBUG", "false").lower() == "true"
