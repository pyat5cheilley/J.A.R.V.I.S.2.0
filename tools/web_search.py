"""Web search tool for J.A.R.V.I.S. 2.0

Provides real-time web search capabilities using DuckDuckGo's API
to supplement the local knowledgebase with up-to-date information.
"""

import os
import requests
from typing import Optional
from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).

    Returns:
        A list of dicts with 'title', 'href', and 'body' keys.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        print(f"[web_search] Search failed: {e}")
    return results


def format_search_results(results: list[dict]) -> str:
    """Format search results into a readable string for the LLM context.

    Args:
        results: List of search result dicts from search_web().

    Returns:
        A formatted string summarising the search results.
    """
    if not results:
        return "No web search results found."

    lines = ["**Web Search Results:**"]
    for i, r in enumerate(results, start=1):
        lines.append(f"\n[{i}] {r['title']}")
        lines.append(f"    URL: {r['url']}")
        lines.append(f"    {r['snippet']}")
    return "\n".join(lines)


def search_news(query: str, max_results: int = 5) -> list[dict]:
    """Search for recent news articles using DuckDuckGo News.

    Args:
        query: The news search query.
        max_results: Maximum number of articles to return.

    Returns:
        A list of dicts with 'title', 'url', 'date', and 'body' keys.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "date": r.get("date", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        print(f"[web_search] News search failed: {e}")
    return results


def should_search_web(user_message: str) -> bool:
    """Heuristic to decide whether a web search would benefit the response.

    Triggers a search for queries that hint at real-time or factual data.

    Args:
        user_message: The raw user input string.

    Returns:
        True if a web search is recommended, False otherwise.
    """
    trigger_keywords = [
        "latest", "current", "today", "news", "recent", "update",
        "price", "weather", "stock", "score", "who is", "what is",
        "when did", "how much", "search", "look up", "find"
    ]
    lower = user_message.lower()
    return any(kw in lower for kw in trigger_keywords)


if __name__ == "__main__":
    # Quick smoke test
    query = "Python 3.13 new features"
    results = search_web(query, max_results=3)
    print(format_search_results(results))
