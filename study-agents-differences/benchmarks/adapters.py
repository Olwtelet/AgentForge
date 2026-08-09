"""Framework adapters.

Every adapter maps a stable framework id to the module that implements it.
Agents are imported lazily so that running a single scenario does not require
every framework's dependencies to be installed.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from agent_contract import AgentResult


class SupportsChat(Protocol):
    name: str

    def chat(self, message: str) -> AgentResult: ...

    def clear_chat(self) -> bool: ...


@dataclass(frozen=True)
class Adapter:
    """Declares how to build one framework's agent for the benchmark."""

    id: str
    label: str
    module: str
    #: Attribute holding the agent class. Every agent module exposes ``Agent``.
    attribute: str = "Agent"

    def factory(
        self, provider: str, memory: bool, verbose: bool = False
    ) -> Callable[[], SupportsChat]:
        """Return a zero-argument callable that builds a fresh agent."""

        def build() -> SupportsChat:
            module: Any = importlib.import_module(self.module)
            agent_class = getattr(module, self.attribute)
            return agent_class(
                provider=provider, memory=memory, verbose=verbose, tokens=True
            )

        return build


ADAPTERS: dict[str, Adapter] = {
    adapter.id: adapter
    for adapter in (
        Adapter("agno", "Agno", "agno_agent"),
        Adapter("langgraph", "LangGraph", "langgraph_agent"),
        Adapter("llama_index", "LlamaIndex (ReAct)", "llama_index_agent"),
        Adapter("llama_index_fc", "LlamaIndex (Function Calling)", "llama_index_fc_agent"),
        Adapter("openai", "OpenAI SDK", "openai_agent"),
        Adapter("pydantic_ai", "Pydantic AI", "pydantic_ai_agent"),
        Adapter("agno_rag_api", "Agno (RAG + API)", "agno_rag_api_agent"),
        Adapter("langgraph_rag_api", "LangGraph (RAG + API)", "langgraph_rag_api_agent"),
        Adapter("llama_index_rag_api", "LlamaIndex (RAG + API)", "llama_index_rag_api_agent"),
    )
}


def get_adapter(framework_id: str) -> Adapter:
    try:
        return ADAPTERS[framework_id]
    except KeyError:
        raise ValueError(
            f"Unknown framework '{framework_id}'. "
            f"Available: {', '.join(sorted(ADAPTERS))}"
        ) from None
