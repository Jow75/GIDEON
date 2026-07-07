import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from core.event_bus import EventBus
from core.events.local_broker import LocalBroker
from core.sync_manager import SyncManager, StateMetadata

@pytest.fixture
def sync_manager():
    bus = EventBus(broker=LocalBroker())
    manager = SyncManager(bus)
    return manager, bus

@pytest.mark.asyncio
async def test_update_state_broadcasts(sync_manager):
    manager, bus = sync_manager
    
    events = []
    def handler(e):
        events.append(e)
        
    bus.subscribe("state_sync", handler)
    asyncio.create_task(bus._broker._process_events()) # Start local queue worker for testing
    
    await manager.update_state("test_key", "test_value")
    
    # Wait for propagation
    await asyncio.sleep(0.01)
    
    assert manager.world_state["test_key"] == "test_value"
    assert len(events) == 1
    assert events[0].payload["key"] == "test_key"
    assert events[0].payload["value"] == "test_value"

@pytest.mark.asyncio
async def test_lww_conflict_resolution(sync_manager):
    manager, bus = sync_manager
    asyncio.create_task(bus._broker._process_events())
    
    # Set local state
    await manager.update_state("key", "local_val")
    await asyncio.sleep(0.01)
    
    local_meta = manager.metadata["key"]
    
    # Create an incoming event with an OLDER timestamp (conflict, should be rejected)
    older_time = local_meta.timestamp - timedelta(seconds=10)
    
    older_meta = StateMetadata(
        node_id="remote_node",
        cluster_id="default",
        timestamp=older_time,
        version=1,
        event_id="old_event"
    )
    
    from core.events.models import Event
    await bus.publish(Event(
        type="state_sync",
        source="remote_node",
        payload={
            "key": "key",
            "value": "remote_val",
            "metadata": older_meta.model_dump(mode="json")
        }
    ))
    
    await asyncio.sleep(0.01)
    
    # Local value should remain
    assert manager.world_state["key"] == "local_val"
    
    # Create an incoming event with a NEWER timestamp (should be accepted)
    newer_time = local_meta.timestamp + timedelta(seconds=10)
    newer_meta = StateMetadata(
        node_id="remote_node",
        cluster_id="default",
        timestamp=newer_time,
        version=2,
        event_id="new_event"
    )
    
    await bus.publish(Event(
        type="state_sync",
        source="remote_node",
        payload={
            "key": "key",
            "value": "remote_val_new",
            "metadata": newer_meta.model_dump(mode="json")
        }
    ))
    
    await asyncio.sleep(0.01)
    
    assert manager.world_state["key"] == "remote_val_new"
