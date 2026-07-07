# Changelog

All notable changes to Gideon Core are documented in this file.

---

## [1.0.0] - 2026-07-07

### Summary

First stable release of Gideon Core. The stabilization period focused on resolving lifecycle correctness issues identified during independent release auditing: startup determinism, shutdown resource ownership, async race conditions, and test reliability. No public APIs, protocols, or schemas changed.

---

### Blocking Issues Resolved

#### Startup Fail-Fast on PostgreSQL Unavailability
**File:** `memory/postgres_history.py`

`PostgresHistory.initialize()` previously caught all exceptions and logged them without re-raising, allowing the server to start with `self.pool = None` and silently discard writes. The exception is now re-raised, propagating through `SystemConsciousness.initialize()` into the FastAPI lifespan, which aborts startup before accepting traffic.

#### SQLite Initialization Race Condition Eliminated
**File:** `memory/sqlite_history.py`

`SQLiteHistory.__init__()` previously called `asyncio.create_task(self._init_db())`. If `add_message()` was called before the task ran, the schema would not yet exist. The floating task has been removed. A new `async def initialize()` awaits schema creation deterministically before traffic is accepted.

#### Shutdown Exception Isolation
**File:** `core/consciousness.py`

`SystemConsciousness.stop()` previously executed shutdown phases sequentially without error handling. A failure in one phase skipped all subsequent ones, leaking connection pools. Each phase is now independently guarded in `try/except`. All phases always execute, and errors are accumulated into a single final `RuntimeError`.

#### RedisBroker Idempotent Shutdown
**File:** `core/events/redis_broker.py`

`RedisBroker.stop()` was not idempotent; repeated calls raised on already-closed resources. Each resource is now guarded, closed in `try/except`, and nullified. Repeated calls to `stop()` are safe.

#### CLI Always Cleans Up Resources
**File:** `main.py`

The CLI entrypoint never called `await gideon.stop()` on exit. `initialize()` is now awaited after construction, and `stop()` is always called in a `finally` block covering normal exit, `KeyboardInterrupt`, and exceptions, including initialization failures.

#### Lifecycle Hooks in Storage ABCs
**File:** `memory/base.py`

`HistoryStore` and `LongTermMemoryStore` now provide concrete no-op `initialize()` and `stop()` methods. The change is additive and fully backward-compatible with all existing subclasses.

---

### Improvements

#### Complete Background Task Ownership in Shutdown
**File:** `core/consciousness.py`

`stop()` now includes `device_monitor.stop()` and `execution_worker.stop()` as independently-isolated phases. All five owned components are deterministically stopped: EventBus, DeviceMonitor, ExecutionWorker, HistoryStore, LongTermMemory.

#### Explicit Error on Uninitialized Postgres Writes
**File:** `memory/postgres_history.py`

`add_message()` now raises `RuntimeError` with a logged error when `pool is None`, instead of silently returning and discarding the write.

#### WebSocket Subscription Cleanup
**File:** `api.py`

WebSocket handlers now call `event_bus.unsubscribe("*", event_handler)` in their `finally` block on disconnect, preventing unbounded subscriber list growth.

#### Deterministic Throughput Tests
**File:** `tests/test_load_and_throughput.py`

Replaced arbitrary `asyncio.sleep(N)` waits with `asyncio.wait_for(queue.join(), timeout=5.0)`, eliminating intermittent failures under CPU load.

---

### New Test Coverage

**File:** `tests/test_lifecycle.py` (new, 25 tests across 10 classes)

Covers all blocking findings with regression-preventing tests for exception propagation, schema ordering, race prevention, double-stop safety, partial-failure isolation, startup ordering, and ABC hook presence.

---

### Test Suite Results

`
71 passed, 1 skipped (qdrant_client not installed), 0 failed
`

---

### Frozen Contract Compliance

EventBus protocol, JWT contract, Skill Manifest, HistoryStore interface, LongTermMemoryStore interface, Remote execution protocol, SyncManager event format, Database migration strategy, and Node heartbeat schema were independently verified as unchanged.

---

### Known Limitations

- Guardian prompt injection scanner uses a keyword blocklist (full LLM-guard integration planned).
- Rate limiting is per-process when Redis is not configured (not enforced across replicas).
- LocalBroker queue is unbounded (production path uses RedisBroker).

---

## [Unreleased]

_(Next entries go here)_
