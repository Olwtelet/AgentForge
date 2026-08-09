"""Config loading, agent discovery and metric aggregation."""

from __future__ import annotations

import pytest

from agent_contract import AgentResult, TokenUsage
from utils import get_available_agents, get_tools_descriptions, summarize_results


def test_settings_load_without_any_credentials():
    """Importing settings must not require a populated .env."""
    from settings import Settings

    settings = Settings()
    assert settings.openai_model_name
    assert settings.temperature == 0.0
    assert settings.metro_api_token.get_secret_value() == ""


def test_settings_read_values_from_the_environment(monkeypatch):
    from settings import Settings

    monkeypatch.setenv("temperature", "0.7")
    monkeypatch.setenv("openai_model_name", "gpt-4.1-mini")
    settings = Settings()
    assert settings.temperature == 0.7
    assert settings.openai_model_name == "gpt-4.1-mini"


def test_secrets_are_not_exposed_by_repr(monkeypatch):
    from settings import Settings

    monkeypatch.setenv("openai_api_key", "super-secret-value")
    assert "super-secret-value" not in repr(Settings())


def test_get_available_agents_discovers_every_agent_module():
    agents = get_available_agents()
    assert "agno_agent" in agents
    assert "langgraph_agent" in agents
    assert all(name.endswith("_agent") for name in agents)
    assert all(label for label in agents.values())


def test_get_available_agents_does_not_import_or_instantiate_anything():
    """Listing agents must work without credentials or vector stores."""
    import sys

    before = set(sys.modules)
    get_available_agents()
    newly_imported = {m for m in set(sys.modules) - before if "agent" in m}
    assert not newly_imported


def test_get_tools_descriptions_formats_one_line_per_tool():
    rendered = get_tools_descriptions([("a", "does A"), ("b", "does B")])
    assert rendered.splitlines() == ["- a (does A)", "- b (does B)"]


def test_get_tools_descriptions_handles_no_tools():
    assert get_tools_descriptions([]) == ""


# --------------------------------------------------------------------------
# summarize_results
# --------------------------------------------------------------------------

def _ok(seconds: float, total: int = 120) -> AgentResult:
    return AgentResult(
        content="ok",
        elapsed_seconds=seconds,
        usage=TokenUsage(input_tokens=100, output_tokens=20, total_tokens=total),
    )


def test_summarize_results_computes_mean_and_std():
    stats = summarize_results([_ok(2.0), _ok(4.0)])
    assert stats["iterations"] == 2
    assert stats["errors"] == 0
    assert stats["mean_time"] == 3.0
    assert stats["std_time"] == 1.0


def test_summarize_results_counts_errors_and_ignores_their_timings():
    stats = summarize_results([_ok(2.0), AgentResult.from_error("boom", 99.0)])
    assert stats["errors"] == 1
    assert stats["mean_time"] == 2.0


def test_summarize_results_handles_only_errors_without_dividing_by_zero():
    stats = summarize_results([AgentResult.from_error("boom")])
    assert stats["errors"] == 1
    assert stats["mean_time"] == 0.0
    assert stats["total_tokens"] == 0.0


def test_summarize_results_handles_empty_input():
    stats = summarize_results([])
    assert stats["iterations"] == 0
    assert stats["mean_time"] == 0.0


def test_summarize_results_handles_agents_that_report_no_usage():
    stats = summarize_results([AgentResult(content="ok", elapsed_seconds=1.0)])
    assert stats["total_tokens"] == 0.0
    assert stats["mean_time"] == 1.0


@pytest.mark.parametrize("field", ["input_tokens", "output_tokens", "total_tokens"])
def test_summarize_results_averages_token_fields(field):
    stats = summarize_results([_ok(1.0, total=100), _ok(1.0, total=300)])
    assert stats[field] > 0
