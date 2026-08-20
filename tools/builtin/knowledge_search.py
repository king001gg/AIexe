from tools.base import Tool


def make_knowledge_search_tool(knowledge_base) -> Tool:
    """创建知识库检索工具（绑定一个 KnowledgeBase 实例）。"""

    def search(query: str, top_k: int = 3) -> str:
        results = knowledge_base.search(query, top_k=top_k)
        if not results:
            return "知识库中没有检索到相关内容。"
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] 来源《{r['title']}》\n{r['content']}")
        return "\n\n".join(parts)

    return Tool(
        name="knowledge_search",
        description="在用户的私有知识库中检索相关内容。当用户询问其上传文档中的信息时使用，不要凭空编造。",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词或问题"},
                "top_k": {"type": "integer", "description": "返回条数，默认 3"},
            },
            "required": ["query"],
        },
        func=search,
    )
