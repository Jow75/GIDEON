from abc import ABC, abstractmethod
from typing import Dict, Any

class Skill(ABC):
    """Abstract base class representing a capability Gideon can learn and use."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the skill."""

    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the skill does, provided to the LLM."""

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema format describing the required parameters."""

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Executes the skill and returns the result as a string."""
