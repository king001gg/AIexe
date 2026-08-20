from types import SimpleNamespace

from services.agent import Agent
from tools.base import Tool


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = SimpleNamespace(name=name, arguments=arguments)


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeUsage:
    prompt_tokens = 10
    completion_tokens = 5
    total_tokens = 15


class FakeResponse:
    def __init__(self, message, usage=None):
        self.choices = [SimpleNamespace(message=message)]
        self.usage = usage or FakeUsage()


class FakeService:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat_with_tools(self, messages, tools=None):
        self.calls.append(messages)
        return self.responses.pop(0)


DOUBLE_TOOL = Tool(
    name="double",
    description="把数字翻倍",
    parameters={
        "type": "object",
        "properties": {"x": {"type": "number"}},
        "required": ["x"],
    },
    func=lambda x: str(x * 2),
)


def test_agent_runs_tool_then_answers():
    responses = [
        FakeResponse(FakeMessage(content=None, tool_calls=[FakeToolCall("c1", "double", '{"x": 21}')])),
        FakeResponse(FakeMessage(content="答案是 42")),
    ]
    service = FakeService(responses)
    agent = Agent(service, tools=[DOUBLE_TOOL])

    result = agent.run([{"role": "user", "content": "21 的两倍"}])

    assert result.answer == "答案是 42"
    assert len(result.tool_steps) == 1
    assert result.tool_steps[0].name == "double"
    assert result.tool_steps[0].output == "42"
    assert result.usage["total_tokens"] == 30
    # 第二次调用时，模型应能看到 tool 角色的观测结果
    assert any(m["role"] == "tool" for m in service.calls[1])


def test_agent_no_tools_returns_direct_answer():
    service = FakeService([FakeResponse(FakeMessage(content="直接回答"))])
    agent = Agent(service, tools=[])

    result = agent.run([{"role": "user", "content": "你好"}])

    assert result.answer == "直接回答"
    assert result.tool_steps == []
