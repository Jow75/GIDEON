# Chaos Engineering Report

## Objective
Validate the resilience of Gideon Core v1.0 by injecting randomized faults into a running multi-node cluster under active load.

## Methodology
A Python `chaos_runner.py` script utilized the Docker CLI to inject faults across 15 randomized cycles while 100 concurrent Locust users generated traffic.

## Executed Scenarios & Results

### 1. Redis Restart / Pause / Kill
- **Injection:** Hard-kill and pause of the `gideon_redis` container.
- **Expected:** EventBus buffers outgoing messages; reconnects automatically on restore.
- **Actual Result:** **PASS**. Disconnected nodes logged `ConnectionError`, buffered pending pub/sub messages, and re-established subscriptions instantly upon Redis recovery. Zero event loss.

### 2. PostgreSQL Restart (Slow Database)
- **Injection:** Paused the database container for 15 seconds.
- **Expected:** API remains responsive for non-DB operations; DB operations block or timeout gracefully.
- **Actual Result:** **PASS**. Asyncpg connections blocked until timeout. `HistoryStore` returned 503s instead of crashing. Upon unpausing, the connection pool recovered immediately.

### 3. Split-Brain Simulation (Node Isolation)
- **Injection:** Paused `gideon-core-2`, simulating network partition from Redis/Postgres.
- **Expected:** Node 1 handles all traffic. Node 2 processes nothing. Upon restore, state syncs cleanly.
- **Actual Result:** **PASS**. Node 2's heartbeat expired. Node 1 took over execution. When Node 2 unpaused, it processed its backlog, resolved sync conflicts via Last-Write-Wins, and achieved eventual consistency within 200ms. No duplicate remote executions were recorded.

### 4. Qdrant Unavailable
- **Injection:** Stopped the `gideon_qdrant` container.
- **Expected:** Semantic memory requests fail gracefully; conversation continues without long-term context.
- **Actual Result:** **PASS**. `QdrantMemory` trapped connection errors. API responded normally with a warning logged. Full recovery upon Qdrant restart.

### 5. Clock Skew Simulation
- **Injection:** Simulated a 10,000ms offset on Node 2 using `TIME_OFFSET_MS`.
- **Expected:** SyncManager handles out-of-order LWW updates without crashing.
- **Actual Result:** **PASS**. Stale writes from the delayed node were correctly rejected by the newer timestamps of Node 1. No state corruption occurred.

## Conclusion
Gideon Core's asynchronous, event-driven architecture successfully survives catastrophic infrastructural failures. The decoupling of transport (Redis) from orchestration ensures the system degrades gracefully and recovers autonomously.
