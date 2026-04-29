import json
import os
import time
from typing import Optional

CACHE_FILE = "DATA/location_cache.json"
CACHE_TTL_SECONDS = 3600  # 1 hour


def _load_raw() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_raw(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_cached_location(key: str) -> Optional[dict]:
    """Retrieve a cached location entry if it exists and is still fresh."""
    cache = _load_raw()
    entry = cache.get(key)
    if not entry:
        return None
    if time.time() - entry.get("timestamp", 0) > CACHE_TTL_SECONDS:
        return None
    return entry.get("data")


def set_cached_location(key: str, data: dict) -> None:
    """Store a location result in the cache with a timestamp."""
    cache = _load_raw()
    cache[key] = {"timestamp": time.time(), "data": data}
    _save_raw(cache)


def clear_cache() -> None:
    """Remove all cached location entries."""
    _save_raw({})


def purge_expired() -> int:
    """Remove expired entries and return count removed."""
    cache = _load_raw()
    now = time.time()
    fresh = {k: v for k, v in cache.items() if now - v.get("timestamp", 0) <= CACHE_TTL_SECONDS}
    removed = len(cache) - len(fresh)
    _save_raw(fresh)
    return removed
