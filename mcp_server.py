"""
MCP Server module using FastAPI.
Exposes HTTP endpoints for weather data retrieval.
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any
import uvicorn

from weather_api import OpenWeatherMapAPI, WeatherAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Weather MCP Server",
    description="Weather data microservice with MCP wrapper for OpenWeatherMap API",
    version="1.0.0"
)


# Initialize weather API client
try:
    weather_client = OpenWeatherMapAPI()
except WeatherAPIError as e:
    logger.warning(f"Weather API client initialization: {e}")
    weather_client = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Weather MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "/weather": "Get current weather data for latitude and longitude"
        }
    }


@app.get("/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    lon: float = Query(..., description="Longitude coordinate", ge=-180, le=180)
) -> Dict[str, Any]:
    """
    Get current weather data for specified coordinates.
    
    Args:
        lat: Latitude coordinate (-90 to 90)
        lon: Longitude coordinate (-180 to 180)
        
    Returns:
        Dictionary containing current weather data
        
    Raises:
        HTTPException: If weather data cannot be retrieved
    """
    if weather_client is None:
        raise HTTPException(
            status_code=500,
            detail="Weather API client not initialized. Check API key configuration."
        )
    
    try:
        raw_weather = weather_client.get_current_weather(lat, lon)
        formatted_weather = weather_client.format_weather_data(raw_weather)
        return {
            "status": "success",
            "data": formatted_weather
        }
    except WeatherAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def run_server(host: str = None, port: int = None):
    """
    Run the MCP server.
    
    Args:
        host: Host address (defaults to MCP_SERVER_HOST env var or "0.0.0.0")
        port: Port number (defaults to MCP_SERVER_PORT env var or 8000)
    """
    host = host or os.environ.get("MCP_SERVER_HOST", "0.0.0.0")
    port = port or int(os.environ.get("MCP_SERVER_PORT", "8000"))
    
    logger.info(f"Starting Weather MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
