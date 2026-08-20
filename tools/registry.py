import logging

from tools.base import Tool

logger = logging.getLogger("aura")


class ToolRegistry:
    """工具注册表：负责注册、查找、执行工具，并生成 OpenAI function-calling spec。"""

    def __init__(self, tools: list = None):
        self._tools = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def names(self) -> list:
        return list(self._tools.keys())

    def to_openai_specs(self) -> list:
        return [tool.to_openai_spec() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> str:
        tool = self.get(name)
        if tool is None:
            return f"错误：未知工具 {name}"
        try:
            return tool.execute(**kwargs)
        except TypeError as exc:
            logger.warning("工具 %s 参数不匹配：%s", name, exc)
            return f"工具 {name} 参数错误：{exc}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("工具 %s 执行失败：%s", name, exc)
            return f"工具 {name} 执行失败：{exc}"
