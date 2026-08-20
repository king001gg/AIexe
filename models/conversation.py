import json
import os
import uuid
from datetime import datetime
from typing import Optional

from config.settings import AppSettings


class ConversationManager:
    def __init__(self):
        self._conversations_dir = AppSettings.CONVERSATIONS_DIR
        AppSettings.ensure_dirs()

    def load_all(self) -> dict:
        convs = {}
        if not os.path.exists(self._conversations_dir):
            return convs
        for fname in os.listdir(self._conversations_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self._conversations_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    convs[data["id"]] = data
                except (json.JSONDecodeError, KeyError):
                    pass
        return convs

    def save(self, conv_data: dict) -> None:
        fpath = os.path.join(self._conversations_dir, f"{conv_data['id']}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(conv_data, f, ensure_ascii=False, indent=2)

    def delete(self, conv_id: str) -> None:
        fpath = os.path.join(self._conversations_dir, f"{conv_id}.json")
        if os.path.exists(fpath):
            os.remove(fpath)

    def create(self, user_name: str = "用户", ai_name: str = "AURA", ai_personality: str = "理性冷静") -> str:
        conv_id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conv_data = {
            "id": conv_id,
            "title": "新对话",
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "user_name": user_name,
            "ai_name": ai_name,
            "ai_personality": ai_personality,
        }
        self.save(conv_data)
        return conv_id

    def auto_title(self, conv_data: dict) -> None:
        if not conv_data["messages"]:
            return
        if conv_data["title"] != "新对话":
            return
        first_user_msg = ""
        for m in conv_data["messages"]:
            if m["role"] == "user":
                first_user_msg = m["content"]
                break
        if first_user_msg:
            limit = AppSettings.AUTO_TITLE_LENGTH
            conv_data["title"] = first_user_msg[:limit] + ("..." if len(first_user_msg) > limit else "")

    def touch(self, conv_data: dict) -> None:
        conv_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    def get_sorted(self, convs: dict) -> list:
        return sorted(convs.values(), key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_latest_id(self, convs: Optional[dict] = None) -> Optional[str]:
        if convs is None:
            convs = self.load_all()
        if not convs:
            return None
        sorted_convs = self.get_sorted(convs)
        return sorted_convs[0]["id"]