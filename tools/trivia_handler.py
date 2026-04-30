import os
import json
import random
import time
import requests
from typing import Optional

CACHE_FILE = "DATA/trivia_cache.json"
CACHE_TTL = 3600  # 1 hour
OPENTDB_URL = "https://opentdb.com/api.php"

CATEGORY_MAP = {
    "general": 9,
    "science": 17,
    "history": 23,
    "geography": 22,
    "sports": 21,
    "music": 12,
    "movies": 11,
    "computers": 18,
}


def _load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {"timestamp": 0, "questions": []}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"timestamp": 0, "questions": []}


def _save_cache(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _cache_is_fresh(cache: dict) -> bool:
    return (time.time() - cache.get("timestamp", 0)) < CACHE_TTL


def fetch_trivia(amount: int = 20, category: Optional[str] = None) -> list:
    cache = _load_cache()
    if _cache_is_fresh(cache) and cache["questions"]:
        return cache["questions"]

    params = {"amount": amount, "type": "multiple", "encode": "url3986"}
    if category and category.lower() in CATEGORY_MAP:
        params["category"] = CATEGORY_MAP[category.lower()]

    try:
        resp = requests.get(OPENTDB_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("response_code") == 0:
            questions = data["results"]
            _save_cache({"timestamp": time.time(), "questions": questions})
            return questions
    except requests.RequestException:
        pass

    return cache.get("questions", [])


def get_random_question(category: Optional[str] = None) -> Optional[dict]:
    questions = fetch_trivia(category=category)
    if not questions:
        return None
    q = random.choice(questions)
    from urllib.parse import unquote
    return {
        "question": unquote(q["question"]),
        "correct": unquote(q["correct_answer"]),
        "choices": [unquote(a) for a in q["incorrect_answers"]] + [unquote(q["correct_answer"])],
        "difficulty": q.get("difficulty", "unknown"),
        "category": unquote(q.get("category", "General")),
    }


def format_question(q: dict) -> str:
    if not q:
        return "Could not load a trivia question right now."
    random.shuffle(q["choices"])
    choices_str = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(q["choices"]))
    return (
        f"[Trivia - {q['category']} / {q['difficulty']}]\n"
        f"{q['question']}\n{choices_str}\n"
        f"(Answer: {q['correct']})"
    )
