"""The result contract every agent must honour."""

from __future__ import annotations

import json

import pytest

from agent_contract import AgentResult, TokenUsage, count_tool_calls


def test_success_result_reports_success():
    result = AgentResult(content="hello", elapsed_seconds=1.5)
    assert result.success is True
    assert result.error is None


def test_error_result_reports_failure():
    result = AgentResult.from_error(ValueError("boom"), elapsed_seconds=0.25)
    assert result.success is False
    assert result.error == "boom"
    assert result.content == ""
    assert result.elapsed_seconds == 0.25


def test_from_error_falls_back_to_exception_type_when_message_is_empty():
    result = AgentResult.from_error(RuntimeError())
    assert result.error == "RuntimeError"


def test_from_error_accepts_plain_strings():
    assert AgentResult.from_error("nope").error == "nope"


def test_to_dict_is_json_serializable():
    result = AgentResult(
        content="hi",
        elapsed_seconds=0.5,
        usage=TokenUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        tool_calls=2,
    )
    payload = json.loads(json.dumps(result.to_dict()))
    assert payload["success"] is True
    assert payload["usage"]["total_tokens"] == 15
    assert payload["tool_calls"] == 2


def test_to_dict_handles_missing_usage():
    payload = AgentResult(content="hi", elapsed_seconds=0.1).to_dict()
    assert payload["usage"] is None
    assert payload["tool_calls"] is None


def test_token_usage_from_legacy_counter():
    usage = TokenUsage.from_legacy_counter(
        {
            "prompt_llm_token_count": 100,
            "completion_llm_token_count": 20,
            "total_llm_token_count": 120,
            "total_embedding_token_count": 7,
        }
    )
    assert usage == TokenUsage(
        input_tokens=100, output_tokens=20, total_tokens=120, embedding_tokens=7
    )


@pytest.mark.parametrize("empty", [None, {}])
def test_token_usage_from_empty_counter_is_none(empty):
    assert TokenUsage.from_legacy_counter(empty) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), ([], 0), ([1, 2, 3], 3), (42, None)],
)
def test_count_tool_calls(value, expected):
    assert count_tool_calls(value) == expected
