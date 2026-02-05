from .persona import PERSONAS
from .state_manager import ConversationState, determine_next_state

def handle_scammer_message(
    scammer_message: str,
    current_state: ConversationState,
    persona_key: str
) -> tuple[str, ConversationState]:
    """
    Handles a scammer message by generating a reply and updating the conversation state.
    This function simulates victim responses to keep scammers engaged and extract intelligence.
    """
    # Retrieve the persona to shape the reply based on their characteristics.
    # WHY: Personas provide realistic tone and behavior to believably engage scammers.
    persona = PERSONAS.get(persona_key)
    if not persona:
        # Fallback if persona not found, to avoid errors in demo.
       return "Sorry, I’m a bit confused right now. Can you explain again?", current_state

    # Determine the next state based on the scammer's message.
    # WHY: State transitions simulate victim behavior, allowing strategic engagement and delay.
    next_state = determine_next_state(current_state, scammer_message)

    # Generate a stub reply based on persona and state.
    # WHY: Replies must reflect persona traits (tone, style, hints) to stay in character and waste time.
    reply_text = generate_stub_reply(persona, next_state)

    return reply_text, next_state

def generate_stub_reply(persona, state):
    """
    Generates a stub reply based on persona attributes and conversation state.
    This is a placeholder for actual response generation (no LLM calls here).
    """

    hints = persona.behavioral_hints.split(", ")

    base_reply = f"Hello, this is {persona.name}. "

    if state == ConversationState.INITIAL:
        # WHY: Initial state introduces the persona politely to start engagement.
        reply = base_reply + "How can I help you today?"
    elif state == ConversationState.CONFUSED:
        # WHY: Confused state shows hesitation to delay and express fear, per behavioral hints.
        reply = base_reply + f"I'm a bit confused. {hints[0] if len(hints) > 0 else ''} Can you explain again?"
    elif state == ConversationState.TRUSTING:
        # WHY: Trusting state builds rapport to prolong conversation and extract more info.
        reply = base_reply + "I trust you, but I need to check something first."
    elif state == ConversationState.STALLING:
        # WHY: Stalling delays action to waste scammer's time, using persona's delay hints.
        reply = base_reply + f"I'm busy right now. {hints[1] if len(hints) > 1 else ''} Let's talk later."
    elif state == ConversationState.EXIT:
        # WHY: Exit state ends conversation safely when risks are too high.
        reply = base_reply + "I think I need to go now. Goodbye."
    else:
        reply = base_reply + "I'm not sure what to say."

    # Incorporate persona's tone and style into the reply.
    # WHY: Ensures replies are in-character, making the honeypot believable.
    if "gentle" in persona.tone:
        reply = reply.replace("Hello", "Hello dear")
    elif "professional" in persona.tone:
        reply = reply.replace("Hello", "Good day")
    elif "casual" in persona.tone:
        reply = reply.replace("Hello", "Hey")

    return reply
