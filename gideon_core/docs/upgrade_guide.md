# Upgrade Guide

## Upgrading from Pre-v1.0 (RC1 or Mega Phases) to v1.0.0

Because `v1.0.0` represents the formal freeze of our core architecture, upgrading from earlier development iterations requires a few specific migrations.

### 1. Database Migration
Pre-v1.0 environments heavily utilized `SQLiteHistory`. If you are migrating to a production setup, you must switch to `PostgresHistory`.
1. Ensure your `.env` contains `POSTGRES_URL`.
2. Start the `postgres` container.
3. The platform will automatically execute `CREATE TABLE IF NOT EXISTS messages` upon the first boot of `PostgresHistory`.
4. (Optional) If you have historical SQLite data you wish to keep, you will need to manually export the `messages` table to CSV and import it into PostgreSQL, as there is no automated schema migrator for the MVP.

### 2. Configuration Changes
The following environment variables are now **strictly required** for production:
- `JWT_SECRET_KEY`: Must be a secure string of at least 32 bytes.
- `EVENT_BROKER_TYPE`: Must be `redis` for multi-node deployments.
- `QDRANT_URL`: Must point to a valid Qdrant instance for Long-Term Memory.

### 3. Application Lifecycle
If you maintain any custom forks of `api.py`, be aware that `@app.on_event("startup")` has been removed. You must migrate any custom initialization code to the `@asynccontextmanager def lifespan(app: FastAPI)` function.

### 4. Skill Migration
Ensure any custom Skills implement the standard `execute` method signature. While the platform supports synchronous execution by wrapping it in a thread pool, migrating your Skills to `async def execute` is highly recommended for optimal performance.
