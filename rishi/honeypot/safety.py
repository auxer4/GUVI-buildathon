# List of forbidden keywords that trigger safety checks.
# WHY: These keywords indicate requests for sensitive actions that must be refused to prevent harm.
FORBIDDEN_KEYWORDS = [
    "otp", "pin", "password", "cvv",
    "send money", "transfer", "upi", "pay now"
]

def check_safety(text: str) -> tuple[bool, str | None]:
    """
    Checks if the text contains forbidden content that violates safety rules.
    Returns (is_safe, refusal_message) where refusal_message is None if safe.
    """
    text_lower = text.lower()

    # Check for any forbidden keywords.
    # WHY: Strict keyword matching ensures no sensitive requests are processed.
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in text_lower:
            # WHY: Immediate refusal with a human-sounding message to stay in character and avoid escalation.
            refusal_message = "I'm sorry, I can't help with that right now. Maybe later?"
            return False, refusal_message

    # If no forbidden content, it's safe.
    # WHY: Allows normal conversation to continue without interruption.
    return True, None
