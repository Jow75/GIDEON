import os
from typing import List
import asyncpg
from config.settings import settings
from providers.base import Message
from memory.base import HistoryStore
import asyncio
import logging

logger = logging.getLogger(__name__)

class PostgresHistory(HistoryStore):
    """Persistent conversation history backed by PostgreSQL (asyncpg)."""
    def __init__(self, postgres_url: str = None):
        self.postgres_url = postgres_url or settings.postgres_url
        self.pool = None
        # Initialization must be awaited explicitly to prevent race conditions.

    async def initialize(self):
        """Initialize the asyncpg connection pool and ensure schema exists.

        Raises on failure so the caller (FastAPI lifespan) can halt startup.
        """
        try:
            self.pool = await asyncpg.create_pool(self.postgres_url)
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)
                ''')
        except Exception as e:
            logger.error(f"Failed to initialize PostgresHistory: {e}")
            raise

    async def add_message(self, session_id: str, role: str, content: str):
        if self.pool is None:
            logger.error(
                "add_message() called but connection pool is unavailable. "
                "Message will not be persisted."
            )
            raise RuntimeError("PostgresHistory is not initialized — call initialize() first.")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES ($1, $2, $3)",
                session_id, role, content
            )

    async def get_context(self, session_id: str, limit: int = 20) -> List[Message]:
        if not self.pool:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT role, content FROM messages WHERE session_id = $1 ORDER BY timestamp DESC LIMIT $2",
                session_id, limit
            )
            # Reverse to maintain chronological order
            return [Message(role=r['role'], content=r['content']) for r in reversed(rows)]

    async def clear(self):
        """Clear all messages from the database."""
        if not self.pool:
            return
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM messages")

    async def stop(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
