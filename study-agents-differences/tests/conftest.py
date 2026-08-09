"""Shared pytest fixtures.

Unit tests must run without any credentials, so the project root is put on
``sys.path`` and dummy environment values are provided before ``settings`` is
imported by anything under test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests from picking up a developer's real .env values."""
    for key in (
        "OPENAI_API_KEY",
        "AZURE_API_KEY",
        "TAVILY_API_KEY",
        "METRO_API_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)
        monkeypatch.delenv(key.lower(), raising=False)
