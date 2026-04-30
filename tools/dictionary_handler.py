"""Dictionary and word definition handler for J.A.R.V.I.S.2.0"""

import os
import json
import time
import requests
from typing import Optional

CACHE_FILE = "DATA/dictionary_cache.json"
CACHE_TTL = 86400 * 7  # 7 days
API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en"


def _load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _cache_is_fresh(entry: dict) -> bool:
    return time.time() - entry.get("timestamp", 0) < CACHE_TTL


def define_word(word: str) -> Optional[dict]:
    """Fetch definition(s) for a word. Returns parsed result or None."""
    word = word.strip().lower()
    cache = _load_cache()

    if word in cache and _cache_is_fresh(cache[word]):
        return cache[word]["data"]

    try:
        resp = requests.get(f"{API_BASE}/{word}", timeout=8)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        cache[word] = {"timestamp": time.time(), "data": data}
        _save_cache(cache)
        return data
    except requests.RequestException:
        return None


def format_definition(word: str, data: list) -> str:
    """Format raw API response into a human-readable string."""
    if not data:
        return f"No definition found for '{word}'."

    lines = [f"**{word.capitalize()}**"]
    entry = data[0]
    phonetic = entry.get("phonetic", "")
    if phonetic:
        lines.append(f"Pronunciation: {phonetic}")

    for meaning in entry.get("meanings", [])[:2]:
        part = meaning.get("partOfSpeech", "")
        lines.append(f"\n[{part}]")
        for defn in meaning.get("definitions", [])[:2]:
            lines.append(f"  • {defn.get('definition', '')}")
            example = defn.get("example", "")
            if example:
                lines.append(f'    e.g. "{example}"')

    return "\n".join(lines)


def get_definition(word: str) -> str:
    """High-level helper: define a word and return formatted string."""
    data = define_word(word)
    if data is None:
        return f"Sorry, I couldn't find a definition for '{word}'."
    return format_definition(word, data)
