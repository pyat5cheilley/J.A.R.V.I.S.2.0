"""Tests for tools/dictionary_handler.py"""

import json
import time
import pytest
from unittest.mock import patch, MagicMock

import tools.dictionary_handler as dh


@pytest.fixture(autouse=True)
def patch_cache_file(tmp_path, monkeypatch):
    cache = tmp_path / "dictionary_cache.json"
    monkeypatch.setattr(dh, "CACHE_FILE", str(cache))
    yield cache


def test_load_cache_missing_file():
    result = dh._load_cache()
    assert result == {}


def test_save_and_load_cache(patch_cache_file):
    data = {"hello": {"timestamp": time.time(), "data": [{"word": "hello"}]}}
    dh._save_cache(data)
    loaded = dh._load_cache()
    assert "hello" in loaded
    assert loaded["hello"]["data"][0]["word"] == "hello"


def test_cache_is_fresh_recent():
    entry = {"timestamp": time.time()}
    assert dh._cache_is_fresh(entry) is True


def test_cache_is_stale_old():
    entry = {"timestamp": time.time() - (86400 * 10)}
    assert dh._cache_is_fresh(entry) is False


def _mock_api_response():
    return [
        {
            "word": "serendipity",
            "phonetic": "/ˌsɛr.ənˈdɪp.ɪ.ti/",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "The occurrence of events by chance in a happy way.",
                            "example": "A fortunate stroke of serendipity.",
                        }
                    ],
                }
            ],
        }
    ]


def test_define_word_fetches_and_caches():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _mock_api_response()

    with patch("tools.dictionary_handler.requests.get", return_value=mock_resp):
        result = dh.define_word("serendipity")

    assert result is not None
    assert result[0]["word"] == "serendipity"
    cache = dh._load_cache()
    assert "serendipity" in cache


def test_define_word_uses_cache():
    cache_data = {"serendipity": {"timestamp": time.time(), "data": _mock_api_response()}}
    dh._save_cache(cache_data)

    with patch("tools.dictionary_handler.requests.get") as mock_get:
        result = dh.define_word("serendipity")
        mock_get.assert_not_called()

    assert result[0]["word"] == "serendipity"


def test_define_word_not_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("tools.dictionary_handler.requests.get", return_value=mock_resp):
        result = dh.define_word("xyznonexistent")

    assert result is None


def test_get_definition_formats_output():
    with patch("tools.dictionary_handler.define_word", return_value=_mock_api_response()):
        output = dh.get_definition("serendipity")

    assert "Serendipity" in output
    assert "noun" in output
    assert "chance" in output


def test_get_definition_word_not_found():
    with patch("tools.dictionary_handler.define_word", return_value=None):
        output = dh.get_definition("xyzfake")

    assert "couldn't find" in output.lower()
