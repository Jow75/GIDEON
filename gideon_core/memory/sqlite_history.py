import os
from typing import List
import aiosqlite
from config.settings import settings
from providers.base import Message
from memory.base import HistoryStore

class SQLiteHistory(HistoryStore):
    """Persistent conversation history backed by SQLite (Async)."""
    def __init__(self, db_name: str = "conversations.db"):
        self.db_path = os.path.join(settings.data_dir, db_name)
        os.makedirs(settings.data_dir, exist_ok=True)
        # Initialization must be awaited explicitly via initialize().

    async def initialize(self):
        """Create the database schema. Must be awaited before use."""
        await self._init_db()

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)
            ''')
            await conn.commit()

    async def add_message(self, session_id: str, role: str, content: str):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            await conn.commit()

    async def get_context(self, session_id: str, limit: int = 20) -> List[Message]:
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
            # Reverse to maintain chronological order
            return [Message(role=r[0], content=r[1]) for r in reversed(rows)]

    async def clear(self):
        """Clear all messages from the database."""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("DELETE FROM messages")
            await conn.commit()

    async def stop(self):
        """No persistent connections to close for SQLite (per-call connections)."""
        pass

