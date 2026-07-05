from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Skill(ABC):
    """Abstract base class representing a capability Gideon can learn and use."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the skill."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the skill does, provided to the LLM."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema format describing the required parameters."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Executes the skill and returns the result as a string."""
        pass
