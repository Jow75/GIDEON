import asyncio
from typing import Dict, Any
from core.event_bus import EventBus, Event
from core.os.factory import get_os
import logging

logger = logging.getLogger(__name__)

class DeviceMonitor:
    """
    Monitors Windows OS telemetry (CPU, RAM, Disk) and publishes to EventBus.
    """
    def __init__(self, bus: EventBus, poll_interval: int = 5):
        self.bus = bus
        self.poll_interval = poll_interval
        self.os_interface = get_os()
        self._task = None

    async def _monitor_loop(self):
        while True:
            try:
                stats = self.get_system_stats()
                event = Event(
                    type="device_telemetry",
                    source="device_monitor",
                    payload=stats
                )
                await self.bus.publish(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"DeviceMonitor error: {e}")
            
            await asyncio.sleep(self.poll_interval)

    def get_system_stats(self) -> Dict[str, Any]:
        """Collect current system telemetry."""
        return self.os_interface.get_telemetry()

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._monitor_loop())
            logger.info("DeviceMonitor started.")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("DeviceMonitor stopped.")
