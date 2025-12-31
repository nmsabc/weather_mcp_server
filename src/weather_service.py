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
            logger.info("Fetching weather data from API")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully fetched weather data")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching weather data: {e}")
            # Check response status code if available
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise ValueError("Invalid API key")
                elif e.response.status_code == 404:
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

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        units: str = "metric",
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetch weather forecast data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Unit system (metric, imperial, or standard)
            lang: Language code for weather descriptions
            
        Returns:
            Dictionary containing forecast data (current + daily + hourly)
            
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
        
        # Prepare API request - include all data for forecast
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": units,
            "lang": lang
        }
        
        try:
            logger.info("Fetching forecast data from API")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully fetched forecast data")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching forecast data: {e}")
            # Check response status code if available
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise ValueError("Invalid API key")
                elif e.response.status_code == 404:
                    raise ValueError("Location not found")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            raise

    def format_forecast_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw forecast API response into a more user-friendly structure.
        
        Args:
            raw_data: Raw response from OpenWeatherMap API (One Call API)
            
        Returns:
            Formatted forecast data with current, daily, and hourly info
        """
        current = raw_data.get("current", {})
        daily = raw_data.get("daily", [])
        hourly = raw_data.get("hourly", [])
        
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
                "uvi": current.get("uvi"),
                "clouds": current.get("clouds"),
                "visibility": current.get("visibility"),
                "wind_speed": current.get("wind_speed"),
                "wind_deg": current.get("wind_deg"),
                "weather": current.get("weather", [{}])[0] if current.get("weather") else {}
            },
            "daily": [
                {
                    "dt": day.get("dt"),
                    "temp": {
                        "day": day.get("temp", {}).get("day"),
                        "min": day.get("temp", {}).get("min"),
                        "max": day.get("temp", {}).get("max"),
                        "night": day.get("temp", {}).get("night"),
                        "eve": day.get("temp", {}).get("eve"),
                        "morn": day.get("temp", {}).get("morn")
                    },
                    "feels_like": {
                        "day": day.get("feels_like", {}).get("day"),
                        "night": day.get("feels_like", {}).get("night"),
                        "eve": day.get("feels_like", {}).get("eve"),
                        "morn": day.get("feels_like", {}).get("morn")
                    },
                    "pressure": day.get("pressure"),
                    "humidity": day.get("humidity"),
                    "wind_speed": day.get("wind_speed"),
                    "wind_deg": day.get("wind_deg"),
                    "clouds": day.get("clouds"),
                    "rain": day.get("rain", 0),
                    "snow": day.get("snow", 0),
                    "weather": day.get("weather", [{}])[0] if day.get("weather") else {}
                }
                for day in daily
            ],
            "hourly": [
                {
                    "dt": hour.get("dt"),
                    "temperature": hour.get("temp"),
                    "feels_like": hour.get("feels_like"),
                    "humidity": hour.get("humidity"),
                    "wind_speed": hour.get("wind_speed"),
                    "weather": hour.get("weather", [{}])[0] if hour.get("weather") else {}
                }
                for hour in hourly
            ]
        }
        
        return formatted
