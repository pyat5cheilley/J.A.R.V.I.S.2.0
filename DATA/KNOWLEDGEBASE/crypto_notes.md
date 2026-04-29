# Cryptocurrency Handler — Notes

## Overview
The `tools/crypto_handler.py` module provides real-time and cached cryptocurrency
price data via the free CoinGecko public API (no API key required).

## Key Functions

| Function | Description |
|---|---|
| `get_price(coin, vs_currency)` | Fetch current price + 24h change for a coin |
| `get_top_coins(limit, vs_currency)` | Return top N coins by market cap |
| `format_price(data)` | Format price dict into readable string |

## Caching
- Results are cached in-memory for **120 seconds** to avoid rate limits.
- Cache key: `<coin_id>_<currency>` (e.g. `bitcoin_usd`).

## Coin Aliases
Common tickers (BTC, ETH, SOL, DOGE, ADA) are resolved to CoinGecko IDs
automatically, so users can say "btc" or "bitcoin" interchangeably.

## Integration with JARVIS
Call `get_price("bitcoin")` and pass the result to `format_price()` to produce
a natural-language response. Use `get_top_coins()` for a market overview digest.

## Rate Limits
CoinGecko free tier: ~10–30 req/min. The 120 s cache keeps usage well within limits.

## Example
```python
from tools.crypto_handler import get_price, format_price
data = get_price("eth")
print(format_price(data))
# Ethereum: USD 3,200.00 (24h: -0.50%)
```
