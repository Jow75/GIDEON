# EventBus Specification

The EventBus is the primary mechanism for asynchronous inter-node and intra-node communication in Gideon Core v1.0.

## Message Format

All events published to the EventBus MUST adhere to the following schema:

```json
{
  "id": "uuid-string",
  "type": "string (The Event Type)",
  "source": "string (Originating Node ID or Agent Name)",
  "payload": {},
  "timestamp": "ISO-8601 string"
}
```

## Standard Event Types

### `CHAT_REQUEST`
Fired when a user submits a chat message.
- **Payload:** `{"user_id": "...", "message": "..."}`

### `SKILL_EXECUTION_REQUEST`
Fired by the Commander when a skill should be executed.
- **Payload:** `{"request_id": "...", "skill_name": "...", "arguments": {}}`

### `SKILL_EXECUTION_RESPONSE`
Fired by an Execution Worker when a skill finishes.
- **Payload:** `{"request_id": "...", "result": {}}`

### `STATE_UPDATE`
Fired by the `SyncManager` to broadcast a state delta to the cluster.
- **Payload:** `{"key": "...", "value": "...", "metadata": {"node_id": "...", "version": int, "timestamp": "..."}}`

### `HEARTBEAT`
Fired periodically by all active nodes to advertise presence and capabilities.
- **Payload:** `{"node_id": "...", "capabilities": ["..."]}`

## Transport Details
- **Local:** Python `asyncio.Queue`. Does not cross process boundaries.
- **Redis:** Redis Pub/Sub. Topics map directly to `Event.type`. Events are JSON serialized.
