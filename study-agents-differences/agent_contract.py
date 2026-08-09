"""Common result contract shared by every agent implementation.

Every agent's ``chat()`` must return an :class:`AgentResult`, both on success
and on failure. This keeps the Streamlit UI, the CLI runner and the benchmark
runner framework-agnostic: they never have to guess whether they received a
string, a tuple or an exception message.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass
class TokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    embedding_tokens: int | None = None

    @classmethod
    def from_legacy_counter(cls, counter: Mapping[str, Any] | None) -> "TokenUsage | None":
        """Build a TokenUsage from the legacy ``{*_token_count: int}`` dicts."""
        if not counter:
            return None
        return cls(
            input_tokens=counter.get("prompt_llm_token_count"),
            output_tokens=counter.get("completion_llm_token_count"),
            total_tokens=counter.get("total_llm_token_count"),
            embedding_tokens=counter.get("total_embedding_token_count"),
        )


@dataclass
class AgentResult:
    content: str
    elapsed_seconds: float
    usage: TokenUsage | None = None
    error: str | None = None
    # Number of tool invocations, when the framework exposes it. ``None`` means
    # "not reported by this framework", which is different from ``0``.
    tool_calls: int | None = None

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["success"] = self.success
        return data

    @classmethod
    def from_error(cls, exc: BaseException | str, elapsed_seconds: float = 0.0) -> "AgentResult":
        if isinstance(exc, BaseException):
            message = str(exc) or exc.__class__.__name__
        else:
            message = str(exc)
        return cls(content="", elapsed_seconds=elapsed_seconds, usage=None, error=message)


def count_tool_calls(candidate: Any) -> int | None:
    """Best-effort count of tool invocations from a framework-specific object.

    Returns ``None`` when the framework does not expose a countable collection,
    so callers can tell "not reported" apart from "zero tool calls".
    """
    if candidate is None:
        return None
    try:
        return len(candidate)
    except TypeError:
        return None
