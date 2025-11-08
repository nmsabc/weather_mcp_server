#!/usr/bin/env python3
"""
HTTP MCP Server for Weather Service

This creates an HTTP endpoint that speaks MCP protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
import argparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

# Import your existing weather service
from src.weather_service import WeatherService
from src.config import settings
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-http-server")

# Pydantic models for MCP protocol


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = {}
    id: int | str


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Dict[str, Any] | None = None
    error: Dict[str, Any] | None = None
    id: int | str


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


# Initialize weather service
weather_service = WeatherService()


async def geocode_location(location: str) -> tuple[float, float]:
    """Convert location name to coordinates using OpenWeatherMap Geocoding API."""
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

        location_data = data[0]
        return float(location_data["lat"]), float(location_data["lon"])

# Create FastAPI app
app = FastAPI(
    title="Weather MCP HTTP Server",
    description="MCP-compatible HTTP server for weather data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Weather MCP HTTP Server",
        "status": "running",
        "protocol": "MCP over HTTP",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/",
            "docs": "/docs"
        }
    }


@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    """Main MCP protocol endpoint."""
    try:
        if request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [
                        {
                            "name": "get_current_weather",
                            "description": "Get current weather data for a specific location. You can use either coordinates (latitude/longitude) OR a location name/address. If you have a place name like 'Baden bei Wien' or 'New York', use the location parameter instead of coordinates.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "latitude": {
                                        "type": "number",
                                        "description": "Latitude coordinate (use this OR location, not both)"
                                    },
                                    "longitude": {
                                        "type": "number",
                                        "description": "Longitude coordinate (use this OR location, not both)"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Location name or address (use this OR coordinates, not both)"
                                    },
                                    "units": {
                                        "type": "string",
                                        "enum": ["metric", "imperial", "kelvin"],
                                        "default": "metric",
                                        "description": "Temperature units"
                                    },
                                    "lang": {
                                        "type": "string",
                                        "default": "en",
                                        "description": "Language for weather description"
                                    }
                                }
                            }
                        }
                    ]
                }
            )

        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if tool_name == "get_current_weather":
                # Handle location vs coordinates
                if "location" in arguments and arguments["location"]:
                    # Geocode the location
                    lat, lon = await geocode_location(arguments["location"])
                elif "latitude" in arguments and "longitude" in arguments:
                    lat = float(arguments["latitude"])
                    lon = float(arguments["longitude"])
                else:
                    raise ValueError(
                        "Either 'location' or both 'latitude' and 'longitude' must be provided")

                # Get weather data - FIXED: No await since get_current_weather is sync
                units = arguments.get("units", "metric")
                lang = arguments.get("lang", "en")

                # Call the synchronous method without await
                weather_data = weather_service.get_current_weather(
                    latitude=lat,
                    longitude=lon,
                    units=units,
                    lang=lang
                )

                # Debug: Log the weather data structure
                logger.info(
                    f"Weather data received: {json.dumps(weather_data, indent=2)}")

                # FIXED: Handle the correct data structure (One Call API format)
                location_name = arguments.get("location", f"{lat}, {lon}")

                # Extract current weather data from the nested structure
                current_data = weather_data.get('current', {})

                # Get location info (this API doesn't return city name, so we'll use geocoding result)
                timezone = weather_data.get('timezone', '').split(
                    '/')[-1].replace('_', ' ')
                city_name = timezone or f"Lat: {lat}, Lon: {lon}"

                # Extract weather information from current data
                temp = current_data.get('temp', 'N/A')
                feels_like = current_data.get('feels_like', 'N/A')
                humidity = current_data.get('humidity', 'N/A')
                pressure = current_data.get('pressure', 'N/A')
                visibility = current_data.get('visibility', 'N/A')
                wind_speed = current_data.get('wind_speed', 'N/A')
                wind_deg = current_data.get('wind_deg')

                # Extract weather description
                weather_list = current_data.get('weather', [{}])
                weather_info = weather_list[0] if weather_list else {}
                description = weather_info.get(
                    'description', 'No description available')

                # Format response with correct data structure
                temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
                speed_unit = 'm/s' if units == 'metric' else 'mph'

                wind_info = f"{wind_speed} {speed_unit}"
                if wind_deg is not None:
                    wind_info += f", {wind_deg}°"

                # Convert visibility from meters to appropriate unit
                if visibility != 'N/A':
                    if units == 'metric':
                        vis_display = f"{visibility} m"
                    else:
                        vis_display = f"{round(visibility * 0.000621371, 1)} mi"
                else:
                    vis_display = "N/A"

                formatted_response = f"""🌤️ Weather for {location_name}:

📍 **Location**: {city_name}
🌡️ **Temperature**: {temp}{temp_unit} (feels like {feels_like}{temp_unit})
☁️ **Condition**: {description.title()}
💧 **Humidity**: {humidity}%
💨 **Wind**: {wind_info}
👁️ **Visibility**: {vis_display}
🔄 **Pressure**: {pressure} hPa

*Data from OpenWeatherMap*"""

                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": formatted_response
                            }
                        ]
                    }
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        elif request.method == "resources/list":
            return MCPResponse(
                id=request.id,
                result={"resources": []}
            )

        elif request.method == "prompts/list":
            return MCPResponse(
                id=request.id,
                result={"prompts": []}
            )

        else:
            raise ValueError(f"Unknown method: {request.method}")

    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )


@app.post("/tools/call")
async def direct_tool_call(tool_call: ToolCall):
    """Direct tool call endpoint (alternative to MCP protocol)."""
    try:
        if tool_call.name == "get_current_weather":
            # Handle location vs coordinates
            if "location" in tool_call.arguments and tool_call.arguments["location"]:
                lat, lon = await geocode_location(tool_call.arguments["location"])
            elif "latitude" in tool_call.arguments and "longitude" in tool_call.arguments:
                lat = float(tool_call.arguments["latitude"])
                lon = float(tool_call.arguments["longitude"])
            else:
                raise ValueError(
                    "Either 'location' or both 'latitude' and 'longitude' must be provided")

            # Get weather data - FIXED: No await since get_current_weather is sync
            units = tool_call.arguments.get("units", "metric")
            lang = tool_call.arguments.get("lang", "en")

            weather_data = weather_service.get_current_weather(
                latitude=lat,
                longitude=lon,
                units=units,
                lang=lang
            )

            return {"success": True, "data": weather_data}

        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown tool: {tool_call.name}")

    except Exception as e:
        logger.error(f"Error in direct tool call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """Run the HTTP MCP server."""
    parser = argparse.ArgumentParser(description="Weather MCP HTTP Server")
    parser.add_argument("--host", default="localhost", help="HTTP host")
    parser.add_argument("--port", type=int, default=8001, help="HTTP port")

    args = parser.parse_args()

    logger.info(
        f"Starting Weather MCP HTTP Server on http://{args.host}:{args.port}")
    logger.info("MCP endpoint: /mcp")
    logger.info("Direct tool endpoint: /tools/call")
    logger.info("Documentation: /docs")

    config = uvicorn.Config(
        app=app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()

if __name__ == "__main__":
    asyncio.run(main())
