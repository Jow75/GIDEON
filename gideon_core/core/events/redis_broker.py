import asyncio
import json
import logging
from typing import Dict, List, Callable, Coroutine
from core.events.models import Event
from core.events.broker import EventBroker
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class RedisBroker(EventBroker):
    """
    Distributed EventBroker using Redis Pub/Sub.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379", node_id: str = "local"):
        self.redis_url = redis_url
        self.node_id = node_id
        self.redis: redis.Redis = None
        self.pubsub: redis.client.PubSub = None
        self.subscribers: Dict[str, List[Callable[[Event], Coroutine]]] = {}
        self._task: asyncio.Task = None

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def start(self) -> None:
        try:
            self.redis = redis.from_url(self.redis_url)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.psubscribe("gideon:*")
            self._task = asyncio.create_task(self._process_events())
            logger.info(f"RedisBroker started on {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to start RedisBroker: {e}")
            raise

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self.pubsub:
            try:
                await self.pubsub.close()
            except Exception:
                pass
            self.pubsub = None
        if self.redis:
            try:
                await self.redis.close()
            except Exception:
                pass
            self.redis = None
        logger.info("RedisBroker stopped.")

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    async def publish(self, event: Event) -> None:
        if not self.redis:
            return
            
        event.node_id = self.node_id
        payload = {
            "type": event.type,
            "source": event.source,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat(),
            "node_id": event.node_id
        }
        await self.redis.publish(f"gideon:{event.type}", json.dumps(payload))
        logger.debug(f"Redis published: {event.type}")

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
        from datetime import datetime
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        data = json.loads(message["data"])
                        # Prevent echoing our own messages if needed, but EventBus semantics
                        # might expect local subscribers to hear local publishes.
                        # We will process all messages here.
                        
                        event = Event(
                            type=data["type"],
                            source=data["source"],
                            payload=data["payload"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            node_id=data.get("node_id", "unknown")
                        )
                        
                        handlers = self.subscribers.get(event.type, [])
                        handlers.extend(self.subscribers.get("*", []))
                        
                        if handlers:
                            tasks = [asyncio.create_task(handler(event)) for handler in handlers]
                            await asyncio.gather(*tasks, return_exceptions=True)
                            
                    except Exception as e:
                        logger.error(f"Error parsing Redis message: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"RedisBroker event loop error: {e}")
