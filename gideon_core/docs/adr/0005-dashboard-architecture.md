# 5. Dashboard Architecture

## Status
Accepted

## Context
Gideon needs a graphical interface for human operators to view real-time telemetry, memory utilization, and topological health of the cluster. A purely text-based CLI is insufficient for visualizing asynchronous distributed events.

## Options Considered
1. **Server-Side Rendering (Jinja2):** Serve HTML directly from FastAPI.
2. **Standalone Web App:** Build a separate Next.js application that requires its own container and deployment pipeline.
3. **Embedded SPA:** Build a React/Vite Single Page Application (SPA) compiled to static assets and served directly from the Commander API.

## Decision
We will build an embedded React/Vite SPA. The compiled assets will be mounted and served via FastAPI at the `/` and `/static` routes. The dashboard will connect to the existing `/api/ws` WebSocket to receive a live stream of EventBus telemetry.

## Consequences
- **Positive:** Zero additional infrastructure required. The dashboard ships inherently with every Gideon node.
- **Positive:** High reactivity and real-time visualization via WebSockets.
- **Negative:** Coupling the frontend build step to the backend Python repository. We will mitigate this by placing the frontend in a dedicated `web/` subdirectory.

## Recommendations & Constraints
- **Resilience:** The WebSocket connection (`/api/ws`) must implement auto-reconnect with exponential backoff on the frontend to handle server restarts gracefully.
- **Performance:** The telemetry payload must remain lightweight. Raw LLM tokens should not be streamed over the general cluster status socket; dedicated channels or summarized metrics will be used instead.
