from tools.base import Tool
from tools.builtin.calculator import calculate
from tools.builtin.datetime_tool import get_datetime
from tools.registry import ToolRegistry


def test_calculate_basic():
    assert calculate("123 * 456") == "56088"


def test_calculate_complex():
    assert calculate("(2 + 3) * 4") == "20"


def test_calculate_invalid_expression():
    assert "计算失败" in calculate("import os")


def test_get_datetime_contains_weekday():
    assert "星期" in get_datetime()


def test_registry_execute_and_specs():
    tool = Tool(
        name="double",
        description="翻倍",
        parameters={
            "type": "object",
            "properties": {"x": {"type": "number"}},
            "required": ["x"],
        },
        func=lambda x: str(x * 2),
    )
    registry = ToolRegistry([tool])
    assert registry.names() == ["double"]
    assert registry.execute("double", x=21) == "42"
    assert registry.to_openai_specs()[0]["function"]["name"] == "double"


def test_registry_unknown_tool():
    registry = ToolRegistry()
    assert "未知工具" in registry.execute("nope")
