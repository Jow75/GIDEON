# Security Model

Gideon Core v1.0 implements a defense-in-depth approach to security, ensuring that rogue skills, malicious payloads, and unauthorized access are blocked at multiple layers.

## 1. Authentication
All API endpoints (except health probes) and WebSocket connections require a valid JSON Web Token (JWT).
- Tokens are signed using `HS256`.
- The `JWT_SECRET_KEY` must be manually provided in production. Booting with the development default will cause a fatal error.
- Tokens enforce an expiration (`exp`).

## 2. Rate Limiting
Distributed rate limiting is enforced via `slowapi` backed by `RedisStorage`.
- Default limit: `60 requests per minute` per IP address.
- Prevents brute-force authentication and denial of service via rapid event generation.

## 3. The Guardian Service
Before any LLM-generated payload is executed (e.g., executing a Skill or making a system call), it must pass through the `GuardianService`.
- **Validation:** Ensures payloads conform strictly to the defined JSON schemas in the `SkillManifest`.
- **Sanitization:** Blocks known malicious patterns (e.g., shell injections, unauthorized directory traversal).
- **Enforcement:** If `Guardian` denies a request, an `AccessDeniedException` is raised, and the event is dropped.

## 4. Execution Isolation
- Skills executed by the `ExecutionWorker` run natively on the host OS in the MVP.
- **Future Milestone:** True sandbox isolation (e.g., Docker-in-Docker, WebAssembly, or gVisor) is planned for untrusted third-party skills. Until then, only install trusted plugins.

## 5. Network Isolation
- It is expected that the Redis, PostgreSQL, and Qdrant containers are NOT exposed to the public internet.
- Only the FastAPI port (`8000`) should be proxied through a load balancer.
