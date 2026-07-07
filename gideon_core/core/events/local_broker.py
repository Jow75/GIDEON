import asyncio
import logging
from typing import Dict, List, Callable, Coroutine
from core.events.models import Event
from core.events.broker import EventBroker

logger = logging.getLogger(__name__)

class LocalBroker(EventBroker):
    """
    In-memory, single-node EventBroker using asyncio.Queue.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Event], Coroutine]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._task: asyncio.Task = None

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        if handler not in self.subscribers[event_type]:
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        if event_type in self.subscribers:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]

    async def _process_events(self):
        while True:
            try:
                event: Event = await self._queue.get()
            except asyncio.CancelledError:
                break
            try:
                handlers = self.subscribers.get(event.type, [])
                handlers.extend(self.subscribers.get("*", []))

                if handlers:
                    tasks = [asyncio.create_task(handler(event)) for handler in handlers]
                    await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"LocalBroker error processing event {event}: {e}")
            finally:
                self._queue.task_done()

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._process_events())
            logger.info("LocalBroker started.")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("LocalBroker stopped.")
