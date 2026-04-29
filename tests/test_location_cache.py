import os
import time
import json
import pytest
from tools.location_cache import (
    get_cached_location,
    set_cached_location,
    clear_cache,
    purge_expired,
    CACHE_FILE,
)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)


def test_cache_miss_on_empty():
    assert get_cached_location("london") is None


def test_set_and_get_cache():
    data = {"city": "Tokyo", "country": "Japan"}
    set_cached_location("tokyo", data)
    result = get_cached_location("tokyo")
    assert result == data


def test_cache_miss_on_expired():
    data = {"city": "Oslo", "country": "Norway"}
    set_cached_location("oslo", data)
    # Manually expire the entry
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
    cache["oslo"]["timestamp"] = time.time() - 7200
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)
    assert get_cached_location("oslo") is None


def test_clear_cache():
    set_cached_location("rome", {"city": "Rome"})
    clear_cache()
    assert get_cached_location("rome") is None


def test_purge_expired_removes_only_stale():
    set_cached_location("fresh", {"city": "Fresh"})
    set_cached_location("stale", {"city": "Stale"})
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
    cache["stale"]["timestamp"] = time.time() - 7200
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)
    removed = purge_expired()
    assert removed == 1
    assert get_cached_location("fresh") is not None
    assert get_cached_location("stale") is None


def test_purge_expired_no_entries():
    removed = purge_expired()
    assert removed == 0
