import logging
from typing import Dict, Any, Optional
import requests
from src.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """Service to fetch weather data from OpenWeatherMap One Call API."""
    
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
    
    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        units: str = "metric",
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetch current weather data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Unit system (metric, imperial, or standard)
            lang: Language code for weather descriptions
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
        
        # Prepare API request
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": units,
            "lang": lang,
            "exclude": "minutely,hourly,daily,alerts"  # Only get current weather
        }
        
        try:
            logger.info(f"Fetching weather for coordinates: ({latitude}, {longitude})")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully fetched weather data")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching weather data: {e}")
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            elif response.status_code == 404:
                raise ValueError("Location not found")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            raise
    
    def format_weather_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw API response into a more user-friendly structure.
        
        Args:
            raw_data: Raw response from OpenWeatherMap API
            
        Returns:
            Formatted weather data
        """
        current = raw_data.get("current", {})
        
        formatted = {
            "location": {
                "latitude": raw_data.get("lat"),
                "longitude": raw_data.get("lon"),
                "timezone": raw_data.get("timezone")
            },
            "current": {
                "timestamp": current.get("dt"),
                "temperature": current.get("temp"),
                "feels_like": current.get("feels_like"),
                "pressure": current.get("pressure"),
                "humidity": current.get("humidity"),
                "dew_point": current.get("dew_point"),
                "uvi": current.get("uvi"),
                "clouds": current.get("clouds"),
                "visibility": current.get("visibility"),
                "wind_speed": current.get("wind_speed"),
                "wind_deg": current.get("wind_deg"),
                "weather": current.get("weather", [{}])[0] if current.get("weather") else {}
            }
        }
        
        return formatted
