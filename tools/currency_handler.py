"""Currency exchange rate handler for J.A.R.V.I.S."""

import os
import time
import json
import requests
from pathlib import Path

CACHE_FILE = Path("DATA/currency_cache.json")
CACHE_TTL = 3600  # 1 hour
ALIASES = {
    "buck": "USD",
    "dollar": "USD",
    "euro": "EUR",
    "pound": "GBP",
    "yen": "JPY",
    "rupee": "INR",
    "yuan": "CNY",
    "franc": "CHF",
    "loonie": "CAD",
}


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(data: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def _cache_is_fresh(cache: dict) -> bool:
    ts = cache.get("timestamp", 0)
    return (time.time() - ts) < CACHE_TTL


def _resolve_currency(code: str) -> str:
    cleaned = code.strip().lower()
    return ALIASES.get(cleaned, cleaned.upper())


def get_exchange_rates(base: str = "USD") -> dict:
    """Fetch exchange rates for a base currency, using cache when fresh."""
    base = _resolve_currency(base)
    cache = _load_cache()
    if cache.get("base") == base and _cache_is_fresh(cache):
        return cache.get("rates", {})

    api_key = os.getenv("EXCHANGE_RATE_API_KEY", "")
    url = (
        f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
        if api_key
        else f"https://open.er-api.com/v6/latest/{base}"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", data.get("conversion_rates", {}))
        _save_cache({"base": base, "rates": rates, "timestamp": time.time()})
        return rates
    except requests.RequestException:
        return cache.get("rates", {})


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount from one currency to another."""
    src = _resolve_currency(from_currency)
    dst = _resolve_currency(to_currency)
    rates = get_exchange_rates(src)
    if not rates:
        return {"error": "Could not fetch exchange rates."}
    if dst not in rates:
        return {"error": f"Currency '{dst}' not found."}
    result = round(amount * rates[dst], 4)
    return {"from": src, "to": dst, "amount": amount, "result": result, "rate": rates[dst]}


def format_conversion(data: dict) -> str:
    """Return a human-readable conversion string."""
    if "error" in data:
        return f"[Currency] Error: {data['error']}"
    return (
        f"{data['amount']} {data['from']} = {data['result']} {data['to']} "
        f"(rate: 1 {data['from']} = {data['rate']} {data['to']})"
    )
