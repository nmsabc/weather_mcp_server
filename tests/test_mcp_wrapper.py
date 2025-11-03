"""Tests for the MCP wrapper."""

import pytest
from unittest.mock import Mock, patch
from src.mcp_wrapper import MCPWeatherWrapper


class TestMCPWeatherWrapper:
    """Test cases for MCPWeatherWrapper."""
    
    @pytest.fixture
    def mcp_wrapper(self):
        """Create an MCP wrapper instance."""
        with patch('src.mcp_wrapper.WeatherService'):
            return MCPWeatherWrapper()
    
    def test_get_tools(self, mcp_wrapper):
        """Test that get_tools returns tool definitions."""
        tools = mcp_wrapper.get_tools()
        
        assert len(tools) > 0
        assert tools[0]["name"] == "get_current_weather"
        assert "parameters" in tools[0]
        assert "latitude" in tools[0]["parameters"]["properties"]
        assert "longitude" in tools[0]["parameters"]["properties"]
    
    def test_execute_unknown_tool(self, mcp_wrapper):
        """Test executing an unknown tool."""
        result = mcp_wrapper.execute_tool("unknown_tool", {})
        
        assert result["success"] is False
        assert "Unknown tool" in result["error"]
    
    @patch.object(MCPWeatherWrapper, '_get_current_weather')
    def test_execute_get_current_weather(self, mock_method, mcp_wrapper):
        """Test executing get_current_weather tool."""
        mock_method.return_value = {"success": True, "data": {}}
        
        result = mcp_wrapper.execute_tool("get_current_weather", {
            "latitude": 40.7128,
            "longitude": -74.006
        })
        
        mock_method.assert_called_once()
        assert result["success"] is True
    
    def test_create_llm_response_success(self, mcp_wrapper):
        """Test creating LLM response from weather data."""
        weather_data = {
            "success": True,
            "data": {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.006,
                    "timezone": "America/New_York"
                },
                "current": {
                    "temperature": 15.5,
                    "feels_like": 14.8,
                    "humidity": 65,
                    "wind_speed": 3.5,
                    "pressure": 1013,
                    "weather": {
                        "description": "clear sky"
                    }
                }
            }
        }
        
        response = mcp_wrapper.create_llm_response(weather_data)
        
        assert "40.7128" in response
        assert "15.5" in response
        assert "clear sky" in response
    
    def test_create_llm_response_error(self, mcp_wrapper):
        """Test creating LLM response from error data."""
        weather_data = {
            "success": False,
            "error": "API error"
        }
        
        response = mcp_wrapper.create_llm_response(weather_data)
        
        assert "Error" in response
        assert "API error" in response
