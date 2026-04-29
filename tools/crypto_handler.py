"""Cryptocurrency price and info handler for J.A.R.V.I.S."""

import os
import time
import requests
from typing import Optional

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_cache: dict = {}
CACHE_TTL = 120  # seconds

COIN_ALIASES = {
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "ethereum": "ethereum",
    "eth": "ethereum",
    "solana": "solana",
    "sol": "solana",
    "dogecoin": "dogecoin",
    "doge": "dogecoin",
    "cardano": "cardano",
    "ada": "cardano",
}


def _resolve_coin(name: str) -> str:
    return COIN_ALIASES.get(name.lower(), name.lower())


def get_price(coin: str, vs_currency: str = "usd") -> Optional[dict]:
    """Fetch current price and 24h change for a coin."""
    coin_id = _resolve_coin(coin)
    cache_key = f"{coin_id}_{vs_currency}"
    now = time.time()

    if cache_key in _cache and now - _cache[cache_key]["ts"] < CACHE_TTL:
        return _cache[cache_key]["data"]

    try:
        resp = requests.get(
            f"{COINGECKO_BASE}/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": vs_currency,
                "include_24hr_change": "true",
                "include_market_cap": "true",
            },
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json().get(coin_id)
        if not data:
            return None
        result = {
            "coin": coin_id,
            "currency": vs_currency.upper(),
            "price": data.get(vs_currency),
            "change_24h": data.get(f"{vs_currency}_24h_change"),
            "market_cap": data.get(f"{vs_currency}_market_cap"),
        }
        _cache[cache_key] = {"ts": now, "data": result}
        return result
    except requests.RequestException:
        return None


def get_top_coins(limit: int = 5, vs_currency: str = "usd") -> list:
    """Return top N coins by market cap."""
    try:
        resp = requests.get(
            f"{COINGECKO_BASE}/coins/markets",
            params={
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false",
            },
            timeout=8,
        )
        resp.raise_for_status()
        coins = resp.json()
        return [
            {
                "rank": c["market_cap_rank"],
                "coin": c["id"],
                "symbol": c["symbol"].upper(),
                "price": c["current_price"],
                "change_24h": c["price_change_percentage_24h"],
                "currency": vs_currency.upper(),
            }
            for c in coins
        ]
    except requests.RequestException:
        return []


def format_price(data: dict) -> str:
    """Format a price result into a human-readable string."""
    if not data:
        return "Could not retrieve price data."
    change = data.get("change_24h")
    change_str = f"{change:+.2f}%" if change is not None else "N/A"
    return (
        f"{data['coin'].capitalize()}: {data['currency']} {data['price']:,.2f} "
        f"(24h: {change_str})"
    )
