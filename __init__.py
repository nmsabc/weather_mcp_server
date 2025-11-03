"""
Weather MCP Server - A weather data microservice with MCP wrapper.

This package provides:
- OpenWeatherMap API integration
- FastAPI-based MCP server
- Python client for server interaction
"""

__version__ = "1.0.0"
__author__ = "Weather MCP Server Contributors"

from .weather_api import OpenWeatherMapAPI, WeatherAPIError
from .mcp_client import MCPClient, MCPClientError
from .mcp_server import app, run_server

__all__ = [
    "OpenWeatherMapAPI",
    "WeatherAPIError",
    "MCPClient",
    "MCPClientError",
    "app",
    "run_server",
]
