# 2. Skill SDK Architecture

## Status
Accepted

## Context
As the Gideon ecosystem grows, developers need a standardized, intuitive way to author remote skills that run on the `ExecutionWorker`. Manually interacting with the raw EventBus and hand-crafting JSON `SkillManifest` schemas is error-prone, brittle, and discouraging to adoption. We need a developer-friendly SDK that abstracts away the underlying messaging protocols.

## Options Considered
1. **Raw JSON/EventBus interaction:** Require developers to manually construct `Event` models and publish them to Redis.
2. **REST Webhooks:** Require skills to be standalone web servers that Gideon calls via HTTP.
3. **Python SDK (`gideon-sdk`):** A lightweight Python package providing decorators and context objects that automatically wrap functions and generate manifests.

## Decision
We will build a Python-first `gideon-sdk`. It will utilize Pydantic for introspection, allowing developers to use a `@gideon_skill` decorator on standard Python functions. The SDK will automatically generate the required JSON schema manifest. It will also provide a `SkillContext` object for interacting with the core framework (e.g., retrieving world state, emitting sub-events) securely.

## Consequences
- **Positive:** Massive reduction in boilerplate code for skill developers.
- **Positive:** Compile-time validation of skill arguments via Pydantic.
- **Negative:** For v1.1, non-Python languages are not natively supported by the SDK, though they can still interact with the raw EventBus if necessary.
