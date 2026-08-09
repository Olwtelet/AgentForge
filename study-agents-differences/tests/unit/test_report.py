"""Markdown report generation from JSONL records."""

from __future__ import annotations

from benchmarks.records import BenchmarkRecord
from benchmarks.report import render_markdown, summarize


def _record(**overrides) -> BenchmarkRecord:
    defaults = dict(
        framework="langgraph",
        scenario="web_search",
        prompt_id="p1",
        iteration=1,
        model="gpt-4o-mini",
        provider="azure",
        temperature=0.0,
        memory=False,
        elapsed_seconds=2.0,
        success=True,
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
        tool_calls=1,
    )
    defaults.update(overrides)
    return BenchmarkRecord(**defaults)


def test_summary_groups_by_scenario_and_framework():
    summary = summarize([
        _record(framework="agno"),
        _record(framework="agno", iteration=2, elapsed_seconds=4.0),
        _record(framework="langgraph"),
    ])
    assert set(summary) == {("web_search", "agno"), ("web_search", "langgraph")}
    assert summary[("web_search", "agno")]["runs"] == 2
    assert summary[("web_search", "agno")]["mean_seconds"] == 3.0


def test_failures_are_counted_and_excluded_from_the_mean():
    summary = summarize([
        _record(elapsed_seconds=2.0),
        _record(iteration=2, success=False, error="boom", elapsed_seconds=99.0,
                input_tokens=None, output_tokens=None, total_tokens=None),
    ])
    stats = summary[("web_search", "langgraph")]
    assert stats["runs"] == 2
    assert stats["failures"] == 1
    assert stats["mean_seconds"] == 2.0


def test_all_failed_runs_produce_no_latency_instead_of_zero():
    stats = summarize([_record(success=False, error="boom")])[("web_search", "langgraph")]
    assert stats["mean_seconds"] is None
    assert stats["total_tokens"] is None


def test_missing_token_counts_are_ignored_not_treated_as_zero():
    stats = summarize([
        _record(total_tokens=100),
        _record(iteration=2, total_tokens=None),
    ])[("web_search", "langgraph")]
    assert stats["total_tokens"] == 100


def test_render_markdown_includes_run_metadata_and_a_table():
    markdown = render_markdown([_record(), _record(framework="agno")])
    assert "# Benchmark results" in markdown
    assert "## Scenario: `web_search`" in markdown
    assert "gpt-4o-mini" in markdown
    assert "LangGraph" in markdown  # adapter label, not the raw id
    assert "| Framework |" in markdown


def test_render_markdown_renders_unreported_metrics_as_a_dash():
    markdown = render_markdown([_record(tool_calls=None, total_tokens=None)])
    assert "—" in markdown


def test_render_markdown_handles_no_records():
    assert "No benchmark records" in render_markdown([])
