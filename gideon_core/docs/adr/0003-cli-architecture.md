# 3. CLI Architecture

## Status
Accepted

## Context
Operators and developers need tooling to manage the Gideon cluster. Monitoring Redis directly via `redis-cli` or making raw `curl` calls to FastAPI is inefficient. A dedicated Command Line Interface (CLI) is necessary to streamline common operational workflows like checking cluster status, inspecting events, and deploying new skills.

## Options Considered
1. **Direct Redis Interaction:** The CLI connects directly to the Redis EventBus to fetch topology and events.
2. **REST API Wrapper:** The CLI communicates strictly over HTTP to the `gideon-core` API.

## Decision
We will build the `gideon` CLI using `Typer` (or `Click`). The CLI will act strictly as an HTTP client communicating with the `gideon-core` Commander API. It will not communicate directly with Redis or PostgreSQL. This preserves the security boundaries enforced by the `Guardian` service and JWT authentication.

Commands will include:
- `gideon cluster status`
- `gideon deploy <skill>`
- `gideon events stream`

## Consequences
- **Positive:** Security boundaries are respected. RBAC and JWT validation apply universally to CLI operations.
- **Positive:** The CLI remains lightweight and decoupled from the backend storage engines.
- **Negative:** Features like `events stream` require the Commander API to expose dedicated diagnostic endpoints (which requires additional backend work).
