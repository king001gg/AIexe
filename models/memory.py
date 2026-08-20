import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config.settings import AppSettings


class MemoryStore:
    """长期记忆：跨会话的用户偏好/事实，落盘到 SQLite。"""

    def __init__(self, db_path: str = None):
        self._db_path = db_path or os.path.join(AppSettings.DB_DIR, "memory.db")
        AppSettings.ensure_dirs()
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    key TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save(self, key: str, content: str) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO memories (key, content, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at",
                (key, content, now),
            )

    def search(self, query: str) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT key, content FROM memories WHERE key LIKE ? OR content LIKE ? "
                "ORDER BY updated_at DESC LIMIT 10",
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
        return [(row["key"], row["content"]) for row in rows]

    def list_all(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT key, content FROM memories ORDER BY updated_at DESC"
            ).fetchall()
        return [(row["key"], row["content"]) for row in rows]

    def delete(self, key: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM memories WHERE key = ?", (key,))


_default_store: MemoryStore = None


def get_memory_store() -> MemoryStore:
    global _default_store
    if _default_store is None:
        _default_store = MemoryStore()
    return _default_store
