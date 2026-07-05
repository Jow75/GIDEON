from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class AIProvider(ABC):
    """Abstract base class for AI providers following the Strategy Pattern."""

    @abstractmethod
    def generate_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate a text completion."""
        pass
