"""Benchmark runner.

Runs the same prompts, with the same model / temperature / tools / memory
settings, across every framework registered for a scenario, and writes one
JSON object per run to a JSONL file.

Usage::

    uv run python -m benchmarks.runner --scenario web_search --iterations 5
    uv run python -m benchmarks.runner --list

Nothing is executed at import time, so this module can be unit-tested with a
fake agent factory and no credentials.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from agent_contract import AgentResult
from benchmarks.adapters import Adapter, get_adapter
from benchmarks.records import BenchmarkRecord, write_records
from benchmarks.scenarios import Prompt, Scenario, load_scenarios

RESULTS_DIR = Path(__file__).parent / "results"
PREVIEW_CHARS = 300


@dataclass
class RunConfig:
    """Everything held constant across frameworks in one benchmark run."""

    provider: str = "azure"
    iterations: int = 3
    memory: bool = False
    #: Rebuild the agent before every iteration (cold-start measurement).
    fresh_agent: bool = True
    timeout_seconds: float = 120.0
    retries: int = 0
    verbose: bool = False

    def describe(self) -> str:
        return (
            f"provider={self.provider} iterations={self.iterations} "
            f"memory={self.memory} fresh_agent={self.fresh_agent} "
            f"retries={self.retries} timeout={self.timeout_seconds}s"
        )


def _model_name(provider: str) -> str:
    from settings import settings

    return (
        settings.azure_deployment_name
        if provider == "azure"
        else settings.openai_model_name
        if provider == "openai"
        else settings.open_source_model_name
    )


def _temperature() -> float:
    from settings import settings

    return settings.temperature


def run_once(agent, prompt: Prompt, config: RunConfig) -> AgentResult:
    """Run one prompt, retrying only on failures, and enforcing the timeout budget.

    Agents already return an :class:`AgentResult` on error, so retries never
    raise. A run that exceeds ``timeout_seconds`` is reported as a failure
    rather than silently accepted as a slow success.
    """
    attempts = config.retries + 1
    result = AgentResult.from_error("no attempt executed")
    for attempt in range(attempts):
        result = agent.chat(prompt.text)
        if result.success:
            break
        if config.verbose:
            print(f"    attempt {attempt + 1}/{attempts} failed: {result.error}")
        time.sleep(min(2**attempt, 8))

    if result.success and result.elapsed_seconds > config.timeout_seconds:
        return AgentResult(
            content=result.content,
            elapsed_seconds=result.elapsed_seconds,
            usage=result.usage,
            tool_calls=result.tool_calls,
            error=(
                f"exceeded timeout budget "
                f"({result.elapsed_seconds:.1f}s > {config.timeout_seconds}s)"
            ),
        )
    return result


def run_framework(
    framework_id: str,
    scenario: Scenario,
    config: RunConfig,
    agent_factory: Callable[[], object] | None = None,
) -> list[BenchmarkRecord]:
    """Run every prompt of ``scenario`` ``config.iterations`` times."""
    adapter: Adapter | None = None
    if agent_factory is None:
        adapter = get_adapter(framework_id)
        agent_factory = adapter.factory(
            provider=config.provider, memory=config.memory, verbose=config.verbose
        )

    model = _model_name(config.provider)
    temperature = _temperature()
    records: list[BenchmarkRecord] = []
    agent = None

    for prompt in scenario.prompts:
        for iteration in range(1, config.iterations + 1):
            if agent is None or config.fresh_agent:
                try:
                    agent = agent_factory()
                except Exception as exc:  # noqa: BLE001 - reported, not raised
                    records.append(
                        _record(
                            framework_id, scenario, prompt, iteration, model,
                            temperature, config,
                            AgentResult.from_error(f"agent construction failed: {exc}"),
                        )
                    )
                    continue
            elif not config.memory:
                agent.clear_chat()

            result = run_once(agent, prompt, config)
            if config.verbose:
                status = "ok" if result.success else f"ERROR: {result.error}"
                print(
                    f"  [{framework_id}] {prompt.id} #{iteration} "
                    f"{result.elapsed_seconds:.2f}s {status}"
                )
            records.append(
                _record(
                    framework_id, scenario, prompt, iteration, model,
                    temperature, config, result,
                )
            )

    return records


def _record(
    framework_id: str,
    scenario: Scenario,
    prompt: Prompt,
    iteration: int,
    model: str,
    temperature: float,
    config: RunConfig,
    result: AgentResult,
) -> BenchmarkRecord:
    usage = result.usage
    return BenchmarkRecord(
        framework=framework_id,
        scenario=scenario.name,
        prompt_id=prompt.id,
        iteration=iteration,
        model=model,
        provider=config.provider,
        temperature=temperature,
        memory=config.memory,
        elapsed_seconds=round(result.elapsed_seconds, 4),
        success=result.success,
        input_tokens=usage.input_tokens if usage else None,
        output_tokens=usage.output_tokens if usage else None,
        total_tokens=usage.total_tokens if usage else None,
        tool_calls=result.tool_calls,
        error=result.error,
        response_preview=(result.content or "")[:PREVIEW_CHARS] or None,
    )


def run_scenarios(
    scenarios: Iterable[Scenario],
    config: RunConfig,
    frameworks: list[str] | None = None,
) -> list[BenchmarkRecord]:
    records: list[BenchmarkRecord] = []
    for scenario in scenarios:
        targets = [
            f for f in scenario.frameworks if not frameworks or f in frameworks
        ]
        if not targets:
            continue
        print(f"\n=== scenario: {scenario.name} ({len(targets)} frameworks) ===")
        for framework_id in targets:
            print(f"-> {framework_id}")
            records.extend(run_framework(framework_id, scenario, config))
    return records


def default_output_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return RESULTS_DIR / f"run-{stamp}.jsonl"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List scenarios and exit.")
    parser.add_argument(
        "--scenario", action="append", dest="scenarios",
        help="Scenario to run (repeatable). Defaults to all scenarios.",
    )
    parser.add_argument(
        "--framework", action="append", dest="frameworks",
        help="Restrict to these framework ids (repeatable).",
    )
    parser.add_argument("--provider", default="azure", choices=["azure", "openai", "other"])
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--memory", action="store_true", help="Keep conversation history.")
    parser.add_argument(
        "--reuse-agent", action="store_true",
        help="Reuse one agent instance instead of rebuilding it per iteration.",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path, help="JSONL output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        for scenario in load_scenarios():
            print(f"{scenario.name}: {scenario.description}")
            print(f"  frameworks: {', '.join(scenario.frameworks)}")
            print(f"  prompts   : {', '.join(p.id for p in scenario.prompts)}")
        return 0

    config = RunConfig(
        provider=args.provider,
        iterations=args.iterations,
        memory=args.memory,
        fresh_agent=not args.reuse_agent,
        timeout_seconds=args.timeout,
        retries=args.retries,
        verbose=args.verbose,
    )
    print(f"Benchmark config: {config.describe()}")

    scenarios = load_scenarios(args.scenarios)
    records = run_scenarios(scenarios, config, args.frameworks)

    output = args.output or default_output_path()
    write_records(records, output)
    failures = sum(1 for r in records if not r.success)
    print(f"\nWrote {len(records)} records ({failures} failed) to {output}")
    print(f"Build a Markdown report with:\n  python -m benchmarks.report {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
