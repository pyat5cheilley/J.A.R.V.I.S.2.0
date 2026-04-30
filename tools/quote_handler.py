"""Quote of the day handler for J.A.R.V.I.S.2.0"""

import os
import json
import random
import time
import requests
from datetime import datetime

CACHE_FILE = "DATA/quote_cache.json"
CACHE_TTL = 86400  # 24 hours
FALLBACK_QUOTES = [
    {"q": "The only way to do great work is to love what you do.", "a": "Steve Jobs"},
    {"q": "In the middle of every difficulty lies opportunity.", "a": "Albert Einstein"},
    {"q": "It does not matter how slowly you go as long as you do not stop.", "a": "Confucius"},
    {"q": "Life is what happens when you're busy making other plans.", "a": "John Lennon"},
    {"q": "The future belongs to those who believe in the beauty of their dreams.", "a": "Eleanor Roosevelt"},
]


def _load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _cache_is_fresh(cache: dict) -> bool:
    ts = cache.get("timestamp", 0)
    return (time.time() - ts) < CACHE_TTL


def fetch_quotes(category: str = "inspire") -> list:
    """Fetch quotes from ZenQuotes API or return fallback list."""
    cache = _load_cache()
    if cache.get("category") == category and _cache_is_fresh(cache):
        return cache.get("quotes", [])

    try:
        url = f"https://zenquotes.io/api/quotes/{category}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        quotes = resp.json()
        if isinstance(quotes, list) and quotes:
            _save_cache({"timestamp": time.time(), "category": category, "quotes": quotes})
            return quotes
    except Exception:
        pass

    return FALLBACK_QUOTES


def get_random_quote(category: str = "inspire") -> dict:
    """Return a single random quote dict with keys 'q' (text) and 'a' (author)."""
    quotes = fetch_quotes(category)
    return random.choice(quotes)


def format_quote(quote: dict) -> str:
    """Format a quote dict into a human-readable string."""
    text = quote.get("q", "No quote available.")
    author = quote.get("a", "Unknown")
    return f'"{text}"\n  — {author}'


def get_daily_quote() -> str:
    """Return today's deterministic quote (same quote all day)."""
    quotes = fetch_quotes()
    day_index = datetime.now().timetuple().tm_yday
    quote = quotes[day_index % len(quotes)]
    return format_quote(quote)
