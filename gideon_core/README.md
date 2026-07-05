# Gideon: Personal AI Platform

Gideon is a personal AI operating layer designed to sit on top of Windows (initially) and Android. It provides a modular, extensible, and multi-agent architecture designed to be a unified digital partner, not just a chatbot.

## Architecture Highlights
- **System Consciousness:** The top-level interface that maintains continuous awareness of user goals, context, and system state before delegating to specific agents.
- **World State & Event Bus:** A reactive architecture that maintains realtime awareness of device status, applications, and notifications via pub/sub events rather than constant polling.
- **Dynamic AI Team:** Specialized agents for planning, memory, research, coding, vision, and voice. Gideon routes tasks dynamically, sometimes chaining multiple models (e.g., Coder -> Reviewer -> Safety) to complete complex objectives.
- **Experience Memory:** Beyond semantic facts, Gideon records workflows, debugging sessions, and outcomes to grow more capable alongside the user.
- **Skills System:** Capabilities (like web browsing, file management, or trading) exist as independent, learnable Skills rather than rigid tools.
- **Cross-Platform:** Python backend with a Flutter-based shared UI for Desktop and Mobile.
- **Dynamic AI Providers:** Supports NVIDIA APIs, OpenAI, Anthropic, and local models.

## Development Status
- **Phase 1 (In Progress):** Preliminary NVIDIA API Audit complete, and high-level architectural constraints established.

Please see `ARCHITECTURE.md` for a deep dive into Gideon's design principles and `NVIDIA_API_AUDIT.md` for details on verified model capabilities.
