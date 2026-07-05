# Gideon Architectural Design

Gideon is designed as a persistent, stateful, and reactive personal AI operating layer. To transition it from a standard "chatbot" into a cohesive digital intelligence, the architecture relies on the following core pillars.

## 1. System Consciousness Layer

Instead of routing directly to a "Commander" agent, all user interactions pass through the **Consciousness Layer**. This layer maintains the illusion of a single, unified intelligence.

Before passing a prompt to the Commander, the Consciousness Layer injects current context:
- **Current Device:** Windows Desktop vs Android Phone.
- **Current Focus:** What application the user is looking at.
- **Active Agents:** Which background tasks are running.
- **Short-term Memory:** Immediate conversation history.
- **Long-term Goals / Mission:** Active objectives (see Mission Mode).

```
User -> [ Consciousness Layer ] -> Commander Agent -> [ Specialized Agents (Planner, Coder, etc) ]
```

## 2. World State & Event Bus

Gideon does not rely purely on synchronous user commands. It is a reactive system driven by an **Event Bus**.

### World State
A continuous snapshot of the environment, updated in real-time by system monitors:
- Battery Level
- Network Status
- Active Window / Focus
- Active Downloads
- Calendar/Meeting status

### Event Bus (Pub/Sub)
Instead of polling, system components publish events (`WhatsAppMessageReceived`, `FileDownloaded`, `BatteryLow`). Gideon subscribes to these events. The Consciousness layer determines if an event warrants interrupting the user, logging to memory, or triggering a background task.

## 3. Skills (formerly Tools)

Capabilities are defined as **Skills**. This semantic shift represents that Gideon "learns" how to interact with the world.
Skills exist in isolated modules (e.g., `skills/coding`, `skills/email`) and expose standard interfaces.
The Commander dynamically provisions Skills to specialized agents based on the task.

## 4. Mission Mode

Gideon supports goal-oriented states called **Missions**.
When a Mission is active (e.g., "Today's mission is to finish the trading bot"):
- The Consciousness layer prioritizes notifications related to the mission.
- Background agents actively monitor progress.
- Gideon can proactively prompt the user to stay on task or suggest the next logical step.

## 5. Experience Memory & Self-Evaluation

**Experience Memory:**
Unlike standard RAG that stores isolated facts ("User likes dark mode"), Experience Memory stores workflows and resolutions. If Gideon spends an hour debugging a Docker issue with the user, the final resolution, the steps taken, and the root cause are stored as a single "Experience" for future recall.

**Self-Evaluation Loop:**
Upon completing a complex task, Gideon triggers a lightweight, asynchronous evaluation agent:
1. Was the task successful?
2. Did the user have to correct me?
3. Should I synthesize an Experience Memory from this?

## 6. Dynamic AI Team (Multi-Agent Routing)

Gideon abstracts the underlying LLM providers (NVIDIA, OpenAI, Local). The routing layer is capable of **chaining** models for a single request to form an AI Team.

Example Workflow for a Coding Task:
1. **Planner Agent** (Using a reasoning model like `cosmos-reason2-8b`) breaks down the request.
2. **Coder Agent** (Using `deepseek-coder` or `codestral`) writes the code.
3. **Reviewer Agent** (Using `llama-3.3-70b-instruct`) reviews the code for bugs.
4. **Safety Agent** (Using `nemoguard`) verifies no destructive commands are included before execution.

## 7. Personality Engine

Gideon's tone and communication style are decoupled from its logical reasoning. A configuration layer injects system prompts that define the active persona (Professional, Friendly, Concise, Detailed), allowing the user to adapt Gideon's presentation to their current preference without altering backend business logic.

## 8. Synchronization & Connectivity (Phase 8)

Gideon employs a **Local Network Sync + VPN** architecture to synchronize memory, World State, and conversations between the Windows Desktop and Android device.

**Why Local + VPN?**
To maintain strict privacy and avoid cloud hosting costs, the `gideon_core` (Python backend) runs exclusively on the primary machine (Windows Desktop). The database (ChromaDB) and API keys never leave this host.

**The Sync Mechanism:**
1. **Local API:** `gideon_core` exposes a FastAPI server binding to `0.0.0.0`.
2. **Dynamic Endpoint:** The `gideon_ui` (Flutter) app allows the user to configure the backend IP.
    - On Desktop: Connects to `127.0.0.1:8000`.
    - On Mobile (Home Wi-Fi): Connects to `192.168.x.x:8000`.
    - On Mobile (Remote): Connects via VPN.
3. **VPN Solution (Tailscale):** To access Gideon while away from the home network, the user installs a zero-config mesh VPN like Tailscale on both the Desktop and the Android device. The Flutter app is configured to connect to the Desktop's static Tailscale IP (e.g., `100.x.x.x:8000`). This provides secure, end-to-end encrypted remote access to Gideon's automation and memory without exposing the local network to the public internet.
