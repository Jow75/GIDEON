from memory.history import ConversationHistory
from orchestration.router import AIOperationsRouter
from providers.base import Message
from typing import List

class SystemConsciousness:
    """
    The top-level interface that maintains continuous awareness of user goals,
    context, and system state before delegating to specific agents.
    """
    def __init__(self):
        self.history = ConversationHistory()
        self.router = AIOperationsRouter()

        # World State (Mocked for Phase 1)
        self.world_state = {
            "Current Device": "CLI Terminal",
            "Battery": "100%",
            "Active Mission": "None"
        }

    def process_input(self, user_input: str) -> str:
        # Add user input to short term memory
        self.history.add_user_message(user_input)

        # Build the injected context prompt
        state_str = "\n".join([f"{k}: {v}" for k, v in self.world_state.items()])
        system_prompt = f"""You are Gideon, a highly intelligent and unified digital partner.
Current System State:
{state_str}

Use your capabilities to assist the user. Maintain your professional and concise persona."""

        # Prepare messages for routing
        messages = [Message(role="system", content=system_prompt)]
        messages.extend(self.history.get_context())

        # Route to Commander (General reasoning)
        try:
            response = self.router.execute_task(required_tags=["commander"], messages=messages)
            self.history.add_assistant_message(response)
            return response
        except Exception as e:
            return f"System Error: {str(e)}"
