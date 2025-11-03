#!/usr/bin/env python3
"""
Example client for the Weather MCP Server.
Demonstrates how to interact with the weather API.
"""

import requests
import sys
from typing import Optional


class WeatherClient:
    """Client for interacting with Weather MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client with base URL."""
        self.base_url = base_url
    
    def get_weather(
        self,
        latitude: float,
        longitude: float,
        units: str = "metric",
        formatted: bool = True
    ) -> Optional[dict]:
        """
        Get weather for coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Unit system (metric, imperial, standard)
            formatted: Whether to get formatted response
            
        Returns:
            Weather data or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "units": units,
                    "formatted": formatted
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if server is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def format_weather_output(data: dict) -> str:
    """Format weather data for display."""
    if not data.get("success"):
        return f"Error: {data.get('error', 'Unknown error')}"
    
    weather_data = data.get("data", {})
    location = weather_data.get("location", {})
    current = weather_data.get("current", {})
    weather = current.get("weather", {})
    
    output = [
        "\n" + "="*50,
        "WEATHER INFORMATION",
        "="*50,
        f"Timezone: {location.get('timezone')}",
        "",
        "Current Conditions:",
        f"  Temperature: {current.get('temperature')}°",
        f"  Feels like: {current.get('feels_like')}°",
        f"  Conditions: {weather.get('description', 'N/A')}",
        f"  Humidity: {current.get('humidity')}%",
        f"  Pressure: {current.get('pressure')} hPa",
        f"  Wind Speed: {current.get('wind_speed')} m/s",
        f"  Clouds: {current.get('clouds')}%",
        f"  Visibility: {current.get('visibility')} m",
        "="*50
    ]
    
    return "\n".join(output)


def main():
    """Main function to demonstrate client usage."""
    # Example coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060
    
    # Parse command line arguments
    if len(sys.argv) >= 3:
        try:
            latitude = float(sys.argv[1])
            longitude = float(sys.argv[2])
        except ValueError:
            print("Usage: python example_client.py [latitude] [longitude]")
            print("Example: python example_client.py 40.7128 -74.0060")
            sys.exit(1)
    
    # Create client
    client = WeatherClient()
    
    # Check server health
    print("Checking server health...")
    if not client.health_check():
        print("Error: Server is not responding. Make sure it's running.")
        sys.exit(1)
    print("Server is healthy!\n")
    
    # Get weather
    print("Fetching weather data...")
    weather_data = client.get_weather(latitude, longitude, units="metric")
    
    if weather_data:
        print(format_weather_output(weather_data))
    else:
        print("Failed to fetch weather data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
