"""Tests for tools/crypto_handler.py"""

import pytest
from unittest.mock import patch, MagicMock
import tools.crypto_handler as ch


@pytest.fixture(autouse=True)
def clear_cache():
    ch._cache.clear()
    yield
    ch._cache.clear()


def _mock_price_response(coin_id="bitcoin", currency="usd"):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        coin_id: {
            currency: 65000.0,
            f"{currency}_24h_change": 2.5,
            f"{currency}_market_cap": 1_200_000_000_000,
        }
    }
    return mock


def test_resolve_coin_alias():
    assert ch._resolve_coin("btc") == "bitcoin"
    assert ch._resolve_coin("ETH") == "ethereum"
    assert ch._resolve_coin("unknown") == "unknown"


def test_get_price_success():
    with patch("tools.crypto_handler.requests.get", return_value=_mock_price_response()):
        result = ch.get_price("bitcoin")
    assert result is not None
    assert result["coin"] == "bitcoin"
    assert result["price"] == 65000.0
    assert result["change_24h"] == 2.5
    assert result["currency"] == "USD"


def test_get_price_uses_cache():
    with patch("tools.crypto_handler.requests.get", return_value=_mock_price_response()) as mock_get:
        ch.get_price("bitcoin")
        ch.get_price("bitcoin")
    assert mock_get.call_count == 1


def test_get_price_alias_resolved():
    with patch("tools.crypto_handler.requests.get", return_value=_mock_price_response()) as mock_get:
        result = ch.get_price("btc")
    assert result["coin"] == "bitcoin"


def test_get_price_unknown_coin_returns_none():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {}
    with patch("tools.crypto_handler.requests.get", return_value=mock):
        result = ch.get_price("notacoin")
    assert result is None


def test_get_price_request_error_returns_none():
    import requests
    with patch("tools.crypto_handler.requests.get", side_effect=requests.RequestException):
        result = ch.get_price("bitcoin")
    assert result is None


def test_get_top_coins_success():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = [
        {"market_cap_rank": 1, "id": "bitcoin", "symbol": "btc",
         "current_price": 65000, "price_change_percentage_24h": 1.2},
        {"market_cap_rank": 2, "id": "ethereum", "symbol": "eth",
         "current_price": 3200, "price_change_percentage_24h": -0.5},
    ]
    with patch("tools.crypto_handler.requests.get", return_value=mock):
        result = ch.get_top_coins(limit=2)
    assert len(result) == 2
    assert result[0]["coin"] == "bitcoin"
    assert result[1]["symbol"] == "ETH"


def test_get_top_coins_request_error_returns_empty():
    import requests
    with patch("tools.crypto_handler.requests.get", side_effect=requests.RequestException):
        result = ch.get_top_coins()
    assert result == []


def test_format_price_normal():
    data = {"coin": "bitcoin", "currency": "USD", "price": 65000.0, "change_24h": 2.5}
    out = ch.format_price(data)
    assert "Bitcoin" in out
    assert "65,000.00" in out
    assert "+2.50%" in out


def test_format_price_none():
    assert ch.format_price(None) == "Could not retrieve price data."
