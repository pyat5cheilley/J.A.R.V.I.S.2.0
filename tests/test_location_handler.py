import pytest
from unittest.mock import patch, MagicMock
from tools.location_handler import (
    get_location_by_ip,
    geocode_address,
    reverse_geocode,
    format_location,
)

MOCK_IP_RESPONSE = {
    "city": "London",
    "region": "England",
    "country_name": "United Kingdom",
    "country_code": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
}

MOCK_GEOCODE_RESPONSE = {
    "results": [
        {
            "formatted": "Paris, France",
            "components": {"city": "Paris", "country": "France", "country_code": "fr"},
            "geometry": {"lat": 48.8566, "lng": 2.3522},
        }
    ]
}


def test_get_location_by_ip_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = MOCK_IP_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    with patch("tools.location_handler.requests.get", return_value=mock_resp):
        result = get_location_by_ip()
    assert result["city"] == "London"
    assert result["country_code"] == "GB"
    assert result["source"] == "ip"


def test_get_location_by_ip_failure():
    with patch("tools.location_handler.requests.get", side_effect=Exception("timeout")):
        result = get_location_by_ip()
    assert "error" in result
    assert result["source"] == "ip"


def test_geocode_address_no_api_key():
    with patch("tools.location_handler.GEOCODE_API_KEY", ""):
        result = geocode_address("Paris, France")
    assert result is None


def test_geocode_address_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = MOCK_GEOCODE_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    with patch("tools.location_handler.GEOCODE_API_KEY", "fake_key"), \
         patch("tools.location_handler.requests.get", return_value=mock_resp):
        result = geocode_address("Paris, France")
    assert result is not None
    assert result["city"] == "Paris"
    assert result["country_code"] == "FR"


def test_geocode_address_empty_results():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"results": []}
    mock_resp.raise_for_status = MagicMock()
    with patch("tools.location_handler.GEOCODE_API_KEY", "fake_key"), \
         patch("tools.location_handler.requests.get", return_value=mock_resp):
        result = geocode_address("Nowhere")
    assert result is None


def test_format_location_full():
    loc = {"city": "Berlin", "region": "Brandenburg", "country": "Germany"}
    assert format_location(loc) == "Berlin, Brandenburg, Germany"


def test_format_location_error():
    result = format_location({"error": "network failure", "source": "ip"})
    assert "unavailable" in result


def test_reverse_geocode_delegates():
    with patch("tools.location_handler.GEOCODE_API_KEY", ""):
        result = reverse_geocode(51.5, -0.1)
    assert result is None
