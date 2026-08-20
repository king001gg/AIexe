import os
import tempfile

from services.usage import UsageTracker


def test_estimate_cost():
    assert UsageTracker.estimate_cost("deepseek-chat", 1_000_000, 1_000_000) == 3.0


def test_record_and_summary():
    with tempfile.TemporaryDirectory() as tmp:
        tracker = UsageTracker(db_path=os.path.join(tmp, "usage.db"))
        tracker.record("deepseek-chat", 1000, 500)

        summary = tracker.summary()
        assert summary["calls"] == 1
        assert summary["total_tokens"] == 1500
