"""Shared tool implementations. HTTP is mocked; no network access."""

from __future__ import annotations

import json

import httpx
import pytest

from shared_functions import F1API, Generic, MetroAPI
from shared_functions.base_module import BaseModule


class _FakeResponse:
    def __init__(self, status_code: int, payload: object | None = None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


# --------------------------------------------------------------------------
# Generic
# --------------------------------------------------------------------------

def test_generic_arithmetic_returns_json():
    assert json.loads(Generic.add(2, 3)) == {"operation": "addition", "result": 5}
    assert json.loads(Generic.multiply(4, 5))["result"] == 20
    assert json.loads(Generic.subtract(9, 4))["result"] == 5
    assert json.loads(Generic.divide(10, 4))["result"] == 2.5


def test_generic_current_date_is_iso_like():
    payload = json.loads(Generic.get_current_date())
    assert payload["operation"] == "current date"
    assert len(payload["result"]) == len("YYYY-MM-DD")


# --------------------------------------------------------------------------
# F1 API
# --------------------------------------------------------------------------

def test_f1_driver_info_returns_payload(monkeypatch):
    monkeypatch.setattr(
        httpx, "get", lambda url, **kw: _FakeResponse(200, [{"driver_number": 44}])
    )
    assert json.loads(F1API.get_driver_info(44)) == [{"driver_number": 44}]


def test_f1_driver_info_reports_http_error_status(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda url, **kw: _FakeResponse(503))
    assert "503" in F1API.get_driver_info(44)


def test_f1_driver_info_survives_transport_errors(monkeypatch):
    def _boom(url, **kw):
        raise httpx.ConnectError("dns failure")

    monkeypatch.setattr(httpx, "get", _boom)
    result = F1API.get_driver_info(44)
    assert result.startswith("Failed to get driver information")


def test_f1_request_sets_a_timeout(monkeypatch):
    captured = {}

    def _capture(url, **kw):
        captured.update(kw)
        return _FakeResponse(200, [])

    monkeypatch.setattr(httpx, "get", _capture)
    F1API.get_driver_info(1)
    assert captured["timeout"] > 0


# --------------------------------------------------------------------------
# Metro API — token handling and TLS
# --------------------------------------------------------------------------

def test_metro_requires_a_token_from_the_environment(monkeypatch):
    monkeypatch.delenv("METRO_API_TOKEN", raising=False)
    result = MetroAPI.get_state_subway()
    assert "METRO_API_TOKEN" in result


def test_metro_sends_the_token_from_the_environment(monkeypatch):
    monkeypatch.setenv("METRO_API_TOKEN", "unit-test-token")
    captured = {}

    def _capture(url, **kw):
        captured.update(kw)
        return _FakeResponse(200, {"ok": True})

    monkeypatch.setattr(httpx, "get", _capture)
    MetroAPI.get_state_subway()
    assert captured["headers"]["Authorization"] == "Bearer unit-test-token"


def test_metro_never_disables_tls_verification(monkeypatch):
    monkeypatch.setenv("METRO_API_TOKEN", "unit-test-token")
    captured = {}

    def _capture(url, **kw):
        captured.update(kw)
        return _FakeResponse(200, {"ok": True})

    monkeypatch.setattr(httpx, "get", _capture)
    MetroAPI.get_state_subway()
    assert captured.get("verify", True) is not False


def test_metro_next_subways_returns_two_lowest_times(monkeypatch):
    monkeypatch.setenv("METRO_API_TOKEN", "unit-test-token")
    payload = {
        "resposta": [
            {"tempoChegada1": "300"},
            {"tempoChegada1": "60"},
            {"tempoChegada1": "120"},
        ]
    }
    monkeypatch.setattr(httpx, "get", lambda url, **kw: _FakeResponse(200, payload))
    result = json.loads(MetroAPI.get_times_next_two_subways_in_station("CG"))
    assert result == {"times": [60, 120], "metric": "seconds"}


def test_metro_survives_transport_errors(monkeypatch):
    monkeypatch.setenv("METRO_API_TOKEN", "unit-test-token")

    def _boom(url, **kw):
        raise httpx.ReadTimeout("too slow")

    monkeypatch.setattr(httpx, "get", _boom)
    assert MetroAPI.get_times_next_two_subways_in_station("CG").startswith("Failed")


# --------------------------------------------------------------------------
# BaseModule tool discovery
# --------------------------------------------------------------------------

def test_list_functions_exposes_public_tools_with_docstrings():
    names = dict(F1API.list_functions())
    assert "get_driver_info" in names
    assert names["get_driver_info"].strip()


def test_list_functions_hides_private_helpers():
    names = [name for name, _ in MetroAPI.list_functions()]
    assert "_headers" not in names
    assert "list_functions" not in names


def test_list_functions_falls_back_when_docstring_missing():
    class _Undocumented(BaseModule):
        @staticmethod
        def bare():
            pass

    assert dict(_Undocumented.list_functions())["bare"] == "No description available."


@pytest.mark.integration
def test_f1_api_live_call():
    """Hits the public OpenF1 API. Run with `pytest -m integration`."""
    payload = json.loads(F1API.get_driver_info(44))
    assert isinstance(payload, list)
