# 6. EventBus Inspection Tooling

## Status
Accepted

## Context
Debugging distributed, asynchronous events across a cluster is fundamentally difficult. When an ExecutionWorker fails to receive a `SKILL_EXECUTION_REQUEST`, operators need a way to determine if the event was never published, dropped, or misrouted. A diagnostic layer over the EventBus is essential for maintainability.

## Options Considered
1. **Third-Party Monitoring (Datadog/Jaeger):** Rely purely on OpenTelemetry tracing and external services for debugging.
2. **Persistent Redis Streams:** Change the EventBus transport from Redis Pub/Sub to Redis Streams to persist all history indefinitely.
3. **In-Memory Diagnostic Ring-Buffer:** The Commander node subscribes to a wildcard topic and retains the last N events in memory, accessible via a REST endpoint.

## Decision
We will implement an In-Memory Diagnostic Ring-Buffer. The Commander node will include an `EventInspector` service that subscribes to `*` on the Redis broker (or local broker). It will maintain a fixed-size `collections.deque(maxlen=1000)` and enforce a TTL (e.g., 5 minutes) on diagnostic retention. These events will be exposed via a new secure REST endpoint `/api/events/history`. 

## Implementation Bounds
To prevent memory exhaustion or OOM evictions:
1. **Python API Endpoint:** The internal buffer must be strictly bounded using `collections.deque(maxlen=1000)`.
2. **Redis Streams/Topics:** All diagnostic inspection channels must enforce a strict `MAXLEN ~ 1000` or a `TTL` of 5 minutes. Unbounded diagnostic logging is strictly prohibited.

## Consequences
- **Positive:** Operators get zero-configuration, immediate introspection into the EventBus directly from the CLI or Dashboard.
- **Positive:** Redis Pub/Sub is maintained, preserving the high-throughput, low-latency transport.
- **Negative:** If event throughput exceeds the ring-buffer capacity within the TTL, older events will be lost. This is acceptable for a diagnostic tool, as persistent tracing should be handled by OpenTelemetry.
