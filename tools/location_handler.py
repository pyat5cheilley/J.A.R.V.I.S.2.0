import requests
import os
from typing import Optional

GEOCODE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")
IPAPI_URL = "https://ipapi.co/json/"
GEOCODE_URL = "https://api.opencagedata.com/geocode/v1/json"


def get_location_by_ip() -> dict:
    """Get approximate location based on public IP address."""
    try:
        response = requests.get(IPAPI_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country_name", "Unknown"),
            "country_code": data.get("country_code", "XX"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone", "UTC"),
            "source": "ip",
        }
    except Exception as e:
        return {"error": str(e), "source": "ip"}


def geocode_address(address: str) -> Optional[dict]:
    """Convert a human-readable address to coordinates using OpenCage."""
    if not GEOCODE_API_KEY:
        return None
    try:
        params = {"q": address, "key": GEOCODE_API_KEY, "limit": 1, "no_annotations": 1}
        response = requests.get(GEOCODE_URL, params=params, timeout=5)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None
        best = results[0]
        components = best.get("components", {})
        geometry = best.get("geometry", {})
        return {
            "formatted": best.get("formatted", address),
            "city": components.get("city") or components.get("town") or components.get("village", "Unknown"),
            "country": components.get("country", "Unknown"),
            "country_code": components.get("country_code", "XX").upper(),
            "latitude": geometry.get("lat"),
            "longitude": geometry.get("lng"),
            "source": "geocode",
        }
    except Exception as e:
        return {"error": str(e), "source": "geocode"}


def reverse_geocode(lat: float, lon: float) -> Optional[dict]:
    """Convert coordinates to a human-readable address using OpenCage."""
    if not GEOCODE_API_KEY:
        return None
    return geocode_address(f"{lat},{lon}")


def format_location(location: dict) -> str:
    """Format a location dict into a readable string."""
    if "error" in location:
        return f"Location unavailable: {location['error']}"
    parts = []
    if location.get("city") and location["city"] != "Unknown":
        parts.append(location["city"])
    if location.get("region") and location["region"] != "Unknown":
        parts.append(location["region"])
    if location.get("country") and location["country"] != "Unknown":
        parts.append(location["country"])
    return ", ".join(parts) if parts else "Unknown location"
