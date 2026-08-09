"""Turn benchmark JSONL results into Markdown tables.

Usage::

    uv run python -m benchmarks.report benchmarks/results/run-*.jsonl
    uv run python -m benchmarks.report benchmarks/results/*.jsonl -o REPORT.md

The README never needs hand-copied numbers: whatever this prints is derived
directly from the recorded runs.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from benchmarks.adapters import ADAPTERS
from benchmarks.records import BenchmarkRecord, load_records


def _label(framework_id: str) -> str:
    adapter = ADAPTERS.get(framework_id)
    return adapter.label if adapter else framework_id


def _mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _stdev(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _fmt(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def summarize(records: list[BenchmarkRecord]) -> dict[tuple[str, str], dict]:
    """Aggregate records by (scenario, framework)."""
    grouped: dict[tuple[str, str], list[BenchmarkRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.scenario, record.framework)].append(record)

    summary: dict[tuple[str, str], dict] = {}
    for key, group in grouped.items():
        ok = [r for r in group if r.success]
        times = [r.elapsed_seconds for r in ok]
        summary[key] = {
            "runs": len(group),
            "failures": len(group) - len(ok),
            "mean_seconds": _mean(times),
            "std_seconds": _stdev(times),
            "input_tokens": _mean([r.input_tokens for r in ok if r.input_tokens is not None]),
            "output_tokens": _mean([r.output_tokens for r in ok if r.output_tokens is not None]),
            "total_tokens": _mean([r.total_tokens for r in ok if r.total_tokens is not None]),
            "tool_calls": _mean([r.tool_calls for r in ok if r.tool_calls is not None]),
        }
    return summary


def render_markdown(records: list[BenchmarkRecord]) -> str:
    if not records:
        return "_No benchmark records found._\n"

    summary = summarize(records)
    models = sorted({r.model for r in records})
    providers = sorted({r.provider for r in records})
    temperatures = sorted({r.temperature for r in records})

    lines: list[str] = [
        "# Benchmark results",
        "",
        f"- Runs recorded: **{len(records)}**",
        f"- Provider(s): `{'`, `'.join(providers)}`",
        f"- Model(s): `{'`, `'.join(models)}`",
        f"- Temperature(s): `{'`, `'.join(str(t) for t in temperatures)}`",
        "",
        "> Latency depends on network, provider load, library version and prompt. "
        "These numbers describe *this* run, not an absolute ranking of the frameworks.",
        "",
    ]

    for scenario in sorted({s for s, _ in summary}):
        lines += [
            f"## Scenario: `{scenario}`",
            "",
            "| Framework | Runs | Failures | Latency (s) | Input tokens | Output tokens | Total tokens | Tool calls |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        rows = [(f, data) for (s, f), data in summary.items() if s == scenario]
        rows.sort(key=lambda item: (item[1]["mean_seconds"] is None, item[1]["mean_seconds"] or 0))
        for framework, data in rows:
            latency = (
                "—"
                if data["mean_seconds"] is None
                else f"{data['mean_seconds']:.2f} ± {data['std_seconds']:.2f}"
            )
            lines.append(
                f"| {_label(framework)} | {data['runs']} | {data['failures']} | {latency} "
                f"| {_fmt(data['input_tokens'])} | {_fmt(data['output_tokens'])} "
                f"| {_fmt(data['total_tokens'])} | {_fmt(data['tool_calls'], 2)} |"
            )
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", type=Path, help="JSONL result files.")
    parser.add_argument("-o", "--output", type=Path, help="Write Markdown here instead of stdout.")
    args = parser.parse_args(argv)

    missing = [p for p in args.results if not p.exists()]
    if missing:
        parser.error(f"File(s) not found: {', '.join(str(p) for p in missing)}")

    records: list[BenchmarkRecord] = []
    for path in args.results:
        records.extend(load_records(path))

    markdown = render_markdown(records)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        # The tables use "±" and "—"; a legacy Windows console would otherwise
        # raise UnicodeEncodeError instead of printing the report.
        reconfigure = getattr(sys.stdout, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
