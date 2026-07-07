# Contributing to Gideon Core

First, thank you for considering contributing to Gideon Core! It's people like you that make Gideon an incredible open-source AI operating system.

## Code of Conduct
This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Submitting Pull Requests
1. **Fork the Repository:** Create your own fork and branch off of `main`.
2. **Follow the Architecture:** Gideon v1.0.0 has a frozen core architecture. Do not propose breaking changes to the EventBus, HistoryStore, or SyncManager without prior discussion in an Issue.
3. **Write Tests:** Any new capability must be fully tested via `pytest`.
4. **Pass CI:** Ensure `flake8`, `mypy`, and `pytest` all pass locally before submitting.

## Reporting Bugs
Open an issue on GitHub. Include:
- Gideon Core version
- Python version
- Docker logs (if applicable)
- Steps to reproduce

## Suggesting Enhancements
We welcome new capabilities! For major features (e.g., a new core Plugin, or changes to the Agent swarm), please open a "Feature Request" issue to discuss the design before submitting a PR.
