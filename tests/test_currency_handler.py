"""Tests for tools/currency_handler.py"""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import tools.currency_handler as ch


@pytest.fixture(autouse=True)
def patch_cache_file(tmp_path, monkeypatch):
    cache = tmp_path / "currency_cache.json"
    monkeypatch.setattr(ch, "CACHE_FILE", cache)
    yield cache


def _mock_rates_response(base="USD"):
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {"rates": {"EUR": 0.92, "GBP": 0.79, "INR": 83.1}}
    return mock


def test_resolve_currency_alias():
    assert ch._resolve_currency("dollar") == "USD"
    assert ch._resolve_currency("euro") == "EUR"
    assert ch._resolve_currency("yen") == "JPY"


def test_resolve_currency_passthrough():
    assert ch._resolve_currency("CHF") == "CHF"
    assert ch._resolve_currency("cad") == "CAD"


def test_load_cache_missing_file(patch_cache_file):
    assert ch._load_cache() == {}


def test_save_and_load_cache(patch_cache_file):
    data = {"base": "USD", "rates": {"EUR": 0.92}, "timestamp": time.time()}
    ch._save_cache(data)
    loaded = ch._load_cache()
    assert loaded["base"] == "USD"
    assert loaded["rates"]["EUR"] == 0.92


def test_cache_is_fresh_recent():
    cache = {"timestamp": time.time() - 100}
    assert ch._cache_is_fresh(cache) is True


def test_cache_is_stale_old():
    cache = {"timestamp": time.time() - 7200}
    assert ch._cache_is_fresh(cache) is False


def test_get_exchange_rates_fetches_and_caches(patch_cache_file):
    with patch("tools.currency_handler.requests.get", return_value=_mock_rates_response()):
        rates = ch.get_exchange_rates("USD")
    assert "EUR" in rates
    assert patch_cache_file.exists()


def test_get_exchange_rates_uses_cache(patch_cache_file):
    cached = {"base": "USD", "rates": {"EUR": 0.91}, "timestamp": time.time()}
    ch._save_cache(cached)
    with patch("tools.currency_handler.requests.get") as mock_get:
        rates = ch.get_exchange_rates("USD")
        mock_get.assert_not_called()
    assert rates["EUR"] == 0.91


def test_convert_currency_success():
    with patch("tools.currency_handler.get_exchange_rates", return_value={"EUR": 0.92, "GBP": 0.79}):
        result = ch.convert_currency(100, "USD", "EUR")
    assert result["result"] == 92.0
    assert result["from"] == "USD"
    assert result["to"] == "EUR"


def test_convert_currency_unknown_target():
    with patch("tools.currency_handler.get_exchange_rates", return_value={"EUR": 0.92}):
        result = ch.convert_currency(50, "USD", "XYZ")
    assert "error" in result


def test_format_conversion_success():
    data = {"from": "USD", "to": "EUR", "amount": 100, "result": 92.0, "rate": 0.92}
    out = ch.format_conversion(data)
    assert "100 USD = 92.0 EUR" in out


def test_format_conversion_error():
    out = ch.format_conversion({"error": "not found"})
    assert "Error" in out
