"""
MCP Server module using FastAPI.
Exposes HTTP endpoints for weather data retrieval and MCP stdio interface.
"""

import os
import sys
import json
import logging
import threading
import time
import requests
from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any, Optional
import uvicorn

from weather_api import OpenWeatherMapAPI, WeatherAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Weather MCP Server",
    description="Weather data microservice with MCP wrapper for OpenWeatherMap API",
    version="1.0.0"
)


# Initialize weather API client
try:
    weather_client = OpenWeatherMapAPI()
except WeatherAPIError as e:
    logger.warning(f"Weather API client initialization: {e}")
    weather_client = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Weather MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "/weather": "Get current weather data for latitude and longitude",
            "/forecast": "Get current weather and forecast (hourly and daily) for latitude and longitude"
        }
    }


@app.get("/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    lon: float = Query(..., description="Longitude coordinate", ge=-180, le=180)
) -> Dict[str, Any]:
    """
    Get current weather data for specified coordinates.
    
    Args:
        lat: Latitude coordinate (-90 to 90)
        lon: Longitude coordinate (-180 to 180)
        
    Returns:
        Dictionary containing current weather data
        
    Raises:
        HTTPException: If weather data cannot be retrieved
    """
    if weather_client is None:
        raise HTTPException(
            status_code=500,
            detail="Weather API client not initialized. Check API key configuration."
        )
    
    try:
        raw_weather = weather_client.get_current_weather(lat, lon)
        formatted_weather = weather_client.format_weather_data(raw_weather)
        return {
            "status": "success",
            "data": formatted_weather
        }
    except WeatherAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/forecast")
async def get_forecast(
    lat: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    lon: float = Query(..., description="Longitude coordinate", ge=-180, le=180)
) -> Dict[str, Any]:
    """
    Get current weather and forecast data for specified coordinates.
    
    Args:
        lat: Latitude coordinate (-90 to 90)
        lon: Longitude coordinate (-180 to 180)
        
    Returns:
        Dictionary containing current weather, hourly (48h), and daily (8d) forecast data
        
    Raises:
        HTTPException: If forecast data cannot be retrieved
    """
    if weather_client is None:
        raise HTTPException(
            status_code=500,
            detail="Weather API client not initialized. Check API key configuration."
        )
    
    try:
        raw_forecast = weather_client.get_forecast(lat, lon)
        formatted_forecast = weather_client.format_forecast_data(raw_forecast)
        return {
            "status": "success",
            "data": formatted_forecast
        }
    except WeatherAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def run_server(host: Optional[str] = None, port: Optional[int] = None):
    """
    Run the MCP server in HTTP mode (blocking).
    
    Args:
        host: Host address (defaults to MCP_SERVER_HOST env var or "0.0.0.0")
        port: Port number (defaults to MCP_SERVER_PORT env var or 8000)
    """
    host = host or os.environ.get("MCP_SERVER_HOST", "0.0.0.0")
    port = port or int(os.environ.get("MCP_SERVER_PORT", "8000"))
    
    logger.info(f"Starting Weather MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


def run_mcp_stdio_server(host: Optional[str] = None, port: Optional[int] = None):
    """
    Run the MCP server in stdio mode (non-blocking).
    Starts HTTP server in background thread and handles MCP JSON-RPC messages via stdin/stdout.
    
    Args:
        host: Host address for HTTP server (defaults to "127.0.0.1")
        port: Port number for HTTP server (defaults to 8000)
    """
    host = host or os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    port = port or int(os.environ.get("MCP_SERVER_PORT", "8000"))
    startup_wait = float(os.environ.get("MCP_SERVER_STARTUP_WAIT", "2.0"))
    
    # Start HTTP server in background thread
    def run_uvicorn_background():
        """Run Uvicorn in background thread."""
        uvicorn.run(app, host=host, port=port, log_level="error")
    
    server_thread = threading.Thread(target=run_uvicorn_background, daemon=True)
    server_thread.start()
    
    # Give server time to start (configurable via environment variable)
    time.sleep(startup_wait)
    logger.info(f"Weather MCP Server HTTP backend started on {host}:{port}")
    logger.info("MCP stdio interface ready - reading from stdin")
    
    # Base URL for internal HTTP calls
    base_url = f"http://{host}:{port}"
    
    # Process MCP messages from stdin
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                # EOF - clean shutdown
                logger.info("stdin closed, shutting down")
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse JSON-RPC message
                message = json.loads(line)
                response = handle_mcp_message(message, base_url)
                
                # Write response to stdout
                if response:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id") if isinstance(message, dict) else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    
    logger.info("MCP server stopped")


def handle_mcp_message(message: Dict[str, Any], base_url: str) -> Optional[Dict[str, Any]]:
    """
    Handle an MCP JSON-RPC message.
    
    Args:
        message: JSON-RPC message
        base_url: Base URL for HTTP backend
        
    Returns:
        JSON-RPC response or None for notifications
    """
    jsonrpc = message.get("jsonrpc")
    msg_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})
    
    # Handle initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "weather-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    # Handle tools/list
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "get_weather",
                        "description": "Get current weather data for a location",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate (-90 to 90)",
                                    "minimum": -90,
                                    "maximum": 90
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate (-180 to 180)",
                                    "minimum": -180,
                                    "maximum": 180
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    },
                    {
                        "name": "get_forecast",
                        "description": "Get weather forecast (hourly 48h + daily 8d) for a location",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate (-90 to 90)",
                                    "minimum": -90,
                                    "maximum": 90
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate (-180 to 180)",
                                    "minimum": -180,
                                    "maximum": 180
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    }
                ]
            }
        }
    
    # Handle tools/call
    if method == "tools/call":
        return handle_tool_call(msg_id, params, base_url)
    
    # Handle notifications (no response needed)
    if msg_id is None:
        return None
    
    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}"
        }
    }


def call_http_endpoint(base_url: str, endpoint: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    Call an HTTP endpoint and return the response data.
    
    Args:
        base_url: Base URL for HTTP backend
        endpoint: Endpoint path (e.g., "/weather" or "/forecast")
        lat: Latitude
        lon: Longitude
        
    Returns:
        Response data from endpoint
        
    Raises:
        requests.RequestException: If HTTP request fails
    """
    response = requests.get(
        f"{base_url}{endpoint}",
        params={"lat": lat, "lon": lon},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def handle_tool_call(msg_id: Optional[int], params: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    """
    Handle a tools/call JSON-RPC method.
    
    Args:
        msg_id: Message ID
        params: Tool call parameters
        base_url: Base URL for HTTP backend
        
    Returns:
        JSON-RPC response
    """
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})
    
    try:
        lat = tool_args.get("latitude")
        lon = tool_args.get("longitude")
        
        if lat is None or lon is None:
            raise ValueError("latitude and longitude are required")
        
        # Route to appropriate endpoint
        if tool_name == "get_weather":
            data = call_http_endpoint(base_url, "/weather", lat, lon)
        elif tool_name == "get_forecast":
            data = call_http_endpoint(base_url, "/forecast", lat, lon)
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(data, indent=2)
                    }
                ]
            }
        }
        
    except requests.RequestException as e:
        error_msg = f"HTTP request failed: {type(e).__name__}"
        logger.error(f"{error_msg} - {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32603,
                "message": error_msg
            }
        }
    except Exception as e:
        error_msg = f"Tool execution failed: {type(e).__name__}"
        logger.error(f"{error_msg} - {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32603,
                "message": error_msg
            }
        }


if __name__ == "__main__":
    # Check if running in MCP mode (stdio interface)
    if os.environ.get("MCP_MODE") == "stdio":
        run_mcp_stdio_server()
    else:
        run_server()
