"""Guardrails that keep known regressions from coming back."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent

AGENT_MODULES = sorted(PROJECT_ROOT.glob("*_agent.py"))
PYTHON_FILES = [
    path
    for path in REPO_ROOT.rglob("*.py")
    if ".venv" not in path.parts and "__pycache__" not in path.parts
]


def test_agent_modules_were_discovered():
    assert AGENT_MODULES, "no *_agent.py modules found"


@pytest.mark.parametrize("path", AGENT_MODULES, ids=lambda p: p.name)
def test_every_agent_module_exposes_an_agent_class(path: Path):
    """The UI and the benchmark adapters both rely on module.Agent."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    } | {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert "Agent" in names


@pytest.mark.parametrize("path", AGENT_MODULES, ids=lambda p: p.name)
def test_agent_chat_returns_the_shared_contract(path: Path):
    """chat() must return AgentResult on success and on failure alike."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    chat_functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "chat"
    ]
    assert chat_functions, f"{path.name} defines no chat()"

    for func in chat_functions:
        returns = [n for n in ast.walk(func) if isinstance(n, ast.Return) and n.value]
        assert returns, f"{path.name}: chat() returns nothing"
        for node in returns:
            rendered = ast.dump(node.value)
            assert "AgentResult" in rendered, (
                f"{path.name}: chat() returns something other than AgentResult"
            )


@pytest.mark.parametrize("path", PYTHON_FILES, ids=lambda p: p.name)
def test_no_disabled_tls_verification(path: Path):
    source = path.read_text(encoding="utf-8", errors="ignore")
    assert not re.search(r"verify\s*=\s*False", source), (
        f"{path} disables TLS certificate verification"
    )


@pytest.mark.parametrize("path", PYTHON_FILES, ids=lambda p: p.name)
def test_no_hardcoded_credential_literals(path: Path):
    """Credential-shaped assignments must come from the environment."""
    source = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"""(?ix)
        \b(api[_-]?key|token|secret|password)\s*[:=]\s*
        ["'](?!\s*$)(?![A-Za-z_]*your[-_])[A-Za-z0-9\-_]{16,}["']
        """
    )
    matches = pattern.findall(source)
    assert not matches, f"{path} looks like it contains a hardcoded credential"


def test_env_example_lists_every_setting_field():
    """A new setting must not silently go undocumented."""
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from settings import Settings

    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").lower()
    for field in Settings.model_fields:
        assert field.lower() in env_example, f"{field} missing from .env.example"


def test_env_example_contains_no_values_that_look_like_real_secrets():
    for line in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        _, _, value = line.partition("=")
        value = value.strip()
        assert len(value) < 40, f"suspiciously long placeholder: {line}"
