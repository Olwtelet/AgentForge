"""Benchmark runner and record serialization. No credentials, no network."""

from __future__ import annotations

import json

import pytest

from agent_contract import AgentResult, TokenUsage
from benchmarks.adapters import ADAPTERS, get_adapter
from benchmarks.records import BenchmarkRecord, load_records, write_records
from benchmarks.runner import RunConfig, run_framework, run_once
from benchmarks.scenarios import SCENARIOS, Prompt, Scenario, load_scenarios


class FakeAgent:
    """Minimal agent honouring the contract, with scripted results."""

    name = "Fake Agent"

    def __init__(self, results: list[AgentResult]):
        self._results = list(results)
        self.calls: list[str] = []
        self.cleared = 0

    def chat(self, message: str) -> AgentResult:
        self.calls.append(message)
        return self._results.pop(0) if self._results else AgentResult("ok", 0.1)

    def clear_chat(self) -> bool:
        self.cleared += 1
        return True


@pytest.fixture
def scenario() -> Scenario:
    return Scenario(
        name="unit",
        description="fixture scenario",
        dataset="unused.json",
        frameworks=("fake",),
        prompts=(Prompt(id="p1", text="hello"),),
    )


@pytest.fixture(autouse=True)
def _stub_settings(monkeypatch):
    """Avoid importing the real settings module in unit tests."""
    monkeypatch.setattr("benchmarks.runner._model_name", lambda provider: "test-model")
    monkeypatch.setattr("benchmarks.runner._temperature", lambda: 0.0)


# --------------------------------------------------------------------------
# run_once
# --------------------------------------------------------------------------

def test_run_once_returns_first_successful_result():
    agent = FakeAgent([AgentResult("done", 0.4)])
    result = run_once(agent, Prompt("p", "hi"), RunConfig())
    assert result.success and result.content == "done"


def test_run_once_retries_until_success(monkeypatch):
    monkeypatch.setattr("benchmarks.runner.time.sleep", lambda _: None)
    agent = FakeAgent([AgentResult.from_error("rate limited"), AgentResult("done", 0.2)])
    result = run_once(agent, Prompt("p", "hi"), RunConfig(retries=1))
    assert result.success
    assert len(agent.calls) == 2


def test_run_once_gives_up_after_retries_and_never_raises(monkeypatch):
    monkeypatch.setattr("benchmarks.runner.time.sleep", lambda _: None)
    agent = FakeAgent([AgentResult.from_error("boom")] * 3)
    result = run_once(agent, Prompt("p", "hi"), RunConfig(retries=2))
    assert result.success is False
    assert result.error == "boom"


def test_run_once_marks_slow_runs_as_timeouts():
    agent = FakeAgent([AgentResult("slow", elapsed_seconds=99.0)])
    result = run_once(agent, Prompt("p", "hi"), RunConfig(timeout_seconds=1.0))
    assert result.success is False
    assert "timeout" in result.error


# --------------------------------------------------------------------------
# run_framework
# --------------------------------------------------------------------------

def test_run_framework_produces_one_record_per_iteration(scenario):
    config = RunConfig(iterations=3)
    records = run_framework(
        "fake", scenario, config, agent_factory=lambda: FakeAgent([])
    )
    assert len(records) == 3
    assert [r.iteration for r in records] == [1, 2, 3]
    assert {r.framework for r in records} == {"fake"}
    assert {r.scenario for r in records} == {"unit"}


def test_run_framework_records_usage_and_tool_calls(scenario):
    result = AgentResult(
        content="answer",
        elapsed_seconds=1.25,
        usage=TokenUsage(input_tokens=100, output_tokens=20, total_tokens=120),
        tool_calls=2,
    )
    records = run_framework(
        "fake", scenario, RunConfig(iterations=1),
        agent_factory=lambda: FakeAgent([result]),
    )
    record = records[0]
    assert (record.input_tokens, record.output_tokens, record.total_tokens) == (100, 20, 120)
    assert record.tool_calls == 2
    assert record.success is True
    assert record.model == "test-model"


def test_run_framework_records_failures_instead_of_raising(scenario):
    records = run_framework(
        "fake", scenario, RunConfig(iterations=2),
        agent_factory=lambda: FakeAgent([AgentResult.from_error("kaboom")] * 2),
    )
    assert all(r.success is False for r in records)
    assert all(r.error == "kaboom" for r in records)
    assert all(r.total_tokens is None for r in records)


def test_run_framework_records_agent_construction_failure(scenario):
    def _explode():
        raise RuntimeError("missing api key")

    records = run_framework("fake", scenario, RunConfig(iterations=1), agent_factory=_explode)
    assert len(records) == 1
    assert records[0].success is False
    assert "missing api key" in records[0].error


def test_reused_agent_is_cleared_between_runs_when_memory_is_off(scenario):
    agent = FakeAgent([])
    run_framework(
        "fake", scenario, RunConfig(iterations=3, fresh_agent=False, memory=False),
        agent_factory=lambda: agent,
    )
    # Built once, then cleared before each subsequent iteration.
    assert agent.cleared == 2


def test_reused_agent_keeps_history_when_memory_is_on(scenario):
    agent = FakeAgent([])
    run_framework(
        "fake", scenario, RunConfig(iterations=3, fresh_agent=False, memory=True),
        agent_factory=lambda: agent,
    )
    assert agent.cleared == 0


# --------------------------------------------------------------------------
# Records round-trip
# --------------------------------------------------------------------------

def test_records_round_trip_through_jsonl(tmp_path, scenario):
    records = run_framework(
        "fake", scenario, RunConfig(iterations=2), agent_factory=lambda: FakeAgent([])
    )
    path = write_records(records, tmp_path / "nested" / "run.jsonl")

    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["framework"] == "fake"

    loaded = load_records(path)
    assert [r.iteration for r in loaded] == [1, 2]
    assert loaded[0].schema_version == records[0].schema_version


def test_write_records_appends(tmp_path):
    path = tmp_path / "run.jsonl"
    record = BenchmarkRecord(
        framework="fake", scenario="unit", prompt_id="p", iteration=1,
        model="m", provider="azure", temperature=0.0, memory=False,
        elapsed_seconds=0.1, success=True,
    )
    write_records([record], path)
    write_records([record], path)
    assert len(load_records(path)) == 2


def test_load_records_ignores_blank_lines(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text('\n{"framework": "a", "scenario": "s", "prompt_id": "p", '
                    '"iteration": 1, "model": "m", "provider": "azure", '
                    '"temperature": 0.0, "memory": false, "elapsed_seconds": 1.0, '
                    '"success": true}\n\n', encoding="utf-8")
    assert len(load_records(path)) == 1


def test_load_records_tolerates_unknown_future_fields(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text('{"framework": "a", "scenario": "s", "prompt_id": "p", '
                    '"iteration": 1, "model": "m", "provider": "azure", '
                    '"temperature": 0.0, "memory": false, "elapsed_seconds": 1.0, '
                    '"success": true, "some_future_field": 123}\n', encoding="utf-8")
    assert load_records(path)[0].framework == "a"


# --------------------------------------------------------------------------
# Scenarios and adapters
# --------------------------------------------------------------------------

def test_every_shipped_scenario_loads_its_dataset():
    scenarios = load_scenarios()
    assert len(scenarios) == len(SCENARIOS)
    for loaded in scenarios:
        assert loaded.prompts, f"{loaded.name} has no prompts"
        assert all(p.text.strip() for p in loaded.prompts)


def test_scenario_prompt_ids_are_unique():
    for scenario in load_scenarios():
        ids = [p.id for p in scenario.prompts]
        assert len(ids) == len(set(ids)), scenario.name


def test_every_scenario_framework_has_an_adapter():
    for scenario in SCENARIOS:
        for framework_id in scenario.frameworks:
            assert framework_id in ADAPTERS, f"{scenario.name} -> {framework_id}"


def test_load_scenarios_rejects_unknown_names():
    with pytest.raises(ValueError, match="Unknown scenario"):
        load_scenarios(["does-not-exist"])


def test_get_adapter_rejects_unknown_framework():
    with pytest.raises(ValueError, match="Unknown framework"):
        get_adapter("nope")


def test_adapter_modules_are_unique():
    modules = [a.module for a in ADAPTERS.values()]
    assert len(modules) == len(set(modules))
