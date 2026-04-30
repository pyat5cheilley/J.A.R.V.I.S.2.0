"""Translation handler using LibreTranslate (free, open API)."""

import os
import json
import time
from pathlib import Path
from typing import Optional
import requests

_CACHE_FILE = Path("DATA/translation_cache.json")
_CACHE_TTL = 86400  # 24 hours
_API_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")
_API_KEY = os.getenv("LIBRETRANSLATE_KEY", "")

LANG_ALIASES: dict[str, str] = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja",
    "arabic": "ar",
    "hindi": "hi",
    "korean": "ko",
}


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        try:
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(data: dict) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_lang(lang: str) -> str:
    """Normalise a language name or code to an ISO 639-1 code."""
    return LANG_ALIASES.get(lang.lower(), lang.lower())


def translate_text(text: str, target: str, source: str = "auto") -> Optional[str]:
    """Translate *text* to *target* language.  Returns translated string or None."""
    target = _resolve_lang(target)
    source = _resolve_lang(source) if source != "auto" else "auto"

    cache_key = f"{source}|{target}|{text}"
    cache = _load_cache()
    entry = cache.get(cache_key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["result"]

    payload: dict = {"q": text, "source": source, "target": target, "format": "text"}
    if _API_KEY:
        payload["api_key"] = _API_KEY

    try:
        resp = requests.post(f"{_API_URL}/translate", json=payload, timeout=10)
        resp.raise_for_status()
        result: str = resp.json()["translatedText"]
    except (requests.RequestException, KeyError):
        return None

    cache[cache_key] = {"result": result, "ts": time.time()}
    _save_cache(cache)
    return result


def detect_language(text: str) -> Optional[str]:
    """Detect the language of *text*.  Returns ISO 639-1 code or None."""
    payload: dict = {"q": text}
    if _API_KEY:
        payload["api_key"] = _API_KEY
    try:
        resp = requests.post(f"{_API_URL}/detect", json=payload, timeout=10)
        resp.raise_for_status()
        detections: list = resp.json()
        if detections:
            return detections[0].get("language")
    except (requests.RequestException, KeyError, IndexError):
        pass
    return None


def format_translation(original: str, translated: str, target: str) -> str:
    """Return a human-readable translation result string."""
    return f"[{target.upper()}] {translated}  (original: \"{original}\")"
