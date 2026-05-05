"""Tests for tools/unit_handler.py"""

import pytest
from tools.unit_handler import convert_units, format_conversion, _find_category


# --- _find_category ---

def test_find_category_length():
    assert _find_category("meter") == "length"
    assert _find_category("km") == "length"
    assert _find_category("inch") == "length"


def test_find_category_weight():
    assert _find_category("kg") == "weight"
    assert _find_category("pound") == "weight"


def test_find_category_unknown():
    assert _find_category("parsec") is None


# --- convert_units: length ---

def test_convert_km_to_miles():
    result = convert_units(1.0, "km", "mile")
    assert result["success"] is True
    assert abs(result["result"] - 0.621371) < 1e-4


def test_convert_meter_to_cm():
    result = convert_units(1.0, "meter", "cm")
    assert result["success"] is True
    assert result["result"] == pytest.approx(100.0)


def test_convert_inch_to_foot():
    result = convert_units(12.0, "in", "ft")
    assert result["success"] is True
    assert result["result"] == pytest.approx(1.0, rel=1e-4)


# --- convert_units: weight ---

def test_convert_kg_to_lbs():
    result = convert_units(1.0, "kg", "lbs")
    assert result["success"] is True
    assert abs(result["result"] - 2.20462) < 1e-3


def test_convert_gram_to_milligram():
    result = convert_units(1.0, "g", "mg")
    assert result["success"] is True
    assert result["result"] == pytest.approx(1000.0)


# --- convert_units: volume ---

def test_convert_liter_to_ml():
    result = convert_units(1.0, "liter", "ml")
    assert result["success"] is True
    assert result["result"] == pytest.approx(1000.0)


def test_convert_gallon_to_liter():
    result = convert_units(1.0, "gallon", "liter")
    assert result["success"] is True
    assert abs(result["result"] - 3.78541) < 1e-3


# --- convert_units: temperature ---

def test_celsius_to_fahrenheit():
    result = convert_units(0.0, "celsius", "fahrenheit")
    assert result["success"] is True
    assert result["result"] == pytest.approx(32.0)


def test_fahrenheit_to_celsius():
    result = convert_units(212.0, "f", "c")
    assert result["success"] is True
    assert result["result"] == pytest.approx(100.0)


def test_celsius_to_kelvin():
    result = convert_units(0.0, "c", "kelvin")
    assert result["success"] is True
    assert result["result"] == pytest.approx(273.15)


# --- convert_units: errors ---

def test_unknown_from_unit():
    result = convert_units(1.0, "furlong", "meter")
    assert result["success"] is False
    assert "furlong" in result["error"]


def test_unknown_to_unit():
    result = convert_units(1.0, "meter", "lightyear")
    assert result["success"] is False


def test_incompatible_categories():
    result = convert_units(1.0, "kg", "meter")
    assert result["success"] is False
    assert "Cannot convert" in result["error"]


# --- format_conversion ---

def test_format_conversion_success():
    data = convert_units(1.0, "km", "meter")
    text = format_conversion(data)
    assert "1.0" in text
    assert "km" in text
    assert "1000" in text


def test_format_conversion_error():
    data = {"success": False, "error": "Unknown unit: 'xyz'"}
    text = format_conversion(data)
    assert "Conversion error" in text
    assert "xyz" in text
