import os
import tempfile

from models.memory import MemoryStore


def test_memory_save_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        store = MemoryStore(db_path=os.path.join(tmp, "mem.db"))
        store.save("喜欢的颜色", "蓝色")

        assert ("喜欢的颜色", "蓝色") in store.search("颜色")


def test_memory_upsert():
    with tempfile.TemporaryDirectory() as tmp:
        store = MemoryStore(db_path=os.path.join(tmp, "mem.db"))
        store.save("城市", "北京")
        store.save("城市", "上海")

        assert store.search("城市")[0][1] == "上海"
