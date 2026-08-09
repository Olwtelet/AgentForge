"""Reproducible cross-framework benchmarks for AgentForge.

Layout:
    adapters.py   -> maps a framework id to the agent module/class that implements it
    scenarios.py  -> scenario definitions + dataset loading
    runner.py     -> executes scenarios and writes JSONL results
    report.py     -> turns JSONL results into Markdown tables
    datasets/     -> the prompts each scenario runs
    results/      -> JSONL output (git-ignored except for .gitkeep)
"""

from benchmarks.records import BenchmarkRecord, load_records, write_records
from benchmarks.scenarios import Scenario, load_scenarios

__all__ = [
    "BenchmarkRecord",
    "Scenario",
    "load_records",
    "load_scenarios",
    "write_records",
]
