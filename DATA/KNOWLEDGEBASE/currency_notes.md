# Currency Handler — Notes

## Overview
The `currency_handler` module provides real-time currency conversion and
exchange-rate lookup for J.A.R.V.I.S. It caches results locally for 1 hour
to reduce API calls and support offline fallback.

## Data Source
- Primary: [ExchangeRate-API](https://www.exchangerate-api.com/) (requires `EXCHANGE_RATE_API_KEY` in `.env`)
- Fallback: [Open Exchange Rates (open.er-api.com)](https://open.er-api.com/) — no key needed, limited quota

## Cache
- Location: `DATA/currency_cache.json`
- TTL: 3600 seconds (1 hour)
- Stores: base currency, rates dict, UNIX timestamp

## Supported Aliases
| Alias   | Code |
|---------|------|
| dollar  | USD  |
| buck    | USD  |
| euro    | EUR  |
| pound   | GBP  |
| yen     | JPY  |
| rupee   | INR  |
| yuan    | CNY  |
| franc   | CHF  |
| loonie  | CAD  |

## Example Usage
```python
from tools.currency_handler import convert_currency, format_conversion

result = convert_currency(250, "USD", "EUR")
print(format_conversion(result))
# 250 USD = 230.0 EUR (rate: 1 USD = 0.92 EUR)
```

## Environment Variable
```
EXCHANGE_RATE_API_KEY=your_key_here
```
If not set, the free open.er-api.com endpoint is used automatically.
