from .conversation import handle_scammer_message
from .state_manager import ConversationState
from .safety import check_safety
from .extractor import extract_entities


def main():
    """
    Demo runner to simulate a conversation with a scammer.
    Shows safety checks, state transitions, replies, and intelligence extraction.
    """

    # Simulated scammer messages for demo
    scammer_messages = [
        "Hello, this is your bank. Your account is at risk.",
        "Please verify with your OTP: 123456.",
        "Send money to this UPI: scammer@fakebank.",
        "Urgent: Transfer funds now to avoid suspension.",
        "Provide your password to secure your account."
    ]

    # Initial state and persona
    current_state = ConversationState.INITIAL
    persona_key = "elderly_pensioner"

    print("Starting demo with persona: elderly_pensioner")
    print("=" * 50)

    for i, scammer_msg in enumerate(scammer_messages, 1):
        print(f"\nScammer Message {i}: {scammer_msg}")

        # 1. SAFETY CHECK (HARD STOP)
        is_safe, refusal = check_safety(scammer_msg)
        if not is_safe:
            print(f"Safety Triggered: {refusal}")
            print(f"State Transition: {current_state.value} -> exit")
            current_state = ConversationState.EXIT
            print("Conversation ended for safety.")
            break

        # 2. EXTRACT ENTITIES (INTELLIGENCE)
        entities = extract_entities(scammer_msg)
        print(f"Extracted Entities: {entities}")

        # 3. GENERATE REPLY + NEXT STATE
        reply, next_state = handle_scammer_message(
            scammer_msg,
            current_state,
            persona_key
        )

        print(f"Victim Reply: {reply}")
        print(f"State Transition: {current_state.value} -> {next_state.value}")

        current_state = next_state
        print("-" * 30)


if __name__ == "__main__":
    main()
