from typing import List
from pydantic import BaseModel
from providers.base import Message

class ConversationHistory:
    """Manages short-term conversation context for the active session."""
    def __init__(self, max_messages: int = 20):
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        self.messages.append(Message(role="user", content=content))
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append(Message(role="assistant", content=content))
        self._trim()

    def get_context(self) -> List[Message]:
        return self.messages.copy()

    def _trim(self):
        """Keep only the most recent max_messages."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self):
        self.messages = []
