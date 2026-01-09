"""
Phase 6: Tool Definitions (same as Phase 5)
Local tools that can be combined with MCP tools.
"""

import os
from typing import Annotated
import httpx
from pydantic import Field


def get_weather(
    city: Annotated[str, Field(description="The name of the city (e.g., 'London', 'Tokyo')")]
) -> str:
    """
    Get the current weather for a city.

    Returns current weather conditions including temperature, condition, and humidity.
    Use this tool when the user asks about weather in a specific location.
    """
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return "Error: WEATHER_API_KEY not set in .env"

    try:
        response = httpx.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": api_key, "q": city},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]

        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C ({temp_f}°F)
☁️ Condition: {condition}
💧 Humidity: {humidity}%
💨 Wind: {wind_kph} km/h"""

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Could not find weather for '{city}'. Please check the city name."
        return f"Weather API error: {e.response.status_code}"
    except httpx.TimeoutException:
        return "Weather API timed out. Please try again."
    except Exception as e:
        return f"Error fetching weather: {e}"


# List of local tools
TOOLS = [get_weather]
