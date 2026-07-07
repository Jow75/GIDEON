"""
RC1 Validation Suite — VP2: EventBus Throughput Test
Verifies that the LocalBroker can process a high volume of events without
dropping messages, corrupting state, or degrading performance.
"""
import pytest
import asyncio
import time
from core.event_bus import EventBus
from core.events.local_broker import LocalBroker
from core.events.models import Event


@pytest.mark.asyncio
async def test_eventbus_high_throughput():
    """Publish 1000 events and verify all are delivered to subscribers."""
    bus = EventBus(broker=LocalBroker())
    asyncio.create_task(bus._broker._process_events())

    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe("throughput_test", handler)

    count = 1000
    start = time.perf_counter()

    for i in range(count):
        await bus.publish(Event(
            type="throughput_test",
            source="load_test",
            payload={"index": i}
        ))

    # Allow propagation — the LocalBroker processes asynchronously
    await asyncio.wait_for(bus._broker._queue.join(), timeout=5.0)

    elapsed = time.perf_counter() - start

    assert len(received) == count, f"Expected {count} events, received {len(received)}"
    print(f"\n[THROUGHPUT] {count} events in {elapsed:.3f}s = {count/elapsed:.0f} events/sec")


@pytest.mark.asyncio
async def test_eventbus_wildcard_throughput():
    """Verify wildcard subscribers receive all event types under load."""
    bus = EventBus(broker=LocalBroker())
    asyncio.create_task(bus._broker._process_events())

    received = []

    async def wildcard_handler(event: Event):
        received.append(event)

    bus.subscribe("*", wildcard_handler)

    event_types = ["type_a", "type_b", "type_c"]
    per_type = 100
    total = len(event_types) * per_type

    for etype in event_types:
        for i in range(per_type):
            await bus.publish(Event(
                type=etype,
                source="load_test",
                payload={"index": i}
            ))

    await asyncio.wait_for(bus._broker._queue.join(), timeout=5.0)

    assert len(received) == total, f"Wildcard: expected {total}, got {len(received)}"


@pytest.mark.asyncio
async def test_eventbus_concurrent_publishers():
    """Multiple concurrent publishers should not lose or corrupt events."""
    bus = EventBus(broker=LocalBroker())
    asyncio.create_task(bus._broker._process_events())

    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe("concurrent_test", handler)

    async def publisher(publisher_id: int, count: int):
        for i in range(count):
            await bus.publish(Event(
                type="concurrent_test",
                source=f"publisher_{publisher_id}",
                payload={"publisher": publisher_id, "index": i}
            ))

    num_publishers = 10
    events_per_publisher = 50
    total_expected = num_publishers * events_per_publisher

    tasks = [publisher(pid, events_per_publisher) for pid in range(num_publishers)]
    await asyncio.gather(*tasks)

    await asyncio.wait_for(bus._broker._queue.join(), timeout=5.0)

    assert len(received) == total_expected, \
        f"Concurrent: expected {total_expected}, got {len(received)}"

    # Verify no duplicate payloads
    seen = set()
    for event in received:
        key = (event.source, event.payload["index"])
        assert key not in seen, f"Duplicate event detected: {key}"
        seen.add(key)


@pytest.mark.asyncio
async def test_sync_manager_under_rapid_updates():
    """SyncManager should handle rapid sequential state updates without corruption."""
    from core.sync_manager import SyncManager

    bus = EventBus(broker=LocalBroker())
    asyncio.create_task(bus._broker._process_events())
    manager = SyncManager(bus)

    update_count = 200
    for i in range(update_count):
        await manager.update_state("counter", i)

    await asyncio.wait_for(bus._broker._queue.join(), timeout=5.0)

    # Final state should reflect the last update
    assert manager.world_state["counter"] == update_count - 1
