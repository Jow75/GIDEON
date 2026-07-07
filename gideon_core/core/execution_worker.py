import logging
import uuid
from typing import Dict, Any, Optional
import time
from datetime import datetime, timezone
import asyncio
from core.event_bus import EventBus, Event
from core.execution import ExecutionService
from config.settings import settings

logger = logging.getLogger(__name__)

class ExecutionWorker:
    """
    Subscribes to execute_skill_request events and invokes the local ExecutionService.
    Ensures idempotency, timeouts, and publishes responses.
    """
    def __init__(self, event_bus: EventBus, execution_service: ExecutionService):
        self.event_bus = event_bus
        self.execution = execution_service
        self.node_id = settings.node_id
        
        # Idempotency tracking (request_id -> timestamp)
        self._processed_requests: Dict[str, float] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        self.event_bus.subscribe("execute_skill_request", self._handle_execution_request)

    async def _heartbeat_loop(self):
        while True:
            try:
                await self.event_bus.publish(Event(
                    type="node_heartbeat",
                    source=self.node_id,
                    payload={
                        "gideon_version": "1.0.0",
                        "protocol_version": "1.0",
                        "api_version": "v1",
                        "capabilities": {
                            "screen_capture": {"version": 2},
                            "voice": {"version": 1},
                            "vision": {"version": 3},
                            "desktop": "windows",
                            "gpu": "cuda" if settings.nvidia_api_key else "none",
                            "models": ["llama", "whisper"]
                        }
                    }
                ))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
            await asyncio.sleep(30)

    def start(self):
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("ExecutionWorker heartbeat started.")

    async def stop(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    def _clean_idempotency_cache(self):
        """Removes old request tracking to prevent memory leaks."""
        current_time = time.time()
        # Keep tracking for 1 hour
        self._processed_requests = {
            req_id: ts for req_id, ts in self._processed_requests.items()
            if current_time - ts < 3600
        }

    async def _handle_execution_request(self, event: Event):
        payload = event.payload
        target_node = payload.get("target_node")
        
        if target_node != "any" and target_node != self.node_id:
            return
            
        request_id = payload.get("request_id")
        if not request_id:
            return
            
        # Idempotency check
        if request_id in self._processed_requests:
            logger.debug(f"Duplicate request suppressed: {request_id}")
            return
            
        self._processed_requests[request_id] = time.time()
        self._clean_idempotency_cache()
        
        skill_name = payload.get("skill_name")
        arguments = payload.get("arguments", {})
        timeout = payload.get("timeout", 30.0)
        requester_node = event.source
        
        logger.info(f"Worker {self.node_id} starting remote execution of {skill_name}")
        start_time = time.time()
        
        try:
            # Enforce timeout for the skill execution
            result = await asyncio.wait_for(
                self.execution.execute_skill(skill_name, **arguments),
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if isinstance(result, str) and result.startswith("[Error"):
                # Guardian blocked it or local error
                await self.event_bus.publish(Event(
                    type="execute_skill_failed",
                    source=self.node_id,
                    payload={
                        "request_id": request_id,
                        "execution_status": "failed",
                        "execution_duration": duration,
                        "failure_reason": result,
                        "target_node": requester_node
                    }
                ))
            else:
                await self.event_bus.publish(Event(
                    type="execute_skill_response",
                    source=self.node_id,
                    payload={
                        "request_id": request_id,
                        "execution_status": "success",
                        "execution_duration": duration,
                        "returned_data": result,
                        "target_node": requester_node
                    }
                ))
                
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.warning(f"Skill {skill_name} execution timed out after {duration}s")
            await self.event_bus.publish(Event(
                type="execute_skill_timeout",
                source=self.node_id,
                payload={
                    "request_id": request_id,
                    "execution_status": "timeout",
                    "execution_duration": duration,
                    "failure_reason": f"Execution timed out after {timeout} seconds",
                    "target_node": requester_node
                }
            ))
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"ExecutionWorker error for {skill_name}: {e}", exc_info=True)
            await self.event_bus.publish(Event(
                type="execute_skill_failed",
                source=self.node_id,
                payload={
                    "request_id": request_id,
                    "execution_status": "failed",
                    "execution_duration": duration,
                    "failure_reason": str(e),
                    "target_node": requester_node
                }
            ))
