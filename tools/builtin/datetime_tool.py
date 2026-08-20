from datetime import datetime

from tools.base import Tool

_WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def get_datetime() -> str:
    now = datetime.now()
    return f"{now:%Y-%m-%d %H:%M:%S} {_WEEKDAYS[now.weekday()]}"


DATETIME_TOOL = Tool(
    name="get_datetime",
    description="获取当前日期、时间和星期。用于需要知道实时时间时。",
    parameters={"type": "object", "properties": {}},
    func=lambda: get_datetime(),
)
