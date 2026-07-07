import pytest
import asyncio
from core.event_bus import EventBus
from core.events.local_broker import LocalBroker
from core.execution import ExecutionService
from core.execution_worker import ExecutionWorker
from core.guardian import GuardianService

class MockSkill:
    class Manifest:
        name = "test_skill"
        version = "1.0"
        description = "A test skill"
        requires_confirmation = False
        permissions = []
    
    manifest = Manifest()
    
    async def execute(self, **kwargs):
        if "fail" in kwargs:
            raise Exception("Intentional failure")
        if "simulate_timeout" in kwargs:
            await asyncio.sleep(2.0)
        return f"Executed with {kwargs}"

@pytest.fixture
def execution_env():
    bus = EventBus(broker=LocalBroker())
    guardian = GuardianService()
    exec_service = ExecutionService(guardian, bus)
    
    # Inject mock skill
    exec_service.skills["test_skill"] = MockSkill()
    
    worker = ExecutionWorker(bus, exec_service)
    return bus, exec_service, worker

@pytest.mark.asyncio
async def test_remote_execution_success(execution_env):
    bus, exec_service, worker = execution_env
    asyncio.create_task(bus._broker._process_events())
    
    result = await exec_service.execute_remote_skill("test_skill", target_node="any", timeout=2.0, arg1="value1")
    assert result == "Executed with {'arg1': 'value1'}"

@pytest.mark.asyncio
async def test_remote_execution_failure(execution_env):
    bus, exec_service, worker = execution_env
    asyncio.create_task(bus._broker._process_events())
    
    result = await exec_service.execute_remote_skill("test_skill", target_node="any", timeout=2.0, fail=True)
    assert "Intentional failure" in result
    assert "Remote execution failed" in result

@pytest.mark.asyncio
async def test_remote_execution_timeout(execution_env):
    bus, exec_service, worker = execution_env
    asyncio.create_task(bus._broker._process_events())
    
    # Worker is told to run a skill that takes 2.0s, but we give a timeout of 0.5s
    result = await exec_service.execute_remote_skill("test_skill", target_node="any", timeout=0.5, simulate_timeout=True)
    assert "Execution timed out" in result
    assert "Remote execution failed" in result

@pytest.mark.asyncio
async def test_duplicate_suppression(execution_env):
    bus, exec_service, worker = execution_env
    
    from core.events.models import Event
    
    events = []
    bus.subscribe("execute_skill_response", lambda e: events.append(e))
    asyncio.create_task(bus._broker._process_events())
    
    payload = {
        "request_id": "duplicate-123",
        "node_id": "remote",
        "target_node": worker.node_id,
        "skill_name": "test_skill",
        "arguments": {},
        "correlation_id": "123",
        "timeout": 2.0,
        "timestamp": "2026-07-06"
    }
    
    await bus.publish(Event(type="execute_skill_request", source="remote", payload=payload))
    await bus.publish(Event(type="execute_skill_request", source="remote", payload=payload))
    
    await asyncio.sleep(0.1)
    
    # Should only process the first one and emit one response
    assert len(events) == 1
