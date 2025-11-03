"""
MCP Client module.
Provides client functionality to interact with the MCP server.
"""

import os
import requests
from typing import Dict, Any, Optional


class MCPClientError(Exception):
    """Custom exception for MCP Client errors."""
    pass


class MCPClient:
    """Client for interacting with the Weather MCP Server."""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize the MCP client.
        
        Args:
            host: Server host (defaults to MCP_SERVER_HOST env var or "localhost")
            port: Server port (defaults to MCP_SERVER_PORT env var or 8000)
        """
        self.host = host or os.environ.get("MCP_SERVER_HOST", "localhost")
        self.port = port or int(os.environ.get("MCP_SERVER_PORT", "8000"))
        self.base_url = f"http://{self.host}:{self.port}"
    
    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch weather data from the MCP server.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            MCPClientError: If request fails
        """
        url = f"{self.base_url}/weather"
        params = {"lat": latitude, "lon": longitude}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise MCPClientError(f"Failed to fetch weather data from server: {str(e)}")
    
    def display_weather(self, weather_data: Dict[str, Any]) -> None:
        """
        Display weather data in a readable format.
        
        Args:
            weather_data: Weather data dictionary from server
        """
        if weather_data.get("status") != "success":
            print("Error: Invalid response from server")
            return
        
        data = weather_data.get("data", {})
        
        print("\n" + "=" * 50)
        print("WEATHER INFORMATION")
        print("=" * 50)
        print(f"Location: Lat {data.get('lat')}, Lon {data.get('lon')}")
        print(f"Timezone: {data.get('timezone')}")
        print("-" * 50)
        print(f"Weather: {data.get('weather')} ({data.get('weather_main')})")
        print(f"Temperature: {data.get('temperature')}°C")
        print(f"Feels Like: {data.get('feels_like')}°C")
        print(f"Humidity: {data.get('humidity')}%")
        print(f"Pressure: {data.get('pressure')} hPa")
        print(f"Wind Speed: {data.get('wind_speed')} m/s")
        print(f"Wind Direction: {data.get('wind_deg')}°")
        print(f"Clouds: {data.get('clouds')}%")
        print(f"Visibility: {data.get('visibility')} meters")
        print(f"UV Index: {data.get('uvi')}")
        print("=" * 50 + "\n")


def run_client(latitude: float, longitude: float, host: str = None, port: int = None):
    """
    Run the MCP client to fetch and display weather data.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        host: Server host (optional)
        port: Server port (optional)
    """
    try:
        client = MCPClient(host=host, port=port)
        print(f"Connecting to Weather MCP Server at {client.base_url}")
        weather_data = client.get_weather(latitude, longitude)
        client.display_weather(weather_data)
    except MCPClientError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python mcp_client.py <latitude> <longitude>")
        sys.exit(1)
    
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    sys.exit(run_client(lat, lon))
