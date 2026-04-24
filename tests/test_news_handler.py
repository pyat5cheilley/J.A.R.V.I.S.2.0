import json
import os
import pytest
from unittest.mock import patch, MagicMock
from tools.news_handler import (
    load_news_cache,
    save_news_cache,
    get_top_headlines,
    format_headlines,
    get_news_digest,
    NEWS_CACHE_FILE,
)

SAMPLE_ARTICLES = [
    {"title": "AI Breakthrough", "source": "TechNews", "url": "http://example.com/1", "snippet": "New model released.", "published": "2024-01-01"},
    {"title": "Space Mission Launched", "source": "SpaceDaily", "url": "http://example.com/2", "snippet": "Rocket heads to Mars.", "published": "2024-01-02"},
]


@pytest.fixture(autouse=True)
def cleanup_cache(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "news_cache.json")
    monkeypatch.setattr("tools.news_handler.NEWS_CACHE_FILE", cache_path)
    yield
    if os.path.exists(cache_path):
        os.remove(cache_path)


def test_load_news_cache_missing_file():
    cache = load_news_cache()
    assert cache == {}


def test_save_and_load_cache(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "news_cache.json")
    monkeypatch.setattr("tools.news_handler.NEWS_CACHE_FILE", cache_path)
    data = {"tech": {"fetched_at": "2024-01-01T00:00:00", "articles": SAMPLE_ARTICLES}}
    save_news_cache(data)
    loaded = load_news_cache()
    assert "tech" in loaded
    assert len(loaded["tech"]["articles"]) == 2


@patch("tools.news_handler.search_news")
def test_get_top_headlines_fetches_and_caches(mock_search):
    mock_search.return_value = SAMPLE_ARTICLES
    articles = get_top_headlines("technology", max_results=2)
    assert len(articles) == 2
    assert articles[0]["title"] == "AI Breakthrough"
    mock_search.assert_called_once()


@patch("tools.news_handler.search_news")
def test_get_top_headlines_uses_cache(mock_search):
    from datetime import datetime
    mock_search.return_value = SAMPLE_ARTICLES
    # Prime the cache
    get_top_headlines("technology", max_results=2)
    mock_search.reset_mock()
    # Second call should use cache
    articles = get_top_headlines("technology", max_results=2)
    mock_search.assert_not_called()
    assert len(articles) == 2


def test_format_headlines_empty():
    result = format_headlines([])
    assert result == "No headlines found."


def test_format_headlines_with_articles():
    result = format_headlines(SAMPLE_ARTICLES)
    assert "AI Breakthrough" in result
    assert "TechNews" in result
    assert "New model released." in result


@patch("tools.news_handler.get_top_headlines")
def test_get_news_digest(mock_headlines):
    mock_headlines.return_value = SAMPLE_ARTICLES[:1]
    digest = get_news_digest(topics=["tech", "world"], max_per_topic=1)
    assert "TECH" in digest
    assert "WORLD" in digest
    assert mock_headlines.call_count == 2
