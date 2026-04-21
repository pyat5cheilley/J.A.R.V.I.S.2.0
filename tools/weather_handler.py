"""Weather handler for J.A.R.V.I.S.2.0

Fetches current weather and forecasts using the OpenWeatherMap API.
Requires OPENWEATHER_API_KEY in the .env file.
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_UNITS = "metric"  # 'metric' for Celsius, 'imperial' for Fahrenheit


def get_current_weather(city: str, units: str = DEFAULT_UNITS) -> dict:
    """Fetch current weather for a given city.

    Args:
        city: Name of the city (e.g. 'London', 'New York').
        units: Unit system — 'metric', 'imperial', or 'standard'.

    Returns:
        A dict with weather details, or an error dict on failure.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set in environment."}

    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": units,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        unit_symbol = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": f"{data['main']['temp']}{unit_symbol}",
            "feels_like": f"{data['main']['feels_like']}{unit_symbol}",
            "humidity": f"{data['main']['humidity']}%",
            "description": data["weather"][0]["description"].capitalize(),
            "wind_speed": f"{data['wind']['speed']} m/s",
            "visibility": f"{data.get('visibility', 'N/A')} m",
            "timestamp": datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M UTC"),
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"City '{city}' not found."}
        return {"error": f"HTTP error: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}


def get_forecast(city: str, days: int = 3, units: str = DEFAULT_UNITS) -> list[dict]:
    """Fetch a multi-day weather forecast for a given city.

    Args:
        city: Name of the city.
        days: Number of forecast days (1–5).
        units: Unit system — 'metric', 'imperial', or 'standard'.

    Returns:
        A list of daily forecast dicts, or a list with a single error dict.
    """
    if not OPENWEATHER_API_KEY:
        return [{"error": "OPENWEATHER_API_KEY not set in environment."}]

    days = max(1, min(days, 5))  # API supports up to 5 days
    unit_symbol = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")

    try:
        response = requests.get(
            f"{BASE_URL}/forecast",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": units,
                "cnt": days * 8,  # API returns data in 3-hour intervals (8 per day)
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Aggregate by date — pick the midday entry closest to 12:00 for each day
        daily: dict[str, dict] = {}
        for entry in data["list"]:
            date_str = datetime.utcfromtimestamp(entry["dt"]).strftime("%Y-%m-%d")
            hour = datetime.utcfromtimestamp(entry["dt"]).hour
            if date_str not in daily or abs(hour - 12) < abs(
                datetime.strptime(daily[date_str]["timestamp"], "%Y-%m-%d %H:%M UTC").hour - 12
            ):
                daily[date_str] = {
                    "date": date_str,
                    "temperature": f"{entry['main']['temp']}{unit_symbol}",
                    "feels_like": f"{entry['main']['feels_like']}{unit_symbol}",
                    "humidity": f"{entry['main']['humidity']}%",
                    "description": entry["weather"][0]["description"].capitalize(),
                    "wind_speed": f"{entry['wind']['speed']} m/s",
                    "timestamp": datetime.utcfromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M UTC"),
                }

        return list(daily.values())[:days]

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return [{"error": f"City '{city}' not found."}]
        return [{"error": f"HTTP error: {e}"}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Network error: {e}"}]


def format_weather(weather: dict) -> str:
    """Format a weather dict into a human-readable string."""
    if "error" in weather:
        return f"Weather error: {weather['error']}"
    return (
        f"Weather in {weather['city']}, {weather['country']} ({weather['timestamp']}):\n"
        f"  {weather['description']}, {weather['temperature']} (feels like {weather['feels_like']})\n"
        f"  Humidity: {weather['humidity']} | Wind: {weather['wind_speed']} | Visibility: {weather['visibility']}"
    )


def format_forecast(forecast: list[dict]) -> str:
    """Format a forecast list into a human-readable string."""
    if not forecast:
        return "No forecast data available."
    if "error" in forecast[0]:
        return f"Forecast error: {forecast[0]['error']}"
    lines = ["Forecast:"]
    for day in forecast:
        lines.append(
            f"  {day['date']}: {day['description']}, {day['temperature']} "
            f"(feels like {day['feels_like']}), Humidity: {day['humidity']}, Wind: {day['wind_speed']}"
        )
    return "\n".join(lines)
