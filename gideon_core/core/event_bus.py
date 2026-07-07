import asyncio
import logging
from typing import Callable, Coroutine
from core.events.models import Event
from core.events.broker import EventBroker
from core.events.local_broker import LocalBroker

logger = logging.getLogger(__name__)

class EventBus:
    """
    Transport-agnostic asynchronous Publish-Subscribe Event Bus.
    Allows decoupled communication between Gideon's microservices.
    """
    def __init__(self, broker: EventBroker = None):
        if broker is None:
            self._broker = LocalBroker()
        else:
            self._broker = broker

    def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]):
        """Register an async handler for a specific event type."""
        self._broker.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe a handler from an event type."""
        self._broker.unsubscribe(event_type, handler)

    async def publish(self, event: Event):
        """Publish an event to the bus."""
        await self._broker.publish(event)

    def start(self):
        """Start the event processing loop in the background."""
        import asyncio
        asyncio.create_task(self._broker.start())
        logger.info("EventBus started using transport: " + self._broker.__class__.__name__)

    async def stop(self):
        """Stop the event processing loop."""
        await self._broker.stop()
        logger.info("EventBus stopped.")
