# Architecture Overview

Gideon Core is a distributed, event-driven orchestration platform designed to power intelligent agentic workflows, long-term memory retrieval, and scalable remote execution.

## Core Components

### 1. SystemConsciousness
The initialization and dependency injection root. It evaluates the `ENVIRONMENT` configuration and wires the appropriate transport, persistence, and memory backends (e.g., Local vs Redis, SQLite vs Postgres).

### 2. EventBus
The nervous system of the platform. All communication between nodes, agents, and workers occurs over the EventBus.
- **LocalBroker:** Used for single-node development (Python `asyncio.Queue`).
- **RedisBroker:** Used for multi-node production (Redis Pub/Sub).

### 3. SyncManager
Maintains the `world_state` across all nodes in a cluster. Uses a Last-Write-Wins (LWW) mechanism backed by logical timestamps and node UUIDs to resolve concurrent mutations without distributed locks.

### 4. AIOperationsRouter & CommanderAgent
The "brain" of the operation. Routes incoming requests to LLM providers (e.g., NVIDIA), parses JSON function calls, and orchestrates the multi-step execution loop.

### 5. ExecutionService & ExecutionWorker
- **ExecutionService:** Evaluates and runs local Python skills in isolated processes or thread pools.
- **ExecutionWorker:** Subscribes to the EventBus to pick up remote execution requests. Allows the cluster to delegate heavy compute skills to dedicated worker nodes.

### 6. Persistence & Memory
- **HistoryStore:** Relational storage of exact conversation messages (`PostgresHistory`).
- **LongTermMemoryStore:** Vector storage of semantic experiences (`QdrantMemory`).

## Request Flow
1. User authenticates via JWT.
2. User submits a request via REST or WebSocket.
3. The API publishes a `CHAT_REQUEST` event to the EventBus.
4. The CommanderAgent intercepts the event, fetches context from `HistoryStore` and `QdrantMemory`.
5. The LLM suggests a Skill.
6. The CommanderAgent publishes a `SKILL_EXECUTION_REQUEST`.
7. An `ExecutionWorker` picks up the request, validates it against `Guardian`, runs the code, and publishes a `SKILL_EXECUTION_RESPONSE`.
8. The CommanderAgent evaluates the result and publishes a `STATE_UPDATE`.
9. `SyncManager` applies the state locally and broadcasts a delta.
10. The result is returned to the user via WebSocket or REST response.
