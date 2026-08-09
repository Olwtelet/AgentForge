"""Benchmark scenarios and their datasets.

A *scenario* fixes what is being measured (which capability, which prompts,
which agent variants). Every framework taking part in a scenario must run the
exact same prompts, so the only variable left is the framework itself.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATASETS_DIR = Path(__file__).parent / "datasets"


@dataclass(frozen=True)
class Prompt:
    id: str
    text: str


@dataclass(frozen=True)
class Scenario:
    """A capability under test, shared by every framework in ``frameworks``."""

    name: str
    description: str
    dataset: str
    frameworks: tuple[str, ...]
    prompts: tuple[Prompt, ...] = ()

    def with_prompts(self, prompts: list[Prompt]) -> "Scenario":
        return Scenario(
            name=self.name,
            description=self.description,
            dataset=self.dataset,
            frameworks=self.frameworks,
            prompts=tuple(prompts),
        )


# Frameworks are referenced by the adapter ids declared in benchmarks/adapters.py
SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="web_search",
        description=(
            "Single-turn question that requires the shared web-search tool. "
            "All frameworks get the same Tavily-backed tool and the same prompts."
        ),
        dataset="web_search.json",
        frameworks=("agno", "langgraph", "llama_index", "llama_index_fc", "openai", "pydantic_ai"),
    ),
    Scenario(
        name="rag",
        description=(
            "Retrieval over the local Champions League knowledge base. Each "
            "framework uses its own vector store, so this measures the whole "
            "retrieval pipeline, not just the LLM."
        ),
        dataset="rag.json",
        frameworks=("agno_rag_api", "langgraph_rag_api", "llama_index_rag_api"),
    ),
    Scenario(
        name="api_tools",
        description=(
            "Multi-tool prompt hitting the shared F1 and Metro API helpers in "
            "shared_functions/, so every framework calls identical tool code."
        ),
        dataset="api_tools.json",
        frameworks=("agno_rag_api", "langgraph_rag_api", "llama_index_rag_api"),
    ),
)


def load_prompts(dataset: str, datasets_dir: Path | None = None) -> list[Prompt]:
    """Load the prompt list backing a scenario."""
    directory = datasets_dir or DATASETS_DIR
    data = json.loads((directory / dataset).read_text(encoding="utf-8"))
    return [Prompt(id=item["id"], text=item["prompt"]) for item in data["prompts"]]


def load_scenarios(
    names: list[str] | None = None, datasets_dir: Path | None = None
) -> list[Scenario]:
    """Return scenarios with their prompts loaded from disk."""
    selected = SCENARIOS
    if names:
        unknown = set(names) - {s.name for s in SCENARIOS}
        if unknown:
            raise ValueError(
                f"Unknown scenario(s): {', '.join(sorted(unknown))}. "
                f"Available: {', '.join(s.name for s in SCENARIOS)}"
            )
        selected = tuple(s for s in SCENARIOS if s.name in names)
    return [s.with_prompts(load_prompts(s.dataset, datasets_dir)) for s in selected]
