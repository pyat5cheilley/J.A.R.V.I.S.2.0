"""Standalone cache helpers for translation results (mirrors location_cache pattern)."""

import json
import time
from pathlib import Path
from typing import Optional

_CACHE_FILE = Path("DATA/translation_cache.json")
_DEFAULT_TTL = 86400  # 24 hours


def _load_raw() -> dict:
    if _CACHE_FILE.exists():
        try:
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_raw(data: dict) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_cached_translation(key: str, ttl: int = _DEFAULT_TTL) -> Optional[str]:
    """Return cached translation for *key* if still fresh, else None."""
    data = _load_raw()
    entry = data.get(key)
    if entry and (time.time() - entry.get("ts", 0)) < ttl:
        return entry.get("result")
    return None


def set_cached_translation(key: str, result: str) -> None:
    """Persist a translation result under *key*."""
    data = _load_raw()
    data[key] = {"result": result, "ts": time.time()}
    _save_raw(data)


def clear_cache() -> None:
    """Remove all cached translations."""
    _save_raw({})


def cache_size() -> int:
    """Return the number of entries currently in the cache."""
    return len(_load_raw())
