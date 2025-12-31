#!/usr/bin/env python3
"""Direct test of forecast functionality."""

import asyncio
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for proper imports
sys.path.insert(0, str(Path(__file__).parent))

from src.weather_service import WeatherService

async def test_forecast():
    """Test forecast functionality directly."""
    # Load environment
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ API key not found in .env file")
        return
    
    print(f"✅ API key loaded: {api_key[:10]}...")
    
    # Create weather service
    service = WeatherService()
    
    # Test current weather first
    print("\n🌡️  Testing get_current_weather...")
    try:
        current = service.get_current_weather(
            latitude=48.0085749,
            longitude=16.2334951,
            units="metric",
            lang="en"
        )
        formatted = service.format_weather_response(current)
        print(f"✅ Current weather retrieved successfully")
        print(f"   Temperature: {formatted['current'].get('temperature', 'N/A')}°C")
        print(f"   Conditions: {formatted['current'].get('weather', {}).get('description', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test forecast
    print("\n📅 Testing get_forecast...")
    try:
        forecast = service.get_forecast(
            latitude=48.0085749,
            longitude=16.2334951,
            units="metric",
            lang="en"
        )
        print(f"✅ Forecast API call successful")
        print(f"   Raw data keys: {forecast.keys()}")
        
        # Test formatting
        print("\n📊 Testing format_forecast_data...")
        formatted_forecast = service.format_forecast_data(forecast)
        print(f"✅ Forecast formatting successful")
        
        # Check structure
        location = formatted_forecast.get("location", {})
        current_fmt = formatted_forecast.get("current", {})
        daily = formatted_forecast.get("daily", [])
        
        print(f"   Location: ({location.get('latitude')}, {location.get('longitude')})")
        print(f"   Current temp: {current_fmt.get('temperature', 'N/A')}°C")
        print(f"   Daily forecasts available: {len(daily)}")
        
        if daily:
            first_day = daily[0]
            print(f"\n   First day forecast:")
            print(f"      Date: {first_day.get('dt', 'N/A')}")
            print(f"      Temp range: {first_day.get('temp', {}).get('min', 'N/A')}°C to {first_day.get('temp', {}).get('max', 'N/A')}°C")
            weather = first_day.get('weather', {})
            print(f"      Weather type: {type(weather)}")
            print(f"      Weather data: {weather}")
            if isinstance(weather, dict):
                print(f"      Conditions: {weather.get('description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_forecast())
