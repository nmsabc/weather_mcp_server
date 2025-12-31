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
    
    def get_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch weather forecast data including hourly and daily forecasts.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary containing current weather and forecast data
            
        Raises:
            WeatherAPIError: If API request fails
        """
        # Note: Not including 'exclude' parameter to get all forecast data (current, hourly, daily)
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"  # Use metric units for temperature
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Failed to fetch forecast data: {str(e)}")
    
    def format_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw weather data into a concise response.
        
        Args:
            weather_data: Raw weather data from API
            
        Returns:
            Formatted dictionary with relevant weather information
        """
        current = weather_data.get("current", {})
        weather_list = current.get("weather", [{}])
        weather_info = weather_list[0] if weather_list else {}
        
        formatted = {
            "temperature": current.get("temp"),
            "feels_like": current.get("feels_like"),
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure"),
            "wind_speed": current.get("wind_speed"),
            "wind_deg": current.get("wind_deg"),
            "weather": weather_info.get("description", "N/A"),
            "weather_main": weather_info.get("main", "N/A"),
            "clouds": current.get("clouds"),
            "visibility": current.get("visibility"),
            "uvi": current.get("uvi"),
            "timezone": weather_data.get("timezone"),
            "lat": weather_data.get("lat"),
            "lon": weather_data.get("lon")
        }
        
        return formatted
    
    def format_forecast_data(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw forecast data into a concise response.
        
        Args:
            forecast_data: Raw forecast data from API
            
        Returns:
            Formatted dictionary with current weather and forecast information
        """
        # Format current weather
        current_formatted = self.format_weather_data(forecast_data)
        
        # Format hourly forecast (next 48 hours)
        hourly_list = forecast_data.get("hourly", [])
        hourly_formatted = []
        for hour in hourly_list[:48]:  # Limit to 48 hours
            weather_list = hour.get("weather", [{}])
            weather_info = weather_list[0] if weather_list else {}
            hourly_formatted.append({
                "dt": hour.get("dt"),
                "temp": hour.get("temp"),
                "feels_like": hour.get("feels_like"),
                "humidity": hour.get("humidity"),
                "weather": weather_info.get("description", "N/A"),
                "weather_main": weather_info.get("main", "N/A"),
                "pop": hour.get("pop"),  # Probability of precipitation
                "wind_speed": hour.get("wind_speed")
            })
        
        # Format daily forecast (next 8 days)
        daily_list = forecast_data.get("daily", [])
        daily_formatted = []
        for day in daily_list[:8]:  # Limit to 8 days
            weather_list = day.get("weather", [{}])
            weather_info = weather_list[0] if weather_list else {}
            temp = day.get("temp", {})
            daily_formatted.append({
                "dt": day.get("dt"),
                "temp_min": temp.get("min"),
                "temp_max": temp.get("max"),
                "temp_day": temp.get("day"),
                "temp_night": temp.get("night"),
                "humidity": day.get("humidity"),
                "weather": weather_info.get("description", "N/A"),
                "weather_main": weather_info.get("main", "N/A"),
                "pop": day.get("pop"),  # Probability of precipitation
                "wind_speed": day.get("wind_speed"),
                "uvi": day.get("uvi")
            })
        
        return {
            "current": current_formatted,
            "hourly": hourly_formatted,
            "daily": daily_formatted,
            "timezone": forecast_data.get("timezone")
        }
