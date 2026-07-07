# API Reference

## Authentication

### `POST /api/auth`
Generates a JWT for the requesting device.
**Payload:**
```json
{
  "device_id": "string"
}
```
**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

## Core Operations

### `POST /api/chat`
Submit a message to Gideon.
**Headers:** `Authorization: Bearer <token>`
**Payload:**
```json
{
  "message": "string"
}
```
**Response:**
```json
{
  "response": "string",
  "skills_executed": ["string"]
}
```

### `POST /api/sync`
Fetches the current global world state.
**Headers:** `Authorization: Bearer <token>`
**Payload:**
```json
{
  "device_id": "string",
  "last_sync_timestamp": "float (optional)"
}
```
**Response:**
```json
{
  "status": "success",
  "world_state": {}
}
```

---

## Telemetry & WebSockets

### `GET /api/ws?token=<token>`
Establishes a WebSocket connection for real-time telemetry and streamed responses.
- Receives events of type: `SYSTEM_READY`, `SKILL_STARTED`, `SKILL_COMPLETED`.

---

## Health & Diagnostics

### `GET /health`
Returns 200 if the HTTP server is running.

### `GET /liveness`
Identical to `/health`, used by Kubernetes liveness probes.

### `GET /readiness`
Returns 200 only if the API can successfully communicate with Redis and PostgreSQL.
