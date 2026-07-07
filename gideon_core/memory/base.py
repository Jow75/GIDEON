from abc import ABC, abstractmethod
from typing import List
from providers.base import Message

class HistoryStore(ABC):
    """
    Abstract interface for conversational history persistence.
    Allows decoupling from SQLite for distributed deployments.
    """
    
    @abstractmethod
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append a message to the history."""
        pass

    @abstractmethod
    async def get_context(self, session_id: str, limit: int = 20) -> List[Message]:
        """Retrieve recent messages for context."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all messages (useful for tests or hard resets)."""
        pass

    async def initialize(self) -> None:
        """Lifecycle hook: called before the store receives requests.

        Subclasses that require async setup (e.g. connection pools)
        should override this method.  The default is a no-op.
        """
        pass

    async def stop(self) -> None:
        """Lifecycle hook: called during graceful shutdown.

        Subclasses that hold open connections should override this
        method to release them.  The default is a no-op.
        """
        pass

class LongTermMemoryStore(ABC):
    """
    Abstract interface for persistent embeddings and semantic retrieval.
    Allows decoupling from ChromaDB/Qdrant.
    """
    
    @abstractmethod
    async def store_experience(self, text: str, metadata: dict = None) -> str:
        """Stores a new experience in long-term memory. Returns document ID."""
        pass

    @abstractmethod
    async def retrieve_relevant_experiences(self, query: str, n_results: int = 3, filter_metadata: dict = None) -> List[str]:
        """Retrieves experiences semantically similar to the query."""
        pass

    async def initialize(self) -> None:
        """Lifecycle hook: called before the store receives requests.

        Subclasses that require async setup should override this method.
        The default is a no-op.
        """
        pass

    async def stop(self) -> None:
        """Lifecycle hook: called during graceful shutdown.

        Subclasses that hold open connections should override this
        method to release them.  The default is a no-op.
        """
        pass

