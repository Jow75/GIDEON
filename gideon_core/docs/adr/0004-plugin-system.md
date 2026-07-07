# 4. Plugin System

## Status
Accepted

## Context
Core capabilities and external integrations (e.g., Slack, GitHub) should not require modifying and rebuilding the core `SystemConsciousness` orchestrator. We need a safe mechanism to dynamically load third-party integrations into Gideon without compromising the stability of the core loop.

## Options Considered
1. **Monolithic Repository:** Integrate all integrations directly into the core repository.
2. **External Remote Workers Only:** Force all plugins to be external processes interacting over the EventBus.
3. **In-Process `PluginManager`:** Allow zipped plugins to be dynamically loaded into the Commander process.

## Decision
We will implement an In-Process `PluginManager` for v1.1. Plugins will be packaged bundles containing a `manifest.json` and Python entry points. The `PluginManager` will dynamically import these modules. 
To mitigate security risks, `Guardian` will enforce explicit permissions (e.g., `eventbus:read`, `state:write`) declared in the plugin manifest. If a plugin requests unauthorized access to the EventBus, it will be blocked.

## Consequences
- **Positive:** Integrations can be maintained, versioned, and distributed independently of the core framework.
- **Positive:** Extremely low latency for core plugins running in the same process.
- **Negative/Risk:** True sandbox isolation (e.g., restricting file system access) is not enforced at the OS level in v1.1. Malicious plugins could compromise the Commander node. Therefore, only trusted plugins should be installed until v1.2.

## Mandatory Guardrails (v1.1)
Because a misbehaving plugin can block the async event loop, leak memory, or crash `SystemConsciousness`, we enforce the following:
1. **Strict Timeouts:** All plugin execution calls must be wrapped in `asyncio.wait_for(timeout=...)`.
2. **Exception Isolation:** All unhandled exceptions must be caught and logged at the plugin boundary so a bad plugin cannot take down the core host.
3. **Roadmap Flag (Technical Debt):** Same-process execution is explicitly marked as technical debt, slated for Wasm or out-of-process RPC isolation in v1.2.
