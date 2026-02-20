"""
OpenAI implementation of the LLM provider interface.
Uses the OpenAI Responses API to stream chat; normalizes raw events to StreamEvent for the route layer.
"""
from typing import Any, Iterator
from openai import OpenAI
from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMChatStream, StreamEvent


class _OpenAIStreamAdapter:
    """Wraps OpenAI stream and yields normalized StreamEvent (delta / done)."""

    def __init__(self, openai_stream: Any) -> None:
        self._stream_manager = openai_stream
        self._stream: Any = None  # Will be set when entering context

    def __enter__(self) -> "_OpenAIStreamAdapter":
        # ResponseStreamManager.__enter__() returns the actual iterable stream
        self._stream = self._stream_manager.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        self._stream_manager.__exit__(*args)

    def __iter__(self) -> Iterator[StreamEvent]:
        if self._stream is None:
            raise RuntimeError("Stream not entered. Use 'with' statement.")
        for event in self._stream:
            if event.type == "response.output_text.delta":
                yield StreamEvent(kind="delta", text=event.delta or "")
            elif event.type == "response.completed" and getattr(event, "response", None):
                rid = getattr(event.response, "id", None) or ""
                yield StreamEvent(kind="done", response_id=rid)
        return


class OpenAIProvider:
    """Implements LLMProvider using OpenAI Responses API."""

    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def stream_chat(
        self,
        model: str,
        input_items: list[dict[str, Any]],
        previous_response_id: str | None = None,
    ) -> LLMChatStream:
        # OpenAI SDK accepts list[dict] for input_items in practice
        raw = self._client.responses.stream(  # pyright: ignore[reportArgumentType]
            model=model,
            input=input_items,
            previous_response_id=previous_response_id,
        )
        return _OpenAIStreamAdapter(raw)
