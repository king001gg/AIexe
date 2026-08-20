from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    """一个可供 agent 调用的工具。

    func 的入参需与 parameters 的 JSON Schema 属性一一对应，
    返回值必须是字符串（作为工具观测结果喂回模型）。
    """

    name: str
    description: str
    parameters: dict
    func: Callable[..., str]

    def execute(self, **kwargs) -> str:
        return self.func(**kwargs)

    def to_openai_spec(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
