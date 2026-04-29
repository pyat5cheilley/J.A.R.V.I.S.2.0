import os
import json
import random
import requests
from datetime import datetime, timedelta

JOKE_CACHE_FILE = "DATA/joke_cache.json"
CACHE_TTL_HOURS = 6
JOKE_API_URL = "https://v2.jokeapi.dev/joke/Any"


def _load_cache() -> dict:
    if os.path.exists(JOKE_CACHE_FILE):
        try:
            with open(JOKE_CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"timestamp": None, "jokes": []}


def _save_cache(data: dict) -> None:
    os.makedirs(os.path.dirname(JOKE_CACHE_FILE), exist_ok=True)
    with open(JOKE_CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _cache_is_fresh(cache: dict) -> bool:
    if not cache.get("timestamp") or not cache.get("jokes"):
        return False
    ts = datetime.fromisoformat(cache["timestamp"])
    return datetime.utcnow() - ts < timedelta(hours=CACHE_TTL_HOURS)


def fetch_jokes(amount: int = 5, blacklist: list = None) -> list:
    """Fetch jokes from JokeAPI, using cache when fresh."""
    cache = _load_cache()
    if _cache_is_fresh(cache):
        return cache["jokes"]

    params = {
        "amount": amount,
        "type": "single,twopart",
        "safe-mode": "",
    }
    if blacklist:
        params["blacklistFlags"] = ",".join(blacklist)

    try:
        resp = requests.get(JOKE_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        jokes_raw = data.get("jokes", [data]) if "jokes" in data else [data]
        jokes = []
        for j in jokes_raw:
            if j.get("type") == "single":
                jokes.append(j["joke"])
            elif j.get("type") == "twopart":
                jokes.append(f"{j['setup']} ... {j['delivery']}")
        if jokes:
            _save_cache({"timestamp": datetime.utcnow().isoformat(), "jokes": jokes})
            return jokes
    except (requests.RequestException, KeyError, ValueError):
        pass

    return cache.get("jokes") or ["Why don't scientists trust atoms? Because they make up everything!"]


def get_random_joke(blacklist: list = None) -> str:
    """Return a single random joke string."""
    jokes = fetch_jokes(blacklist=blacklist)
    return random.choice(jokes) if jokes else "I'm all out of jokes right now!"


def format_joke(joke: str) -> str:
    """Format a joke for display."""
    return f"😄 {joke}"
