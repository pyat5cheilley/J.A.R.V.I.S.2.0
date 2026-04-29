import json
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import tools.joke_handler as jh

TEST_CACHE = "DATA/joke_cache_test.json"


@pytest.fixture(autouse=True)
def patch_cache_file(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "joke_cache.json")
    monkeypatch.setattr(jh, "JOKE_CACHE_FILE", cache_path)
    yield cache_path
    if os.path.exists(cache_path):
        os.remove(cache_path)


def test_load_cache_missing_file(patch_cache_file):
    cache = jh._load_cache()
    assert cache == {"timestamp": None, "jokes": []}


def test_save_and_load_cache(patch_cache_file):
    data = {"timestamp": datetime.utcnow().isoformat(), "jokes": ["Test joke"]}
    jh._save_cache(data)
    loaded = jh._load_cache()
    assert loaded["jokes"] == ["Test joke"]


def test_cache_is_fresh_with_recent_timestamp():
    cache = {
        "timestamp": datetime.utcnow().isoformat(),
        "jokes": ["A fresh joke"],
    }
    assert jh._cache_is_fresh(cache) is True


def test_cache_is_stale_with_old_timestamp():
    old_ts = (datetime.utcnow() - timedelta(hours=10)).isoformat()
    cache = {"timestamp": old_ts, "jokes": ["Old joke"]}
    assert jh._cache_is_fresh(cache) is False


def test_fetch_jokes_uses_cache_when_fresh(patch_cache_file):
    fresh_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "jokes": ["Cached joke"],
    }
    jh._save_cache(fresh_data)
    jokes = jh.fetch_jokes()
    assert jokes == ["Cached joke"]


def test_fetch_jokes_calls_api_when_stale(patch_cache_file):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "jokes": [
            {"type": "single", "joke": "API joke one"},
            {"type": "twopart", "setup": "Why?", "delivery": "Because!"},
        ]
    }
    with patch("tools.joke_handler.requests.get", return_value=mock_response):
        jokes = jh.fetch_jokes()
    assert "API joke one" in jokes
    assert "Why? ... Because!" in jokes


def test_get_random_joke_returns_string(patch_cache_file):
    with patch("tools.joke_handler.fetch_jokes", return_value=["Ha!", "Ho!"]):
        joke = jh.get_random_joke()
    assert isinstance(joke, str)
    assert joke in ["Ha!", "Ho!"]


def test_format_joke_prefix():
    result = jh.format_joke("Why so serious?")
    assert result.startswith("😄")
    assert "Why so serious?" in result
