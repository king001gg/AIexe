import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime

from config.settings import AppSettings
from services.rag.chunker import chunk_text
from services.rag.retriever import BM25Index


class KnowledgeBase:
    """私有知识库：文档落盘到 SQLite，检索用内存 BM25 索引。"""

    def __init__(self, db_path: str = None):
        self._db_path = db_path or os.path.join(AppSettings.DB_DIR, "knowledge.db")
        AppSettings.ensure_dirs()
        self._index = BM25Index()
        self._init_db()
        self._load_index()

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
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _load_index(self) -> None:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, title, content FROM documents").fetchall()
        for row in rows:
            for chunk in chunk_text(row["content"]):
                self._index.add(row["id"], row["title"], chunk)

    def _rebuild_index(self) -> None:
        self._index = BM25Index()
        self._load_index()

    def add_document(self, title: str, content: str):
        chunks = chunk_text(content)
        if not chunks:
            return None
        doc_id = uuid.uuid4().hex[:12]
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO documents (id, title, content, chunk_count, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    doc_id,
                    title,
                    content,
                    len(chunks),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        for chunk in chunks:
            self._index.add(doc_id, title, chunk)
        return doc_id

    def search(self, query: str, top_k: int = 3) -> list:
        return self._index.search(query, top_k)

    def list_documents(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, chunk_count, created_at FROM documents ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def delete(self, doc_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self._rebuild_index()


_default_kb: KnowledgeBase = None


def get_knowledge_base() -> KnowledgeBase:
    global _default_kb
    if _default_kb is None:
        _default_kb = KnowledgeBase()
    return _default_kb
