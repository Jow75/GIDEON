# Operational Runbook

## Core Services Overview
- **Gideon Core:** The primary API and orchestration service (FastAPI).
- **Redis:** Used for EventBus pub/sub, heartbeat, and distributed rate limiting.
- **PostgreSQL:** Persistent relational store for Conversation History.
- **Qdrant:** Persistent vector store for Long-Term Memory (Experiences).

## Common Operational Tasks

### 1. Scaling Nodes
To scale the cluster, simply add more instances of `gideon-core` pointing to the same Redis and PostgreSQL instances.
Ensure each node has a unique `NODE_ID` environment variable.
```bash
docker-compose up -d --scale gideon-core=3
```

### 2. Database Migrations
Currently, the `PostgresHistory` adapter auto-initializes the `messages` table if it does not exist.
For complex schema changes in the future, Alembic should be utilized.
```bash
# Future Alembic command
alembic upgrade head
```

### 3. Monitoring Health
Query the health endpoints exposed on every node:
- **Liveness:** `GET /liveness` (Returns 200 OK immediately if API is running)
- **Readiness:** `GET /readiness` (Returns 200 OK only if DB and Redis connections are established)

### 4. Backups
**PostgreSQL Backup:**
```bash
docker exec gideon_postgres pg_dump -U gideon gideon_db > backup.sql
```
**Qdrant Snapshot:**
Use the Qdrant snapshot API to backup vectors:
```bash
curl -X POST http://localhost:6333/collections/gideon_experiences/snapshots
```

## Troubleshooting Guide

### Issue: Node is dropping off the cluster (Heartbeat Failure)
**Symptoms:** Logs show "Node X heartbeat expired."
**Resolution:** Check CPU utilization on the affected node. If the event loop is blocked by synchronous CPU-bound operations, heartbeats will fail. Ensure all custom Skills use `async def` or are explicitly offloaded to thread pools.

### Issue: Rate Limits Exceeded (HTTP 429)
**Symptoms:** Legitimate traffic is blocked with 429 errors.
**Resolution:** The default limit is `60/minute`. Update `LIMITS_DEFAULT` in the environment configuration and restart the nodes.

### Issue: State Synchronization Conflicts
**Symptoms:** `logger.debug("Conflict detected for X. Local timestamp is newer. Ignoring incoming.")`
**Resolution:** This is normal and indicates the LWW (Last-Write-Wins) resolution is working. If this happens excessively, verify that server clocks are tightly synchronized via NTP across all nodes.
