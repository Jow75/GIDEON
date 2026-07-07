# Independent Audit Checklist

Prior to officially tagging the `v1.0.0` release, an independent reviewer must complete this checklist. This ensures the implementation matches the reports and the platform is truly production-ready.

### 1. Repository & Code Quality
- [ ] Clone repository into a clean environment.
- [ ] Review codebase for architectural consistency against the [Architecture Overview](architecture_overview.md).
- [ ] Verify `flake8` and `mypy` pass with no critical errors.
- [ ] Verify `requirements.txt` correctly pins dependencies (Dependency audit).

### 2. Deployment Validation
- [ ] Run `docker-compose up --build -d`.
- [ ] Verify PostgreSQL initializes and migrations (`messages` table) run cleanly.
- [ ] Verify Redis connects without error.
- [ ] Verify Qdrant initializes without error.
- [ ] Access `/readiness` on all nodes and receive `200 OK`.

### 3. Testing & Resilience
- [ ] Run the full test suite (`pytest tests/`) and verify 100% pass rate.
- [ ] Simulate a Redis restart; confirm EventBus gracefully buffers and reconnects.
- [ ] Run the Locust load test and verify throughput and P95 latency match the benchmark reports.
- [ ] Attempt to inject a malicious payload and confirm `GuardianService` blocks it.

### 4. Release Validation & Audit
- [ ] Verify API documentation accurately matches the FastAPI swagger output.
- [ ] Ensure the MIT License is included and third-party dependencies comply.
- [ ] Verify reproducible builds (Docker image from tag matches deployment, no local config required).
- [ ] Verify Secrets Hygiene (`.env.example` is complete, no secrets committed, `.gitignore` skips runtime artifacts).
- [ ] Run a dependency vulnerability scan (e.g., `pip-audit`) and document accepted risks.
- [ ] Run static analysis (`flake8`, `mypy`) consistently.
- [ ] Perform one complete backup and restore test for PostgreSQL and Qdrant (verify no data corruption).
- [ ] Confirm Observability traces correlate logs and metrics via single request IDs.

---
**Reviewer Sign-off:** ___________________________  
**Date:** ___________________________
