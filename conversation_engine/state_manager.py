from enum import Enum

class ConversationState(Enum):
    INITIAL = "initial"
    CONFUSED = "confused"
    TRUSTING = "trusting"
    STALLING = "stalling"
    EXIT = "exit"

def determine_next_state(
    current_state: ConversationState,
    scammer_message: str
) -> ConversationState:
    """
    Determines the next conversation state based on the current state and scammer message.
    Uses simple keyword-based heuristics to simulate realistic victim behavior transitions.
    """
    message_lower = scammer_message.lower()

    # Keywords for heuristics
    urgency_keywords = ["urgent", "now", "immediately", "quick", "fast"]
    payment_keywords = ["pay", "transfer", "send money", "bank", "account"]
    credential_keywords = ["password", "otp", "pin", "cvv", "login"]

    has_urgency = any(keyword in message_lower for keyword in urgency_keywords)
    has_payment = any(keyword in message_lower for keyword in payment_keywords)
    has_credentials = any(keyword in message_lower for keyword in credential_keywords)

    if current_state == ConversationState.INITIAL:
        if has_urgency:
            # Transition to CONFUSED: Victim shows confusion when faced with urgent requests to delay and engage.
            return ConversationState.CONFUSED
        elif has_payment:
            # Transition to TRUSTING: Initial trust building when payment is mentioned, to keep scammer engaged.
            return ConversationState.TRUSTING
        else:
            # Stay in INITIAL: No strong triggers, maintain starting state.
            return ConversationState.INITIAL

    elif current_state == ConversationState.CONFUSED:
        if has_credentials:
            # Transition to EXIT: Request for credentials triggers safety exit to avoid harm.
            return ConversationState.EXIT
        elif has_urgency:
            # Transition to STALLING: More urgency causes victim to stall further, wasting time.
            return ConversationState.STALLING
        else:
            # Stay in CONFUSED: Continue showing confusion to prolong engagement.
            return ConversationState.CONFUSED

    elif current_state == ConversationState.TRUSTING:
        if has_credentials:
            # Transition to EXIT: Credentials request overrides trust, exit for safety.
            return ConversationState.EXIT
        elif has_urgency:
            # Transition to STALLING: Urgency in trusting phase leads to stalling tactics.
            return ConversationState.STALLING
        else:
            # Stay in TRUSTING: Maintain trust to extract more intelligence.
            return ConversationState.TRUSTING

    elif current_state == ConversationState.STALLING:
        if has_credentials:
            # Transition to EXIT: Credentials are a hard stop for safety.
            return ConversationState.EXIT
        else:
            # Stay in STALLING: Continue stalling to waste scammer's time.
            return ConversationState.STALLING

    elif current_state == ConversationState.EXIT:
        # Once in EXIT, stay there to end the conversation safely.
        return ConversationState.EXIT

    # Default fallback
    return current_state
