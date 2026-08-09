"""Structured benchmark records (one JSON object per agent run)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

SCHEMA_VERSION = 1


@dataclass
class BenchmarkRecord:
    """A single agent execution.

    One record per (framework, scenario, prompt, iteration). Errors are recorded
    like any other run so failure rates stay visible instead of disappearing.
    """

    framework: str
    scenario: str
    prompt_id: str
    iteration: int
    model: str
    provider: str
    temperature: float
    memory: bool
    elapsed_seconds: float
    success: bool
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    tool_calls: int | None = None
    error: str | None = None
    response_preview: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def write_records(records: Iterable[BenchmarkRecord], path: str | Path) -> Path:
    """Append records to a JSONL file, creating parent directories if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    return path


def load_records(path: str | Path) -> list[BenchmarkRecord]:
    """Load records from a JSONL file, ignoring blank lines."""
    return list(_iter_records(Path(path)))


def _iter_records(path: Path) -> Iterator[BenchmarkRecord]:
    known = {f for f in BenchmarkRecord.__dataclass_fields__}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            yield BenchmarkRecord(**{k: v for k, v in data.items() if k in known})
