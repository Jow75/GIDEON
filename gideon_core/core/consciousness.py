from memory.history import ConversationHistory
from memory.long_term import LongTermMemory
from orchestration.router import AIOperationsRouter
from orchestration.commander import CommanderAgent
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
        self.commander = CommanderAgent(self.router)
        self.ltm = LongTermMemory()

        # World State (Mocked for Phase 1/2)
        self.world_state = {
            "Current Device": "CLI Terminal",
            "Battery": "100%",
            "Active Mission": "None"
        }

    def process_input(self, user_input: str) -> str:
        self.history.add_user_message(user_input)

        relevant_memories = []
        try:
            relevant_memories = self.ltm.retrieve_relevant_experiences(user_input)
        except Exception as e:
            print(f"[Warning: LTM Retrieval Failed: {e}]")

        memory_context = ""
        if relevant_memories:
            memory_context = "\nRelevant Past Experiences:\n" + "\n".join([f"- {m}" for m in relevant_memories])

        state_str = "\n".join([f"{k}: {v}" for k, v in self.world_state.items()])
        system_prompt = f"""You are Gideon, a highly intelligent and unified digital partner.
Current System State:
{state_str}
{memory_context}

Use your capabilities to assist the user. Maintain your professional and concise persona."""

        messages = [Message(role="system", content=system_prompt)]
        messages.extend(self.history.get_context())

        try:
            # Delegate to Commander instead of routing directly
            response = self.commander.process(messages)
            self.history.add_assistant_message(response)
            return response
        except Exception as e:
            return f"System Error: {str(e)}"

    def store_experience(self, text: str):
        try:
            self.ltm.store_experience(text, {"source": "user_instruction"})
            return "Experience stored successfully."
        except Exception as e:
            return f"Failed to store experience: {e}"
