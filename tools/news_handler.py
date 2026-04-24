import os
import json
from datetime import datetime
from tools.web_search import search_news

NEWS_CACHE_FILE = "DATA/news_cache.json"
DEFAULT_TOPICS = ["technology", "world", "science"]


def load_news_cache() -> dict:
    """Load cached news from disk."""
    if os.path.exists(NEWS_CACHE_FILE):
        try:
            with open(NEWS_CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_news_cache(cache: dict) -> None:
    """Persist news cache to disk."""
    os.makedirs(os.path.dirname(NEWS_CACHE_FILE), exist_ok=True)
    with open(NEWS_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_top_headlines(topic: str = "world", max_results: int = 5) -> list[dict]:
    """Fetch top headlines for a given topic, using cache if fresh."""
    cache = load_news_cache()
    now = datetime.utcnow().isoformat()

    if topic in cache:
        cached_at = cache[topic].get("fetched_at", "")
        if cached_at:
            age_seconds = (datetime.utcnow() - datetime.fromisoformat(cached_at)).total_seconds()
            if age_seconds < 1800:  # 30-minute cache
                return cache[topic].get("articles", [])[:max_results]

    raw_results = search_news(topic, max_results=max_results)
    articles = []
    for item in raw_results:
        articles.append({
            "title": item.get("title", "No title"),
            "source": item.get("source", "Unknown"),
            "url": item.get("url", ""),
            "snippet": item.get("snippet", ""),
            "published": item.get("published", "")
        })

    cache[topic] = {"fetched_at": now, "articles": articles}
    save_news_cache(cache)
    return articles[:max_results]


def format_headlines(articles: list[dict]) -> str:
    """Format a list of article dicts into a readable string."""
    if not articles:
        return "No headlines found."
    lines = []
    for i, article in enumerate(articles, 1):
        source = f" [{article['source']}]" if article.get("source") else ""
        lines.append(f"{i}. {article['title']}{source}")
        if article.get("snippet"):
            lines.append(f"   {article['snippet']}")
    return "\n".join(lines)


def get_news_digest(topics: list[str] = None, max_per_topic: int = 3) -> str:
    """Build a multi-topic news digest string."""
    topics = topics or DEFAULT_TOPICS
    sections = []
    for topic in topics:
        articles = get_top_headlines(topic, max_results=max_per_topic)
        formatted = format_headlines(articles)
        sections.append(f"=== {topic.upper()} ===\n{formatted}")
    return "\n\n".join(sections)
