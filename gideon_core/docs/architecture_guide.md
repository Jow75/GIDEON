# Gideon Core — Architecture Guide

## Overview

Gideon is a persistent AI operating layer composed of specialized internal services that cooperate through an asynchronous, event-driven architecture. It is **not** a single LLM with tools — it is a modular platform where each service runs independently, communicates through an EventBus, and can be upgraded without affecting others.

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  FastAPI (REST + WebSocket + Health Probes)              │
│  Rate Limiting (slowapi) · JWT Auth · Audit Logging      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               SystemConsciousness                        │
│  Central orchestrator. Owns session, routes to services. │
│  Coordinates: Commander, Planner, Execution, Memory.     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     EventBus                             │
│  Transport-agnostic pub/sub.                             │
│  Backends: LocalBroker (dev) · RedisBroker (prod)        │
└────────────┬───────────┬───────────┬────────────────────┘
             │           │           │
     ┌───────▼──┐  ┌─────▼────┐  ┌──▼──────────┐
     │ Device   │  │ Sync     │  │ Execution   │
     │ Monitor  │  │ Manager  │  │ Worker      │
     └──────────┘  └──────────┘  └─────────────┘
```

## Service Inventory

| Service | Module | Purpose |
|---|---|---|
| SystemConsciousness | `core/consciousness.py` | Central coordinator. Maintains world state, session context, and routes user input. |
| EventBus | `core/event_bus.py` | Transport-agnostic async pub/sub. Decouples all services. |
| LocalBroker | `core/events/local_broker.py` | In-process `asyncio.Queue` broker for development. |
| RedisBroker | `core/events/redis_broker.py` | Distributed Redis Pub/Sub broker for production. |
| SyncManager | `core/sync_manager.py` | Distributed world_state synchronization with LWW conflict resolution. |
| ExecutionService | `core/execution.py` | Skill discovery, validation, and local execution. |
| ExecutionWorker | `core/execution_worker.py` | Listens for remote `execute_skill_request` events and delegates to ExecutionService. |
| Guardian | `core/guardian.py` | Permission enforcement, prompt injection scanning, and audit logging. |
| DeviceMonitor | `core/device_monitor.py` | Collects system telemetry (CPU, RAM, disk) via the OS abstraction layer. |
| AuthManager | `core/auth.py` | JWT generation, verification, and session management. |
| HistoryStore | `memory/base.py` | Abstract persistence interface for conversation history. |
| SQLiteHistory | `memory/sqlite_history.py` | Async SQLite implementation for development. |
| PostgresHistory | `memory/postgres_history.py` | Async PostgreSQL implementation for production. |
| LongTermMemory | `memory/long_term.py` | ChromaDB/Qdrant vector store for semantic experience retrieval. |
| LearningService | `core/learning.py` | Post-task self-evaluation and workflow recording. |
| OS Abstraction | `core/os/` | Cross-platform OS interface with Windows, Linux, and macOS providers. |

## Key Design Principles

1. **Transport Agnosticism**: The EventBus is completely unaware of transport details. All services publish and subscribe through the same interface regardless of whether the backend is an in-memory queue or Redis.

2. **Persistence Abstraction**: All services depend on the `HistoryStore` interface, never on SQLite or PostgreSQL directly. Backend selection is configuration-driven.

3. **Capability-Driven Execution**: Skills declare capabilities and permissions. The Guardian validates every execution request before it proceeds.

4. **Eventual Consistency**: Distributed state uses Last-Write-Wins (LWW) with nanosecond-precision timestamps and deterministic node_id tiebreakers.

5. **Fail Fast**: Production deployments validate all configuration at startup and refuse to boot with invalid or missing critical settings.

## Authentication Flow

```
Client → POST /api/auth/token → JWT (access_token)
Client → GET /api/sync (Authorization: Bearer <token>) → Verified
Client → WS /ws?token=<token> → Authenticated WebSocket
```

## Environment Configuration

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` or `production` |
| `EVENT_BROKER_TYPE` | `local` | `local` or `redis` |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `POSTGRES_URL` | `postgresql://gideon:...@localhost:5432/gideon_db` | PostgreSQL connection string |
| `GIDEON_JWT_SECRET` | (default) | **Must be changed in production** |
| `DISABLE_AUTH_FOR_DEV` | `false` | Bypass auth for local development |
