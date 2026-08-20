from tools.base import Tool


def make_memory_tools(memory_store) -> list:
    """创建长期记忆读写工具（绑定一个 MemoryStore 实例）。"""

    def save(key: str, content: str) -> str:
        memory_store.save(key, content)
        return f"已记住：{key} = {content}"

    def search(query: str) -> str:
        results = memory_store.search(query)
        if not results:
            return "没有找到相关记忆。"
        return "\n".join(f"- {k}: {v}" for k, v in results)

    save_tool = Tool(
        name="memory_save",
        description="保存一条长期记忆（键值对），供以后跨会话使用。当用户说'记住…'时使用。",
        parameters={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "记忆主题/键，如'用户喜欢的颜色'"},
                "content": {"type": "string", "description": "记忆内容"},
            },
            "required": ["key", "content"],
        },
        func=save,
    )

    search_tool = Tool(
        name="memory_search",
        description="检索已保存的长期记忆。当需要回忆用户之前的偏好或事实时使用。",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词"},
            },
            "required": ["query"],
        },
        func=search,
    )

    return [save_tool, search_tool]
