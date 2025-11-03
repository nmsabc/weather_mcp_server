#!/usr/bin/env python3
"""
Example script demonstrating various ways to use the Weather MCP Server.
This can be run independently to test the service.
"""

import os
import time
import subprocess
import requests
from mcp_client import MCPClient


def example_direct_api_call():
    """Example: Direct HTTP API call to the server."""
    print("\n" + "=" * 60)
    print("Example 1: Direct HTTP API Call")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    print(f"\nCalling {base_url}/")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test weather endpoint
    lat, lon = 40.7128, -74.0060  # New York City
    print(f"\nCalling {base_url}/weather?lat={lat}&lon={lon}")
    response = requests.get(f"{base_url}/weather", params={"lat": lat, "lon": lon})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        weather_data = data.get("data", {})
        print(f"\nWeather in NYC:")
        print(f"  Temperature: {weather_data.get('temperature')}°C")
        print(f"  Conditions: {weather_data.get('weather')}")
        print(f"  Humidity: {weather_data.get('humidity')}%")
    else:
        print(f"Error: {response.text}")


def example_python_client():
    """Example: Using the Python MCP Client."""
    print("\n" + "=" * 60)
    print("Example 2: Using Python MCP Client")
    print("=" * 60)
    
    client = MCPClient(host="localhost", port=8000)
    
    # Fetch weather for London
    lat, lon = 51.5074, -0.1278
    print(f"\nFetching weather for London (lat={lat}, lon={lon})")
    
    try:
        weather_data = client.get_weather(lat, lon)
        client.display_weather(weather_data)
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_locations():
    """Example: Fetch weather for multiple locations."""
    print("\n" + "=" * 60)
    print("Example 3: Multiple Locations")
    print("=" * 60)
    
    # Check if user wants to run this example (requires valid API key and makes multiple calls)
    run_multiple = os.environ.get("WEATHER_EXAMPLE_MULTIPLE", "false").lower() == "true"
    
    if not run_multiple:
        print("\nSkipped: This example makes multiple API calls.")
        print("Set WEATHER_EXAMPLE_MULTIPLE=true to enable this example.")
        return
    
    locations = [
        ("New York", 40.7128, -74.0060),
        ("London", 51.5074, -0.1278),
        ("Tokyo", 35.6762, 139.6503),
        ("Sydney", -33.8688, 151.2093),
    ]
    
    client = MCPClient(host="localhost", port=8000)
    
    for city, lat, lon in locations:
        print(f"\n{city}:")
        print("-" * 40)
        try:
            weather_data = client.get_weather(lat, lon)
            data = weather_data.get("data", {})
            print(f"  Temperature: {data.get('temperature')}°C")
            print(f"  Weather: {data.get('weather')}")
            print(f"  Humidity: {data.get('humidity')}%")
            print(f"  Wind: {data.get('wind_speed')} m/s")
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(1)  # Rate limiting


def main():
    """Main function to run all examples."""
    print("=" * 60)
    print("Weather MCP Server - Usage Examples")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  python main.py server")
    print("\nPress Enter to continue...")
    input()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running!")
        else:
            print("✗ Server responded with unexpected status")
            return
    except requests.exceptions.RequestException:
        print("✗ Server is not running. Please start it first:")
        print("  python main.py server")
        return
    
    # Run examples
    example_direct_api_call()
    
    example_python_client()
    
    # Optional: Multiple locations example (controlled by environment variable)
    example_multiple_locations()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
