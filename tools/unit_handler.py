"""Unit conversion handler for J.A.R.V.I.S. 2.0"""

from typing import Optional

# Conversion factors to a common base unit
_CONVERSIONS = {
    # Length (base: meter)
    "length": {
        "meter": 1.0, "m": 1.0,
        "kilometer": 1000.0, "km": 1000.0,
        "centimeter": 0.01, "cm": 0.01,
        "millimeter": 0.001, "mm": 0.001,
        "mile": 1609.344, "mi": 1609.344,
        "yard": 0.9144, "yd": 0.9144,
        "foot": 0.3048, "ft": 0.3048,
        "inch": 0.0254, "in": 0.0254,
    },
    # Weight (base: kilogram)
    "weight": {
        "kilogram": 1.0, "kg": 1.0,
        "gram": 0.001, "g": 0.001,
        "milligram": 1e-6, "mg": 1e-6,
        "pound": 0.453592, "lb": 0.453592, "lbs": 0.453592,
        "ounce": 0.0283495, "oz": 0.0283495,
        "ton": 1000.0, "tonne": 1000.0,
    },
    # Volume (base: liter)
    "volume": {
        "liter": 1.0, "l": 1.0, "litre": 1.0,
        "milliliter": 0.001, "ml": 0.001,
        "gallon": 3.78541, "gal": 3.78541,
        "quart": 0.946353, "qt": 0.946353,
        "pint": 0.473176, "pt": 0.473176,
        "cup": 0.236588,
        "fluid_ounce": 0.0295735, "fl_oz": 0.0295735,
    },
    # Temperature handled separately
    "temperature": {
        "celsius": "c", "c": "c",
        "fahrenheit": "f", "f": "f",
        "kelvin": "k", "k": "k",
    },
}


def _find_category(unit: str) -> Optional[str]:
    unit = unit.lower().strip()
    for category, units in _CONVERSIONS.items():
        if unit in units:
            return category
    return None


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()
    temps = _CONVERSIONS["temperature"]
    f = temps.get(from_unit)
    t = temps.get(to_unit)
    if f is None or t is None:
        raise ValueError(f"Unknown temperature unit: {from_unit!r} or {to_unit!r}")
    # Convert to Celsius first
    if f == "c":
        celsius = value
    elif f == "f":
        celsius = (value - 32) * 5 / 9
    else:  # kelvin
        celsius = value - 273.15
    # Convert Celsius to target
    if t == "c":
        return celsius
    elif t == "f":
        return celsius * 9 / 5 + 32
    else:  # kelvin
        return celsius + 273.15


def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert a value from one unit to another. Returns a result dict."""
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    from_cat = _find_category(from_unit)
    to_cat = _find_category(to_unit)

    if from_cat is None:
        return {"success": False, "error": f"Unknown unit: '{from_unit}'"}
    if to_cat is None:
        return {"success": False, "error": f"Unknown unit: '{to_unit}'"}
    if from_cat != to_cat:
        return {"success": False, "error": f"Cannot convert {from_cat} to {to_cat}"}

    if from_cat == "temperature":
        result = _convert_temperature(value, from_unit, to_unit)
    else:
        base = value * _CONVERSIONS[from_cat][from_unit]
        result = base / _CONVERSIONS[from_cat][to_unit]

    return {
        "success": True,
        "value": value,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "result": round(result, 6),
        "category": from_cat,
    }


def format_conversion(data: dict) -> str:
    """Format a conversion result dict into a human-readable string."""
    if not data.get("success"):
        return f"Conversion error: {data.get('error', 'unknown error')}"
    return (
        f"{data['value']} {data['from_unit']} = "
        f"{data['result']} {data['to_unit']} "
        f"({data['category']})"
    )
