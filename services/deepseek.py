import logging
import time
from typing import Iterator, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    OpenAI,
    RateLimitError,
)

from config.settings import AppSettings

logger = logging.getLogger("aura")


def _is_retryable(exc: Exception) -> bool:
    """判断异常是否值得重试（超时/连接/限流/5xx）。"""
    if isinstance(exc, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code >= 500
    return False


class DeepSeekService:
    def __init__(self, api_key: str, model: str = None):
        self._api_key = api_key
        self._model = model or AppSettings.DEFAULT_MODEL
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=AppSettings.DEEPSEEK_BASE_URL,
            timeout=AppSettings.REQUEST_TIMEOUT,
        )

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        self._model = value

    def _call_with_retry(self, func):
        """对可重试的 API 调用做指数退避重试。"""
        last_exc = None
        for attempt in range(AppSettings.MAX_RETRIES):
            try:
                return func()
            except Exception as exc:  # noqa: BLE001
                if not _is_retryable(exc):
                    raise
                last_exc = exc
                wait = 2 ** attempt
                logger.warning(
                    "DeepSeek 调用失败（第 %d/%d 次）：%s，%.0f 秒后重试",
                    attempt + 1, AppSettings.MAX_RETRIES, exc, wait,
                )
                time.sleep(wait)
        raise last_exc

    def chat_stream(self, messages: list) -> Iterator:
        """流式对话，返回迭代器；开启 usage 回传（最后一个 chunk 携带 usage）。"""
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
        )

    def chat(self, messages: list) -> str:
        def _call():
            return self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                stream=False,
            )
        response = self._call_with_retry(_call)
        return response.choices[0].message.content

    def chat_with_tools(self, messages: list, tools: Optional[list] = None):
        """非流式 function calling 调用，返回完整 response（含 tool_calls）。"""
        def _call():
            return self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                stream=False,
            )
        return self._call_with_retry(_call)

    @staticmethod
    def validate_key(api_key: str) -> bool:
        try:
            client = OpenAI(api_key=api_key, base_url=AppSettings.DEEPSEEK_BASE_URL)
            client.models.list()
            return True
        except Exception:
            return False
