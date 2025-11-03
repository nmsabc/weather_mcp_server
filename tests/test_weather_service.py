"""Tests for the weather service."""

import pytest
from unittest.mock import Mock, patch
from src.weather_service import WeatherService


class TestWeatherService:
    """Test cases for WeatherService."""
    
    @pytest.fixture
    def weather_service(self):
        """Create a weather service instance."""
        with patch('src.weather_service.settings') as mock_settings:
            mock_settings.openweather_api_key = "test_api_key"
            mock_settings.openweather_base_url = "https://api.openweathermap.org/data/3.0/onecall"
            return WeatherService()
    
    def test_invalid_latitude(self, weather_service):
        """Test that invalid latitude raises ValueError."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            weather_service.get_current_weather(latitude=95, longitude=0)
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            weather_service.get_current_weather(latitude=-95, longitude=0)
    
    def test_invalid_longitude(self, weather_service):
        """Test that invalid longitude raises ValueError."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            weather_service.get_current_weather(latitude=0, longitude=185)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            weather_service.get_current_weather(latitude=0, longitude=-185)
    
    @patch('src.weather_service.requests.get')
    def test_successful_weather_fetch(self, mock_get, weather_service):
        """Test successful weather data fetch."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 40.7128,
            "lon": -74.006,
            "timezone": "America/New_York",
            "current": {
                "dt": 1699036800,
                "temp": 15.5,
                "feels_like": 14.8,
                "pressure": 1013,
                "humidity": 65,
                "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}]
            }
        }
        mock_get.return_value = mock_response
        
        result = weather_service.get_current_weather(latitude=40.7128, longitude=-74.006)
        
        assert result["lat"] == 40.7128
        assert result["lon"] == -74.006
        assert "current" in result
    
    @patch('src.weather_service.requests.get')
    def test_api_key_error(self, mock_get, weather_service):
        """Test handling of invalid API key."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="Invalid API key"):
            weather_service.get_current_weather(latitude=40.7128, longitude=-74.006)
    
    def test_format_weather_response(self, weather_service):
        """Test weather response formatting."""
        raw_data = {
            "lat": 40.7128,
            "lon": -74.006,
            "timezone": "America/New_York",
            "current": {
                "dt": 1699036800,
                "temp": 15.5,
                "feels_like": 14.8,
                "pressure": 1013,
                "humidity": 65,
                "clouds": 20,
                "visibility": 10000,
                "wind_speed": 3.5,
                "wind_deg": 180,
                "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}]
            }
        }
        
        formatted = weather_service.format_weather_response(raw_data)
        
        assert formatted["location"]["latitude"] == 40.7128
        assert formatted["location"]["longitude"] == -74.006
        assert formatted["current"]["temperature"] == 15.5
        assert formatted["current"]["humidity"] == 65
