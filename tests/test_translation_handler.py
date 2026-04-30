"""Tests for tools/translation_handler.py"""

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import tools.translation_handler as th


@pytest.fixture(autouse=True)
def patch_cache_file(tmp_path, monkeypatch):
    cache = tmp_path / "translation_cache.json"
    monkeypatch.setattr(th, "_CACHE_FILE", cache)
    yield cache


def _mock_translate_response(translated: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"translatedText": translated}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_resolve_lang_alias():
    assert th._resolve_lang("French") == "fr"
    assert th._resolve_lang("GERMAN") == "de"


def test_resolve_lang_passthrough():
    assert th._resolve_lang("pt") == "pt"


def test_load_cache_missing_file(patch_cache_file):
    assert th._load_cache() == {}


def test_save_and_load_cache(patch_cache_file):
    th._save_cache({"key": {"result": "hola", "ts": 1}})
    data = th._load_cache()
    assert data["key"]["result"] == "hola"


def test_translate_text_success(patch_cache_file):
    with patch("tools.translation_handler.requests.post",
               return_value=_mock_translate_response("Bonjour")) as mock_post:
        result = th.translate_text("Hello", "french")
    assert result == "Bonjour"
    mock_post.assert_called_once()


def test_translate_text_uses_cache(patch_cache_file):
    cache_key = "auto|fr|Hello"
    th._save_cache({cache_key: {"result": "Bonjour", "ts": time.time()}})
    with patch("tools.translation_handler.requests.post") as mock_post:
        result = th.translate_text("Hello", "fr")
    assert result == "Bonjour"
    mock_post.assert_not_called()


def test_translate_text_expired_cache(patch_cache_file):
    cache_key = "auto|fr|Hello"
    th._save_cache({cache_key: {"result": "OldValue", "ts": time.time() - 999999}})
    with patch("tools.translation_handler.requests.post",
               return_value=_mock_translate_response("Bonjour")):
        result = th.translate_text("Hello", "fr")
    assert result == "Bonjour"


def test_translate_text_api_failure(patch_cache_file):
    with patch("tools.translation_handler.requests.post", side_effect=Exception("err")):
        result = th.translate_text("Hello", "es")
    assert result is None


def test_detect_language_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"language": "en", "confidence": 0.99}]
    mock_resp.raise_for_status = MagicMock()
    with patch("tools.translation_handler.requests.post", return_value=mock_resp):
        lang = th.detect_language("Hello world")
    assert lang == "en"


def test_detect_language_failure():
    with patch("tools.translation_handler.requests.post", side_effect=Exception("err")):
        lang = th.detect_language("Hello")
    assert lang is None


def test_format_translation():
    out = th.format_translation("Hello", "Hola", "es")
    assert "ES" in out
    assert "Hola" in out
    assert "Hello" in out
