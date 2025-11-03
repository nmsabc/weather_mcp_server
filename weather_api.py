"""
OpenWeatherMap API integration module.
Handles fetching weather data from OpenWeatherMap One Call API v3.
"""

import os
import requests
from typing import Dict, Any, Optional


class WeatherAPIError(Exception):
    """Custom exception for Weather API errors."""
    pass


class OpenWeatherMapAPI:
    """Handles interactions with OpenWeatherMap One Call API v3."""
    
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenWeatherMap API client.
        
        Args:
            api_key: OpenWeatherMap API key. If not provided, reads from 
                     OPENWEATHER_API_KEY environment variable.
        
        Raises:
            WeatherAPIError: If API key is not provided or found.
        """
        self.api_key = api_key or os.environ.get("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise WeatherAPIError(
                "OpenWeatherMap API key not provided. "
                "Set OPENWEATHER_API_KEY environment variable or pass api_key parameter."
            )
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch current weather data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            WeatherAPIError: If API request fails
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "exclude": "hourly,daily",
            "appid": self.api_key,
            "units": "metric"  # Use metric units for temperature
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Failed to fetch weather data: {str(e)}")
    
    def format_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw weather data into a concise response.
        
        Args:
            weather_data: Raw weather data from API
            
        Returns:
            Formatted dictionary with relevant weather information
        """
        current = weather_data.get("current", {})
        
        formatted = {
            "temperature": current.get("temp"),
            "feels_like": current.get("feels_like"),
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure"),
            "wind_speed": current.get("wind_speed"),
            "wind_deg": current.get("wind_deg"),
            "weather": current.get("weather", [{}])[0].get("description", "N/A"),
            "weather_main": current.get("weather", [{}])[0].get("main", "N/A"),
            "clouds": current.get("clouds"),
            "visibility": current.get("visibility"),
            "uvi": current.get("uvi"),
            "timezone": weather_data.get("timezone"),
            "lat": weather_data.get("lat"),
            "lon": weather_data.get("lon")
        }
        
        return formatted
