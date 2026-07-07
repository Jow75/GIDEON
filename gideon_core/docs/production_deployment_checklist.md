# Production Deployment Checklist

Before routing live traffic to Gideon Core v1.0, ensure all items on this checklist are verified.

## 1. Security Configuration
- [ ] `JWT_SECRET_KEY` is set to a secure, random string (min 32 bytes). It MUST NOT be the default.
- [ ] `ENVIRONMENT` is explicitly set to `production`.
- [ ] HTTPS/TLS termination is configured at the Load Balancer / API Gateway layer.
- [ ] PostgreSQL is secured with a strong password and restricted network access.
- [ ] Qdrant API key is configured (if exposed outside the private network).

## 2. Infrastructure Setup
- [ ] Redis is deployed in a highly available configuration (e.g., Redis Sentinel or Cluster) if strict uptime is required.
- [ ] PostgreSQL is configured for automated daily backups and WAL archiving.
- [ ] Multiple Gideon Core nodes are deployed behind a Load Balancer (e.g., Nginx, ALB).
- [ ] Server clocks on all Gideon nodes are synchronized via NTP to ensure accurate `SyncManager` LWW resolution.

## 3. Observability
- [ ] Application logs are aggregated to a centralized logging system (e.g., ELK, Datadog).
- [ ] Uptime monitoring is configured to poll `GET /health` and `GET /readiness`.
- [ ] Alerts are configured for HTTP 5xx errors and high CPU/Memory utilization.

## 4. Performance Tuning
- [ ] Docker container memory limits are set appropriately (minimum 256MB recommended per node).
- [ ] `asyncpg` connection pool size is tuned to match the expected concurrent request volume (Default: 20).
- [ ] API Rate Limits are configured to match expected user behavior to prevent abuse without impacting UX.
