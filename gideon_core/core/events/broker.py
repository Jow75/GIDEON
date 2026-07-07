from abc import ABC, abstractmethod
from typing import Callable, Coroutine
from core.events.models import Event

class EventBroker(ABC):
    """
    Abstract interface for EventBus transport backends.
    Implementations handle the actual routing of messages.
    """
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event to the transport."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        """Register a handler for a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        """Remove a handler from an event type."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Initialize the connection and start processing events."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully close the transport connection."""
        pass
