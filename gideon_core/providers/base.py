from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class AIProvider(ABC):
    """Abstract base class for AI providers following the Strategy Pattern."""

    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate a text completion."""

    @abstractmethod
    async def generate_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
