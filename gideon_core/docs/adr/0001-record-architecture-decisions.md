# 1. Record Architecture Decisions

## Status
Accepted

## Context
Gideon Core has transitioned from an experimental orchestration framework into a stable, distributed platform (v1.0.0). As the project scales, new contributors and auditors will need to understand the historical context behind major architectural choices (e.g., Last-Write-Wins synchronization, Redis pub/sub transport, Qdrant memory). Without a formal record, this institutional knowledge is lost or scattered across pull requests and chat logs.

## Options Considered
- Rely on commit messages and pull request descriptions.
- Maintain a single, monolithic architecture document.
- Adopt Architecture Decision Records (ADRs).

## Decision
We will use Architecture Decision Records, as described by Michael Nygard. We will maintain these records in the `docs/adr/` directory. Each significant architectural decision will be recorded in a standardized markdown file.

## Consequences
- **Positive:** New contributors can easily read the history of the project's evolution.
- **Positive:** Decision rationale is preserved independently of the original developers.
- **Negative:** Requires strict discipline from the core team to write an ADR before implementing any major architectural change.
