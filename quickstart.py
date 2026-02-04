#!/usr/bin/env python3
"""
QUICK START GUIDE - Scam Intelligence Engine (Rishi Module)

This script helps you get started with the system.
Run: python quickstart.py
"""

import sys
from pathlib import Path


def print_header(title):
    """Print formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_section(title):
    """Print section header."""
    print(f"\n🔷 {title}")
    print("-" * 70)


def check_requirements():
    """Check if required packages are installed."""
    print_section("Checking Requirements")

    required = ["fastapi", "pydantic", "yaml"]
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"  pip install -r requirements.txt\n")
        return False

    print("\n✅ All requirements met!")
    return True


def show_file_structure():
    """Show the created file structure."""
    print_section("File Structure Created")

    structure = """
rishi/                          ← Your scam detection module
├── detectors/                  ← 5 independent detectors
│   ├── linguistic.py
│   ├── behavioral.py
│   ├── link_intel.py
│   ├── identity_mismatch.py
│   └── historical.py
├── scoring/
│   └── risk_fusion.py          ← Weighted fusion engine
├── api/
│   └── detect.py               ← FastAPI endpoint
├── schemas/
│   └── events.py               ← Pydantic models
├── config/
│   └── thresholds.yaml         ← Configuration (no hardcoding!)
└── README.md                   ← Full documentation

shared/                         ← Inter-agent communication
├── event_bus.py
├── message_models.py
└── constants.py
    """
    print(structure)


def show_quick_commands():
    """Show quick commands to get started."""
    print_section("Quick Commands")

    commands = {
        "Run the application": "python main.py",
        "Run example scenarios": "python example_scenarios.py",
        "View API docs": "Open http://localhost:8000/docs",
        "Install dependencies": "pip install -r requirements.txt",
        "Run with auto-reload": "uvicorn main:app --reload",
    }

    for desc, cmd in commands.items():
        print(f"📌 {desc}:")
        print(f"   $ {cmd}\n")


def show_usage_example():
    """Show a simple usage example."""
    print_section("Simple Usage Example")

    code = '''
from rishi.schemas.events import (
    ScamDetectionInput, ConversationMessage, SenderMetadata
)
from datetime import datetime

# Create a test message
messages = [
    ConversationMessage(
        message_id="msg1",
        sender="attacker",
        content="URGENT! Click here to verify your account!",
        timestamp=datetime.utcnow()
    )
]

# Create sender info
sender = SenderMetadata(
    user_id="user_123",
    account_age_days=2,
    verification_status="unverified"
)

# Create input
input_data = ScamDetectionInput(
    conversation_id="conv_1",
    messages=messages,
    sender_metadata=sender
)

# Run detection (via FastAPI)
# POST /detect-scam
    '''
    print(code)


def show_next_steps():
    """Show next steps."""
    print_section("Next Steps")

    steps = [
        ("1. Install Dependencies", "pip install -r requirements.txt"),
        ("2. Run Application", "python main.py"),
        ("3. Open API Docs", "http://localhost:8000/docs"),
        ("4. Try Examples", "python example_scenarios.py"),
        ("5. Read Documentation", "cat rishi/README.md"),
        ("6. Explore Architecture", "cat ARCHITECTURE.md"),
    ]

    for step, action in steps:
        print(f"\n{step}")
        print(f"   → {action}")


def show_detector_info():
    """Show information about detectors."""
    print_section("5 Independent Detectors")

    detectors = {
        "Linguistic Detector": {
            "detects": [
                "Urgency tactics (immediate, urgent, limited time)",
                "Fear appeals (locked account, suspicious activity)",
                "Authority impersonation (FBI, Microsoft, Apple)",
                "Reward baiting (won prize, free money)",
            ],
            "weight": "30%",
        },
        "Behavioral Detector": {
            "detects": [
                "High message frequency (< 2 min between messages)",
                "Instruction repetition (same message 3+ times)",
                "Script rigidity (ignoring user questions)",
                "Pressure tactics (act now, don't delay)",
            ],
            "weight": "25%",
        },
        "Link Intelligence Detector": {
            "detects": [
                "Domain age (< 30 days = risky)",
                "Suspicious TLDs (.tk, .ml, .ga, .cf)",
                "Lookalike domains (amaz0n.com vs amazon.com)",
                "URL entropy (high randomness = obfuscation)",
            ],
            "weight": "20%",
        },
        "Identity Mismatch Detector": {
            "detects": [
                "Brand impersonation (Apple claim + attacker domain)",
                "Credential anomalies (new account, claims authority)",
                "Contradictory claims (different identities)",
                "Signature inconsistency (multiple signatures)",
            ],
            "weight": "15%",
        },
        "Historical Pattern Detector": {
            "detects": [
                "Known bad actors (future: event_bus integration)",
                "Historical scam patterns (TODO)",
                "Threat intelligence (TODO)",
            ],
            "weight": "10%",
        },
    }

    for name, info in detectors.items():
        print(f"\n{name} ({info['weight']}):")
        for detect in info["detects"]:
            print(f"  • {detect}")


def show_api_endpoints():
    """Show available API endpoints."""
    print_section("API Endpoints")

    endpoints = {
        "POST /detect-scam": {
            "description": "Main detection endpoint",
            "input": "conversation_id, messages, sender_metadata",
            "output": "scam_probability, risk_level, breakdown, handoff_triggered",
        },
        "GET /health": {
            "description": "Health check",
            "input": "none",
            "output": "{status: healthy}",
        },
        "GET /system/info": {
            "description": "System information",
            "input": "none",
            "output": "System and module status",
        },
        "GET /docs": {
            "description": "Interactive API documentation (Swagger)",
            "input": "none",
            "output": "Browser UI",
        },
    }

    for endpoint, info in endpoints.items():
        print(f"\n{endpoint}")
        print(f"  Description: {info['description']}")
        print(f"  Input: {info['input']}")
        print(f"  Output: {info['output']}")


def show_risk_levels():
    """Show risk level information."""
    print_section("Risk Levels & Scoring")

    levels = [
        ("SAFE", "0-29", "✅ No action needed"),
        ("SUSPICIOUS", "30-69", "⚠️  Monitor / Alert user"),
        ("HIGH", "70-84", "🚨 Escalate"),
        ("CONFIRMED", "85-100", "🛑 Trigger handoff to honeypot"),
    ]

    print("\nRisk Level  |  Score Range  |  Action")
    print("-" * 60)
    for level, score, action in levels:
        print(f"{level:12}|  {score:12}  |  {action}")


def show_documentation():
    """Show documentation files."""
    print_section("📚 Documentation Files")

    docs = {
        "rishi/README.md": "Complete module documentation",
        "ARCHITECTURE.md": "System design and data flows",
        "SUMMARY.md": "Implementation summary",
        "IMPLEMENTATION_COMPLETE.md": "Detailed guide",
        "CHECKLIST.md": "Requirements checklist",
        "example_scenarios.py": "5 real-world test scenarios",
    }

    for file, desc in docs.items():
        print(f"\n📄 {file}")
        print(f"   → {desc}")


def show_configuration():
    """Show configuration information."""
    print_section("🔧 Configuration")

    print("""
The system is configured via: rishi/config/thresholds.yaml

Key configurations:

1. DETECTOR WEIGHTS (customize in YAML)
   • Linguistic: 30%
   • Behavioral: 25%
   • Link/Infra: 20%
   • Identity: 15%
   • Historical: 10%

2. RISK THRESHOLDS (customize in YAML)
   • Safe: 0-29
   • Suspicious: 30-69
   • High: 70-84
   • Confirmed: 85-100

3. NO HARDCODING
   • All weights configurable
   • All thresholds tunable
   • No entity names hardcoded
   • Change behavior without code changes
    """)


def main():
    """Main function."""
    print_header("🎯 SCAM INTELLIGENCE ENGINE - QUICK START")

    print("""
Welcome to the Scam Intelligence Engine (Rishi Module)!

This is a bank-grade fraud detection system designed for:
✅ Multi-agent hackathon projects
✅ Production deployment
✅ Easy integration with other services
✅ ML model integration

Let's get you started!
    """)

    show_detector_info()
    show_risk_levels()
    show_api_endpoints()
    show_file_structure()
    show_configuration()
    show_quick_commands()
    show_documentation()
    show_next_steps()

    print_header("🚀 YOU'RE READY!")

    print("""
Next: Run these commands to get started

  1. pip install -r requirements.txt
  2. python main.py
  3. Open http://localhost:8000/docs

Questions? Check rishi/README.md for comprehensive documentation.

Good luck! 🎉
    """)


if __name__ == "__main__":
    main()
