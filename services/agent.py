import json
import logging
from dataclasses import dataclass
from typing import Optional

from config.settings import AppSettings
from services.deepseek import DeepSeekService
from tools.registry import ToolRegistry

logger = logging.getLogger("aura")


@dataclass
class ToolStep:
    name: str
    arguments: dict
    output: str


@dataclass
class AgentResult:
    answer: str
    tool_steps: list
    usage: dict


class Agent:
    """ReAct 风格 agent 循环：模型 → 工具调用 → 观测 → 循环，直至给出最终回答。"""

    def __init__(
        self,
        service: DeepSeekService,
        tools: Optional[list] = None,
        max_iterations: int = None,
    ):
        self.service = service
        self.registry = ToolRegistry(tools or [])
        self.max_iterations = max_iterations or AppSettings.MAX_AGENT_ITERATIONS

    def run(self, messages: list) -> AgentResult:
        working = list(messages)
        tool_steps = []
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for _ in range(self.max_iterations):
            tools = self.registry.to_openai_specs() or None
            response = self.service.chat_with_tools(working, tools)
            self._accumulate_usage(usage, response.usage)
            msg = response.choices[0].message

            if msg.tool_calls:
                working.append(self._assistant_message(msg))
                for tc in msg.tool_calls:
                    name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    output = self.registry.execute(name, **args)
                    logger.info("工具调用 %s(%s) -> %s", name, args, output[:100])
                    tool_steps.append(ToolStep(name=name, arguments=args, output=output))
                    working.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": output}
                    )
                continue

            return AgentResult(answer=msg.content or "", tool_steps=tool_steps, usage=usage)

        logger.warning("Agent 达到最大迭代次数 %d，返回空回答", self.max_iterations)
        return AgentResult(answer="", tool_steps=tool_steps, usage=usage)

    @staticmethod
    def _assistant_message(msg) -> dict:
        return {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        }

    @staticmethod
    def _accumulate_usage(usage: dict, chunk_usage) -> None:
        if not chunk_usage:
            return
        usage["prompt_tokens"] += chunk_usage.prompt_tokens or 0
        usage["completion_tokens"] += chunk_usage.completion_tokens or 0
        usage["total_tokens"] += chunk_usage.total_tokens or 0
