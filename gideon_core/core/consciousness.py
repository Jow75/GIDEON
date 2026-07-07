import logging
from memory.sqlite_history import SQLiteHistory
from memory.base import HistoryStore, LongTermMemoryStore
from memory.long_term import ChromaMemory
from orchestration.router import AIOperationsRouter
from orchestration.commander import CommanderAgent
from core.execution import ExecutionService
from core.event_bus import EventBus
from core.events.models import Event
from core.events.redis_broker import RedisBroker
from config.settings import settings
from core.device_monitor import DeviceMonitor
from core.guardian import GuardianService
from core.execution_worker import ExecutionWorker
from core.execution_worker import ExecutionWorker
from core.learning import LearningService
from providers.base import Message
from typing import Dict, Any
from core.sync_manager import SyncManager

logger = logging.getLogger(__name__)

class SystemConsciousness:
    """
    The Orchestration Layer of Gideon.
    Not an LLM itself, but the central nervous system that coordinates
    state, missions, memory, and specialized services via the Event Bus.
    """
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        
        # 1. Initialize Services
        if settings.event_broker_type == "redis":
            broker = RedisBroker(redis_url=settings.redis_url, node_id=settings.node_id)
            self.event_bus = EventBus(broker=broker)
            logger.info("Initialized RedisBroker for EventBus.")
        else:
            self.event_bus = EventBus()
            logger.info("Initialized LocalBroker for EventBus.")
            
        self.guardian = GuardianService()
        
        if settings.environment == "production":
            from memory.postgres_history import PostgresHistory
            from memory.qdrant_memory import QdrantMemory
            self.history: HistoryStore = PostgresHistory()
            self.ltm: LongTermMemoryStore = QdrantMemory()
            logger.info("Initialized PostgresHistory and QdrantMemory for production.")
        else:
            self.history: HistoryStore = SQLiteHistory()
            self.ltm: LongTermMemoryStore = ChromaMemory()
            logger.info("Initialized SQLiteHistory and ChromaMemory for development.")
        self.execution = ExecutionService(self.guardian, self.event_bus)
        self.execution_worker = ExecutionWorker(self.event_bus, self.execution)
        
        # 2. Initialize Agents
        self.router = AIOperationsRouter()
        self.commander = CommanderAgent(self.router, self.execution)
        self.device_monitor = DeviceMonitor(self.event_bus)
        self.learning = LearningService(self.event_bus, self.ltm, self.router)
        
        # 3. World State via SyncManager
        self.sync_manager = SyncManager(self.event_bus, initial_state={
            "Time": "Unknown",
            "Active Mission": "None",
            "Current Device": "Unknown",
            "Device_Telemetry": {}
        })
        
        self._register_subscriptions()

    @property
    def world_state(self):
        return self.sync_manager.world_state

    def _register_subscriptions(self):
        """Subscribe to all major events for global orchestration."""
        self.event_bus.subscribe("device_telemetry", self._on_device_telemetry)
        self.event_bus.subscribe("user_input", self._on_user_input)
        self.event_bus.subscribe("system_alert", self._on_system_alert)

    def start_services(self):
        """Boot up all background loops."""
        self.event_bus.start()
        self.device_monitor.start()
        self.execution_worker.start()

    async def initialize(self):
        """Ensure critical components (like database pools) are fully initialized before serving traffic."""
        if hasattr(self.history, "initialize"):
            await self.history.initialize()
        if hasattr(self.ltm, "initialize"):
            await self.ltm.initialize()

    async def stop(self):
        """Deterministically shutdown resources safely to avoid leaks.

        Each phase is independently guarded so that a failure in one
        phase does not prevent subsequent resources from being cleaned up.
        """
        errors = []

        # 1. Stop EventBus (stops new requests)
        try:
            await self.event_bus.stop()
        except Exception as e:
            logger.error(f"Error stopping EventBus: {e}", exc_info=True)
            errors.append(e)

        # 2. Stop DeviceMonitor background task
        try:
            if hasattr(self, "device_monitor") and hasattr(self.device_monitor, "stop"):
                await self.device_monitor.stop()
        except Exception as e:
            logger.error(f"Error stopping DeviceMonitor: {e}", exc_info=True)
            errors.append(e)

        # 3. Stop ExecutionWorker heartbeat task
        try:
            if hasattr(self, "execution_worker") and hasattr(self.execution_worker, "stop"):
                await self.execution_worker.stop()
        except Exception as e:
            logger.error(f"Error stopping ExecutionWorker: {e}", exc_info=True)
            errors.append(e)

        # 4. Close HistoryStore
        try:
            if hasattr(self.history, "stop"):
                await self.history.stop()
        except Exception as e:
            logger.error(f"Error stopping HistoryStore: {e}", exc_info=True)
            errors.append(e)

        # 5. Close LongTermMemory
        try:
            if hasattr(self.ltm, "stop"):
                await self.ltm.stop()
        except Exception as e:
            logger.error(f"Error stopping LongTermMemory: {e}", exc_info=True)
            errors.append(e)

        if errors:
            raise RuntimeError(
                f"Shutdown completed with {len(errors)} error(s): "
                + "; ".join(str(e) for e in errors)
            )

    async def _on_device_telemetry(self, event: Event):
        """Maintain global world state from hardware."""
        await self.sync_manager.update_state("Device_Telemetry", event.payload)

    async def _on_system_alert(self, event: Event):
        """Handle urgent system alerts by notifying the user or taking corrective action."""
        logger.warning(f"System Alert: {event.payload}")
        await self.history.add_message(self.session_id, "system", f"ALERT: {event.payload}")

    async def _on_user_input(self, event: Event):
        """Orchestrate the processing of incoming user instructions via the event bus."""
        user_input = event.payload
        await self.process_input(user_input)

    async def process_input(self, user_input: str) -> str:
        """Entry point for testing, publishes to event bus and awaits response (simplified for synchronous CLI)."""
        # In a fully asynchronous web/socket layer, this would just publish and return.
        # For our CLI/API interface, we orchestrate it directly here to return a string.
        
        if not self.guardian.scan_prompt_injection(user_input):
            return "Guardian Intervention: Input violates safety parameters."

        await self.history.add_message(self.session_id, "user", user_input)

        # 1. Decide if memory retrieval is needed
        relevant_memories = []
        try:
            relevant_memories = await self.ltm.retrieve_relevant_experiences(user_input)
        except Exception as e:
            logger.warning(f"LTM Retrieval Failed: {e}")

        system_prompt = f"""You are Gideon.
World State: {self.world_state}
Relevant Memories: {relevant_memories}
Use your capabilities to assist the user. Maintain your professional persona."""

        messages = [Message(role="system", content=system_prompt)]
        history_context = await self.history.get_context(self.session_id)
        messages.extend(history_context)

        try:
            # 2. Dispatch work to specialized service (Commander)
            # In the future, this might dispatch to Planner or Researcher depending on the intent
            response = await self.commander.process(messages)
            
            # 3. Decide if memory should be updated
            # A background learning service could do this, but for now we commit successful interactions
            await self.history.add_message(self.session_id, "assistant", response)
            
            return response
        except Exception as e:
            logger.error(f"Execution Error: {e}", exc_info=True)
            return f"System Error: {str(e)}"

    async def store_experience(self, text: str):
        try:
            await self.ltm.store_experience(text, {"source": "user_instruction"})
            return "Experience stored successfully."
        except Exception as e:
            return f"Failed to store experience: {e}"
