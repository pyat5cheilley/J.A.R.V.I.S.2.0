"""Tests for tools/quote_handler.py"""

import json
import time
import pytest
from unittest.mock import patch, MagicMock

from tools.quote_handler import (
    _load_cache,
    _save_cache,
    _cache_is_fresh,
    fetch_quotes,
    get_random_quote,
    format_quote,
    get_daily_quote,
    CACHE_FILE,
    FALLBACK_QUOTES,
)


@pytest.fixture(autouse=True)
patch_cache_file = pytest.fixture(autouse=True)(
    lambda tmp_path, monkeypatch: monkeypatch.setattr(
        "tools.quote_handler.CACHE_FILE", str(tmp_path / "quote_cache.json")
    )
)


def test_load_cache_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", str(tmp_path / "missing.json"))
    assert _load_cache() == {}


def test_save_and_load_cache(tmp_path, monkeypatch):
    path = str(tmp_path / "quote_cache.json")
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", path)
    data = {"timestamp": time.time(), "quotes": FALLBACK_QUOTES, "category": "inspire"}
    _save_cache(data)
    loaded = _load_cache()
    assert loaded["category"] == "inspire"
    assert len(loaded["quotes"]) == len(FALLBACK_QUOTES)


def test_cache_is_fresh_recent():
    cache = {"timestamp": time.time()}
    assert _cache_is_fresh(cache) is True


def test_cache_is_stale_old():
    cache = {"timestamp": time.time() - 90000}
    assert _cache_is_fresh(cache) is False


def test_fetch_quotes_uses_cache(tmp_path, monkeypatch):
    path = str(tmp_path / "quote_cache.json")
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", path)
    cached_quotes = [{"q": "Test quote", "a": "Tester"}]
    _save_cache({"timestamp": time.time(), "category": "inspire", "quotes": cached_quotes})
    with patch("tools.quote_handler.requests.get") as mock_get:
        result = fetch_quotes("inspire")
        mock_get.assert_not_called()
    assert result == cached_quotes


def test_fetch_quotes_falls_back_on_error(tmp_path, monkeypatch):
    path = str(tmp_path / "quote_cache.json")
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", path)
    with patch("tools.quote_handler.requests.get", side_effect=Exception("network error")):
        result = fetch_quotes("inspire")
    assert result == FALLBACK_QUOTES


def test_get_random_quote_returns_dict(tmp_path, monkeypatch):
    path = str(tmp_path / "quote_cache.json")
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", path)
    with patch("tools.quote_handler.requests.get", side_effect=Exception):
        quote = get_random_quote()
    assert "q" in quote and "a" in quote


def test_format_quote_output():
    quote = {"q": "Be yourself.", "a": "Oscar Wilde"}
    result = format_quote(quote)
    assert "Be yourself." in result
    assert "Oscar Wilde" in result
    assert result.startswith('"')


def test_get_daily_quote_returns_string(tmp_path, monkeypatch):
    path = str(tmp_path / "quote_cache.json")
    monkeypatch.setattr("tools.quote_handler.CACHE_FILE", path)
    with patch("tools.quote_handler.requests.get", side_effect=Exception):
        result = get_daily_quote()
    assert isinstance(result, str)
    assert "\u2014" in result  # em dash
