import json
import time
import pytest
from unittest.mock import patch, MagicMock

import tools.trivia_handler as th


@pytest.fixture(autouse=True)
def patch_cache_file(tmp_path, monkeypatch):
    cache = tmp_path / "trivia_cache.json"
    monkeypatch.setattr(th, "CACHE_FILE", str(cache))
    yield cache


def _make_question(text="What is 2+2?", correct="4"):
    from urllib.parse import quote
    return {
        "question": quote(text),
        "correct_answer": quote(correct),
        "incorrect_answers": [quote("3"), quote("5"), quote("6")],
        "difficulty": "easy",
        "category": quote("Mathematics"),
    }


def test_load_cache_missing_file():
    cache = th._load_cache()
    assert cache["questions"] == []
    assert cache["timestamp"] == 0


def test_save_and_load_cache(patch_cache_file):
    data = {"timestamp": 999, "questions": [_make_question()]}
    th._save_cache(data)
    loaded = th._load_cache()
    assert loaded["timestamp"] == 999
    assert len(loaded["questions"]) == 1


def test_cache_is_fresh_recent():
    cache = {"timestamp": time.time() - 100, "questions": []}
    assert th._cache_is_fresh(cache) is True


def test_cache_is_stale_old():
    cache = {"timestamp": time.time() - 9999, "questions": []}
    assert th._cache_is_fresh(cache) is False


def test_fetch_trivia_uses_cache(patch_cache_file):
    fresh = {"timestamp": time.time(), "questions": [_make_question()]}
    th._save_cache(fresh)
    with patch("tools.trivia_handler.requests.get") as mock_get:
        result = th.fetch_trivia()
    mock_get.assert_not_called()
    assert len(result) == 1


def test_fetch_trivia_fetches_when_stale(patch_cache_file):
    stale = {"timestamp": 0, "questions": []}
    th._save_cache(stale)
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response_code": 0,
        "results": [_make_question(), _make_question("Capital of France?", "Paris")],
    }
    with patch("tools.trivia_handler.requests.get", return_value=mock_resp):
        result = th.fetch_trivia()
    assert len(result) == 2


def test_get_random_question_structure(patch_cache_file):
    fresh = {"timestamp": time.time(), "questions": [_make_question()]}
    th._save_cache(fresh)
    q = th.get_random_question()
    assert q is not None
    assert "question" in q
    assert "correct" in q
    assert "choices" in q
    assert len(q["choices"]) == 4


def test_format_question_output(patch_cache_file):
    fresh = {"timestamp": time.time(), "questions": [_make_question()]}
    th._save_cache(fresh)
    q = th.get_random_question()
    text = th.format_question(q)
    assert "Trivia" in text
    assert q["correct"] in text


def test_format_question_none():
    result = th.format_question(None)
    assert "Could not load" in result
