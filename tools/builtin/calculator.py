import ast
import operator

from tools.base import Tool

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    raise ValueError("不支持的表达式")


def calculate(expression: str) -> str:
    """安全地计算数学表达式（仅数字与运算符，不执行任意代码）。"""
    try:
        result = _eval(ast.parse(expression.strip(), mode="eval"))
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except Exception as exc:  # noqa: BLE001
        return f"计算失败：{exc}"


CALCULATOR_TOOL = Tool(
    name="calculator",
    description="执行数学表达式计算（支持 + - * / % // ** 与括号），返回计算结果。用于需要精确算术时。",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，例如 '(123 * 456) / 2'",
            },
        },
        "required": ["expression"],
    },
    func=lambda expression: calculate(expression),
)
