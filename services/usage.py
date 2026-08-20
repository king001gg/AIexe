import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config.settings import AppSettings

# DeepSeek 定价（元 / 百万 token，输入 / 输出）
PRICING = {
    "deepseek-chat": {"input": 1.0, "output": 2.0},
    "deepseek-reasoner": {"input": 4.0, "output": 16.0},
}


class UsageTracker:
    """Token 用量与成本统计，落盘到 SQLite。"""

    def __init__(self, db_path: str = None):
        self._db_path = db_path or os.path.join(AppSettings.DB_DIR, "usage.db")
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
                CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL DEFAULT 0,
                    completion_tokens INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    cost REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        price = PRICING.get(model, {"input": 1.0, "output": 2.0})
        return (prompt_tokens * price["input"] + completion_tokens * price["output"]) / 1_000_000

    def record(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        if not prompt_tokens and not completion_tokens:
            return
        cost = self.estimate_cost(model, prompt_tokens, completion_tokens)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO usage (model, prompt_tokens, completion_tokens, total_tokens, cost, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    model,
                    prompt_tokens,
                    completion_tokens,
                    prompt_tokens + completion_tokens,
                    cost,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

    def summary(self) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS calls, "
                "COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens, "
                "COALESCE(SUM(completion_tokens), 0) AS completion_tokens, "
                "COALESCE(SUM(total_tokens), 0) AS total_tokens, "
                "COALESCE(SUM(cost), 0) AS cost "
                "FROM usage"
            ).fetchone()
        return dict(row)


_default_tracker: UsageTracker = None


def get_tracker() -> UsageTracker:
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = UsageTracker()
    return _default_tracker
