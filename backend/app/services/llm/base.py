"""
LLM abstraction: interface that any chat provider must implement.
This is the "interface" in the factory pattern — routes depend on this, not on OpenAI or any concrete provider.
"""
from dataclasses import dataclass
from typing import Iterator, Protocol, runtime_checkable


@dataclass
class StreamEvent:
    """Normalized event from any LLM stream: either a text delta or completion with response_id."""
    kind: str  # "delta" | "done"
    text: str | None = None
    response_id: str | None = None


@runtime_checkable
class LLMChatStream(Protocol):
    """Context manager that yields normalized StreamEvent (delta / done)."""
    def __enter__(self) -> "LLMChatStream":
        ...
    def __exit__(self, *args: object) -> None:
        ...
    def __iter__(self) -> Iterator[StreamEvent]:
        ...


class LLMProvider(Protocol):
    """
    Interface for an LLM provider: must be able to stream chat given model, messages, and optional previous response id.
    Implement this for OpenAI, Anthropic, local models, etc.
    """
    def stream_chat(
        self,
        model: str,
        input_items: list[dict],
        previous_response_id: str | None = None,
    ) -> LLMChatStream:
        ...
