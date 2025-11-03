"""
MCP (Model Context Protocol) wrapper for the weather service.
This allows LLMs to interact with the weather service.
"""

import logging
from typing import Dict, Any, List
from src.weather_service import WeatherService

logger = logging.getLogger(__name__)


class MCPWeatherWrapper:
    """MCP wrapper for weather service to enable LLM integration."""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register available tools for MCP."""
        return [
            {
                "name": "get_current_weather",
                "description": "Get current weather data for a specific location using latitude and longitude coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude coordinate (-90 to 90)",
                            "minimum": -90,
                            "maximum": 90
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude coordinate (-180 to 180)",
                            "minimum": -180,
                            "maximum": 180
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
                    "required": ["latitude", "longitude"]
                }
            }
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return self.tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        if tool_name == "get_current_weather":
            return self._get_current_weather(**parameters)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    def _get_current_weather(
        self,
        latitude: float,
        longitude: float,
        units: str = "metric",
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Execute get_current_weather tool.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Unit system
            lang: Language code
            
        Returns:
            Weather data result
        """
        try:
            logger.info(f"MCP: Fetching weather for ({latitude}, {longitude})")
            
            raw_data = self.weather_service.get_current_weather(
                latitude=latitude,
                longitude=longitude,
                units=units,
                lang=lang
            )
            
            formatted_data = self.weather_service.format_weather_response(raw_data)
            
            return {
                "success": True,
                "data": formatted_data
            }
            
        except Exception as e:
            logger.error(f"MCP: Error fetching weather: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_llm_response(self, weather_data: Dict[str, Any]) -> str:
        """
        Create a natural language response from weather data for LLM.
        
        Args:
            weather_data: Formatted weather data
            
        Returns:
            Natural language description of weather
        """
        if not weather_data.get("success"):
            return f"Error fetching weather data: {weather_data.get('error', 'Unknown error')}"
        
        data = weather_data.get("data", {})
        location = data.get("location", {})
        current = data.get("current", {})
        weather = current.get("weather", {})
        
        response_parts = [
            f"Current weather for coordinates ({location.get('latitude')}, {location.get('longitude')}):",
            f"Temperature: {current.get('temperature')}°",
            f"Feels like: {current.get('feels_like')}°",
            f"Conditions: {weather.get('description', 'N/A')}",
            f"Humidity: {current.get('humidity')}%",
            f"Wind speed: {current.get('wind_speed')} m/s",
            f"Pressure: {current.get('pressure')} hPa"
        ]
        
        return "\n".join(response_parts)
