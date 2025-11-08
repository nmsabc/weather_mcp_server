#!/usr/bin/env python3
"""
MCP Server for Weather Service

This implements the Model Context Protocol for the weather service,
allowing LLMs to get weather data through the MCP inspector.
"""

import asyncio
import logging
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
)
from pydantic import AnyUrl

# Import our weather service
from src.weather_service import WeatherService
from src.config import settings
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-server")


async def geocode_location(location: str) -> tuple[float, float]:
    """Convert a location name to latitude/longitude coordinates using OpenWeatherMap Geocoding API.

    Args:
        location: Location name (e.g., "Baden bei Wien, Austria")

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If location cannot be geocoded
    """
    try:
        # Use OpenWeatherMap Geocoding API
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location,
            "limit": 1,
            "appid": settings.openweather_api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if not data:
                raise ValueError(f"Location '{location}' not found")

            result = data[0]
            return float(result["lat"]), float(result["lon"])

    except Exception as e:
        logger.error(f"Geocoding error for '{location}': {e}")
        raise ValueError(f"Could not geocode location '{location}': {str(e)}")

# Initialize weather service
weather_service = WeatherService()

# Create MCP server instance
server = Server("weather-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather data for a specific location. You can use either coordinates (latitude/longitude) OR a location name/address. If you have a place name like 'Baden bei Wien' or 'New York', use the location parameter instead of coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate (-90 to 90). Optional if location is provided.",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate (-180 to 180). Optional if location is provided.",
                        "minimum": -180,
                        "maximum": 180
                    },
                    "location": {
                        "type": "string",
                        "description": "Location name, city, or address (e.g., 'Baden bei Wien, Austria', 'New York, NY', 'London, UK'). Use this if you don't have exact coordinates."
                    },
                    "units": {
                        "type": "string",
                        "description": "Unit system for temperature and other measurements",
                        "enum": ["metric", "imperial", "standard"],
                        "default": "metric"
                    },
                    "lang": {
                        "type": "string",
                        "description": "Language code for weather descriptions",
                        "default": "en"
                    }
                },
                "required": []
            }
        )
    ]


@server.list_resources()
async def list_resources() -> list:
    """List available resources (none for weather server)."""
    return []


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""
    if name != "get_current_weather":
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Extract parameters
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")
        location = arguments.get("location")
        units = arguments.get("units", "metric")
        lang = arguments.get("lang", "en")

        # Get coordinates from location name if not provided
        if latitude is None or longitude is None:
            if not location:
                raise ValueError(
                    "Either latitude/longitude coordinates OR location name must be provided")

            # Use OpenWeatherMap geocoding API to get coordinates
            latitude, longitude = await geocode_location(location)
            if latitude is None or longitude is None:
                raise ValueError(
                    f"Could not find coordinates for location: {location}")

        # Validate parameter ranges
        if not (-90 <= latitude <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("longitude must be between -180 and 180")

        logger.info(
            f"Getting weather for coordinates: {latitude}, {longitude}")

        # Get weather data
        raw_data = weather_service.get_current_weather(
            latitude=latitude,
            longitude=longitude,
            units=units,
            lang=lang
        )

        # Format the response
        formatted_data = weather_service.format_weather_response(raw_data)

        # Create a natural language response
        location = formatted_data.get("location", {})
        current = formatted_data.get("current", {})
        weather = current.get("weather", {})

        # Get coordinates with defaults
        lat = location.get('latitude', latitude)
        lon = location.get('longitude', longitude)

        response_text = f"""Current weather for coordinates ({lat}, {lon}):

🌡️  Temperature: {current.get('temperature', 'N/A')}°
🌡️  Feels like: {current.get('feels_like', 'N/A')}°
🌤️  Conditions: {weather.get('description', 'N/A').title()}
💧 Humidity: {current.get('humidity', 'N/A')}%
🌪️  Wind speed: {current.get('wind_speed', 'N/A')} m/s
🌪️  Wind direction: {current.get('wind_deg', 'N/A')}°
📊 Pressure: {current.get('pressure', 'N/A')} hPa
👁️  Visibility: {current.get('visibility', 'N/A')} meters
☁️  Cloud cover: {current.get('clouds', 'N/A')}%
🌅 Sunrise: {current.get('sunrise', 'N/A')}
🌇 Sunset: {current.get('sunset', 'N/A')}"""

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        error_msg = f"Error fetching weather data: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server."""
    logger.info("Starting Weather MCP Server...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
