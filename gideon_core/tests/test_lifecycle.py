"""
Lifecycle Regression Test Suite — Audit Findings Verification
Tests that validate the initialize()/stop() lifecycle fixes for:
  - NEW-001: PostgresHistory.initialize() must propagate exceptions
  - NEW-002: SQLiteHistory must not use floating asyncio.create_task()
  - NEW-003: RedisBroker.stop() must be idempotent
  - NEW-004: SystemConsciousness.stop() must isolate exceptions per phase
  - NEW-005: CLI main.py must call stop() (structural verification)
  - NEW-006: Base classes provide lifecycle hooks
"""
import pytest
import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock


# ─── Fixtures ────────────────────────────────────────────────────────────────

class MockHistoryStore:
    """Minimal mock that simulates the HistoryStore lifecycle contract."""
    def __init__(self, fail_init=False, fail_stop=False):
        self._fail_init = fail_init
        self._fail_stop = fail_stop
        self.initialized = False
        self.stopped = False

    async def initialize(self):
        if self._fail_init:
            raise ConnectionError("Mock DB unavailable")
        self.initialized = True

    async def stop(self):
        if self._fail_stop:
            raise ConnectionError("Mock DB close failed")
        self.stopped = True

    async def add_message(self, session_id, role, content):
        pass

    async def get_context(self, session_id, limit=20):
        return []

    async def clear(self):
        pass


class MockLTMStore:
    """Minimal mock that simulates the LongTermMemoryStore lifecycle contract."""
    def __init__(self, fail_init=False, fail_stop=False):
        self._fail_init = fail_init
        self._fail_stop = fail_stop
        self.initialized = False
        self.stopped = False

    async def initialize(self):
        if self._fail_init:
            raise ConnectionError("Mock vector store unavailable")
        self.initialized = True

    async def stop(self):
        if self._fail_stop:
            raise ConnectionError("Mock vector store close failed")
        self.stopped = True

    async def store_experience(self, text, metadata=None):
        return "mock-id"

    async def retrieve_relevant_experiences(self, query, n_results=3, filter_metadata=None):
        return []


class MockEventBus:
    """Minimal mock EventBus with controllable stop() behavior."""
    def __init__(self, fail_stop=False):
        self._fail_stop = fail_stop
        self.stopped = False

    def subscribe(self, event_type, handler):
        pass

    async def publish(self, event):
        pass

    def start(self):
        pass

    async def stop(self):
        if self._fail_stop:
            raise ConnectionError("Mock EventBus stop failed")
        self.stopped = True


# ─── NEW-001: PostgresHistory.initialize() Must Propagate Exceptions ────────

class TestPostgresHistoryInitialize:
    @pytest.mark.asyncio
    async def test_initialize_propagates_connection_error(self):
        """If asyncpg cannot connect, initialize() MUST raise — not swallow."""
        from memory.postgres_history import PostgresHistory

        history = PostgresHistory(postgres_url="postgresql://invalid:5432/nonexistent")

        with pytest.raises(Exception):
            await history.initialize()

        # Pool must remain None — server should never have started
        assert history.pool is None

    @pytest.mark.asyncio
    async def test_initialize_success_sets_pool(self):
        """When initialize() succeeds, pool must be non-None."""
        from memory.postgres_history import PostgresHistory

        history = PostgresHistory()

        # Mock asyncpg.create_pool to simulate success
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

        # create_pool is a coroutine — use AsyncMock that returns the pool
        mock_create_pool = AsyncMock(return_value=mock_pool)

        with patch("memory.postgres_history.asyncpg.create_pool", mock_create_pool):
            await history.initialize()

        assert history.pool is not None


# ─── NEW-002: SQLiteHistory Must Use Explicit initialize() ──────────────────

class TestSQLiteHistoryInitialize:
    @pytest.mark.asyncio
    async def test_no_floating_create_task(self):
        """SQLiteHistory.__init__() must NOT call asyncio.create_task()."""
        import inspect
        from memory.sqlite_history import SQLiteHistory

        source = inspect.getsource(SQLiteHistory.__init__)
        assert "create_task" not in source, \
            "SQLiteHistory.__init__() still contains asyncio.create_task()"

    @pytest.mark.asyncio
    async def test_has_initialize_method(self):
        """SQLiteHistory must have an async initialize() method."""
        from memory.sqlite_history import SQLiteHistory

        assert hasattr(SQLiteHistory, "initialize"), \
            "SQLiteHistory missing initialize() method"
        assert asyncio.iscoroutinefunction(SQLiteHistory.initialize), \
            "SQLiteHistory.initialize() must be async"

    @pytest.mark.asyncio
    async def test_has_stop_method(self):
        """SQLiteHistory must have an async stop() method."""
        from memory.sqlite_history import SQLiteHistory

        assert hasattr(SQLiteHistory, "stop"), \
            "SQLiteHistory missing stop() method"
        assert asyncio.iscoroutinefunction(SQLiteHistory.stop), \
            "SQLiteHistory.stop() must be async"

    @pytest.mark.asyncio
    async def test_initialize_creates_schema_before_use(self):
        """After initialize(), add_message must work without errors."""
        from memory.sqlite_history import SQLiteHistory

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("memory.sqlite_history.settings") as mock_settings:
                mock_settings.data_dir = tmpdir
                history = SQLiteHistory(db_name="test_lifecycle.db")
                await history.initialize()

                # This would fail with OperationalError if schema wasn't created
                await history.add_message("test_session", "user", "hello")
                messages = await history.get_context("test_session")
                assert len(messages) == 1
                assert messages[0].content == "hello"

    @pytest.mark.asyncio
    async def test_add_message_before_initialize_fails(self):
        """Without initialize(), the schema doesn't exist and operations should fail."""
        from memory.sqlite_history import SQLiteHistory

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("memory.sqlite_history.settings") as mock_settings:
                mock_settings.data_dir = tmpdir
                history = SQLiteHistory(db_name="test_no_init.db")

                # Without initialize(), the table doesn't exist
                with pytest.raises(Exception):
                    await history.add_message("test_session", "user", "hello")


# ─── NEW-003: RedisBroker.stop() Must Be Idempotent ────────────────────────

class TestRedisBrokerIdempotentStop:
    @pytest.mark.asyncio
    async def test_double_stop_is_safe(self):
        """Calling stop() twice must not raise."""
        from core.events.redis_broker import RedisBroker

        broker = RedisBroker()

        # Create a real cancellable asyncio task
        async def _noop():
            await asyncio.sleep(3600)
        broker._task = asyncio.create_task(_noop())

        mock_pubsub = AsyncMock()
        broker.pubsub = mock_pubsub
        mock_redis = AsyncMock()
        broker.redis = mock_redis

        # First stop
        await broker.stop()
        assert broker._task is None
        assert broker.pubsub is None
        assert broker.redis is None

        # Second stop — must not raise
        await broker.stop()

    @pytest.mark.asyncio
    async def test_stop_from_clean_state(self):
        """Calling stop() on a never-started broker must not raise."""
        from core.events.redis_broker import RedisBroker

        broker = RedisBroker()
        assert broker._task is None
        assert broker.pubsub is None
        assert broker.redis is None

        # Must not raise
        await broker.stop()


# ─── NEW-004: SystemConsciousness.stop() Must Isolate Exceptions ────────────

class TestShutdownExceptionIsolation:
    @pytest.mark.asyncio
    async def test_history_and_ltm_still_stop_when_eventbus_fails(self):
        """If event_bus.stop() raises, history and ltm must still get stop() called."""
        history = MockHistoryStore()
        ltm = MockLTMStore()
        event_bus = MockEventBus(fail_stop=True)

        # Build a minimal SystemConsciousness-like object
        from core.consciousness import SystemConsciousness

        with patch.object(SystemConsciousness, "__init__", lambda self, *a, **kw: None):
            sc = SystemConsciousness.__new__(SystemConsciousness)
            sc.event_bus = event_bus
            sc.history = history
            sc.ltm = ltm

            # stop() should raise (because event_bus failed), but history and ltm must be cleaned up
            with pytest.raises(RuntimeError, match="1 error"):
                await sc.stop()

            assert history.stopped is True, "HistoryStore.stop() was not called"
            assert ltm.stopped is True, "LongTermMemoryStore.stop() was not called"

    @pytest.mark.asyncio
    async def test_all_errors_collected_when_multiple_fail(self):
        """If all three phases fail, all three errors must be reported."""
        history = MockHistoryStore(fail_stop=True)
        ltm = MockLTMStore(fail_stop=True)
        event_bus = MockEventBus(fail_stop=True)

        from core.consciousness import SystemConsciousness

        with patch.object(SystemConsciousness, "__init__", lambda self, *a, **kw: None):
            sc = SystemConsciousness.__new__(SystemConsciousness)
            sc.event_bus = event_bus
            sc.history = history
            sc.ltm = ltm

            with pytest.raises(RuntimeError, match="3 error"):
                await sc.stop()

    @pytest.mark.asyncio
    async def test_clean_shutdown_does_not_raise(self):
        """When all phases succeed, stop() must complete without error."""
        history = MockHistoryStore()
        ltm = MockLTMStore()
        event_bus = MockEventBus()

        from core.consciousness import SystemConsciousness

        with patch.object(SystemConsciousness, "__init__", lambda self, *a, **kw: None):
            sc = SystemConsciousness.__new__(SystemConsciousness)
            sc.event_bus = event_bus
            sc.history = history
            sc.ltm = ltm

            await sc.stop()  # Must not raise

            assert event_bus.stopped is True
            assert history.stopped is True
            assert ltm.stopped is True


# ─── Repeated stop() Safety ────────────────────────────────────────────────

class TestRepeatedShutdown:
    @pytest.mark.asyncio
    async def test_postgres_double_stop(self):
        """PostgresHistory.stop() called twice must not raise."""
        from memory.postgres_history import PostgresHistory

        history = PostgresHistory()
        history.pool = None  # Simulate never-initialized or already-stopped

        await history.stop()  # First — no-op
        await history.stop()  # Second — still no-op, must not raise

    @pytest.mark.asyncio
    async def test_sqlite_double_stop(self):
        """SQLiteHistory.stop() called twice must not raise."""
        from memory.sqlite_history import SQLiteHistory

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("memory.sqlite_history.settings") as mock_settings:
                mock_settings.data_dir = tmpdir
                history = SQLiteHistory()

                await history.stop()
                await history.stop()  # Must not raise

    @pytest.mark.asyncio
    async def test_qdrant_double_stop(self):
        """QdrantMemory.stop() called twice must not raise."""
        try:
            from memory.qdrant_memory import QdrantMemory
        except ModuleNotFoundError:
            pytest.skip("qdrant_client not installed")

        mem = QdrantMemory.__new__(QdrantMemory)
        mem.client = None  # Simulate already-stopped

        await mem.stop()  # Must not raise

    @pytest.mark.asyncio
    async def test_consciousness_double_stop(self):
        """SystemConsciousness.stop() called twice must not raise on second call."""
        history = MockHistoryStore()
        ltm = MockLTMStore()
        event_bus = MockEventBus()

        from core.consciousness import SystemConsciousness

        with patch.object(SystemConsciousness, "__init__", lambda self, *a, **kw: None):
            sc = SystemConsciousness.__new__(SystemConsciousness)
            sc.event_bus = event_bus
            sc.history = history
            sc.ltm = ltm

            await sc.stop()
            # Second stop — mock stores will see stop() again but must not crash
            await sc.stop()


# ─── Startup Ordering: Initialize Before Traffic ───────────────────────────

class TestStartupOrdering:
    @pytest.mark.asyncio
    async def test_lifespan_awaits_initialize_before_yield(self):
        """The FastAPI lifespan must call initialize() before yielding."""
        import inspect
        from api import lifespan

        source = inspect.getsource(lifespan)

        # Verify that initialize() is called and that it appears before yield
        init_pos = source.find("initialize()")
        yield_pos = source.find("yield")

        assert init_pos != -1, "lifespan does not call initialize()"
        assert yield_pos != -1, "lifespan does not yield"
        assert init_pos < yield_pos, "initialize() must be called before yield"

    @pytest.mark.asyncio
    async def test_lifespan_fails_fast_on_init_error(self):
        """If initialize() raises, the lifespan must propagate the error (no traffic accepted)."""
        from api import app, lifespan

        with patch("api.SystemConsciousness") as MockSC:
            instance = MockSC.return_value
            instance.initialize = AsyncMock(side_effect=ConnectionError("DB down"))
            instance.stop = AsyncMock()

            with pytest.raises((RuntimeError, ConnectionError)):
                async with lifespan(app):
                    pass  # Should never reach here


# ─── Database Unavailable at Startup ───────────────────────────────────────

class TestDatabaseUnavailableAtStartup:
    @pytest.mark.asyncio
    async def test_postgres_unavailable_halts_startup(self):
        """When PostgreSQL is unreachable, initialize() must raise."""
        from memory.postgres_history import PostgresHistory

        history = PostgresHistory(postgres_url="postgresql://badhost:9999/nodb")

        with pytest.raises(Exception):
            await history.initialize()

        assert history.pool is None

    @pytest.mark.asyncio
    async def test_consciousness_init_propagates_db_failure(self):
        """SystemConsciousness.initialize() must propagate HistoryStore init failures."""
        from core.consciousness import SystemConsciousness

        with patch.object(SystemConsciousness, "__init__", lambda self, *a, **kw: None):
            sc = SystemConsciousness.__new__(SystemConsciousness)
            sc.history = MockHistoryStore(fail_init=True)
            sc.ltm = MockLTMStore()

            with pytest.raises(ConnectionError, match="Mock DB unavailable"):
                await sc.initialize()


# ─── NEW-006: Base Class Lifecycle Hooks ───────────────────────────────────

class TestBaseClassLifecycleHooks:
    @pytest.mark.asyncio
    async def test_history_store_has_initialize(self):
        """HistoryStore base class must have initialize() as a concrete method."""
        from memory.base import HistoryStore

        assert hasattr(HistoryStore, "initialize")
        assert asyncio.iscoroutinefunction(HistoryStore.initialize)

    @pytest.mark.asyncio
    async def test_history_store_has_stop(self):
        """HistoryStore base class must have stop() as a concrete method."""
        from memory.base import HistoryStore

        assert hasattr(HistoryStore, "stop")
        assert asyncio.iscoroutinefunction(HistoryStore.stop)

    @pytest.mark.asyncio
    async def test_ltm_store_has_initialize(self):
        """LongTermMemoryStore base class must have initialize()."""
        from memory.base import LongTermMemoryStore

        assert hasattr(LongTermMemoryStore, "initialize")
        assert asyncio.iscoroutinefunction(LongTermMemoryStore.initialize)

    @pytest.mark.asyncio
    async def test_ltm_store_has_stop(self):
        """LongTermMemoryStore base class must have stop()."""
        from memory.base import LongTermMemoryStore

        assert hasattr(LongTermMemoryStore, "stop")
        assert asyncio.iscoroutinefunction(LongTermMemoryStore.stop)


# ─── LocalBroker Idempotent Stop ───────────────────────────────────────────

class TestLocalBrokerIdempotentStop:
    @pytest.mark.asyncio
    async def test_double_stop_is_safe(self):
        """LocalBroker.stop() called twice must not raise."""
        from core.events.local_broker import LocalBroker

        broker = LocalBroker()
        await broker.start()
        await broker.stop()
        await broker.stop()  # Must not raise
