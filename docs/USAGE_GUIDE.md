# Weather MCP Server - Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [HTTP Mode Usage](#http-mode-usage)
4. [MCP Stdio Mode Usage](#mcp-stdio-mode-usage)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)

## Installation

```bash
cd weather_mcp_server
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables

```bash
export OPENWEATHER_API_KEY="your_openweathermap_api_key"
```

### Optional Environment Variables

```bash
export MCP_SERVER_HOST="127.0.0.1"  # Default: 0.0.0.0 (HTTP mode), 127.0.0.1 (MCP mode)
export MCP_SERVER_PORT="8000"       # Default: 8000
export MCP_MODE="stdio"             # Set to enable MCP stdio mode
```

## HTTP Mode Usage

### Starting the Server

**Basic:**
```bash
export OPENWEATHER_API_KEY="your_key"
python main.py server
```

**Custom host/port:**
```bash
python main.py server --host 0.0.0.0 --port 8080
```

### Using the Client

**Current Weather:**
```bash
# In a separate terminal
python main.py client --lat 40.7128 --lon -74.0060
```

**Weather Forecast:**
```bash
python main.py forecast --lat 40.7128 --lon -74.0060
```

**Direct HTTP Calls:**
```bash
# Current weather
curl "http://localhost:8000/weather?lat=40.7128&lon=-74.0060"

# Forecast
curl "http://localhost:8000/forecast?lat=40.7128&lon=-74.0060"
```

### Example Output (HTTP Mode)

```
==================================================
WEATHER INFORMATION
==================================================
Location: Lat 40.7128, Lon -74.006
Timezone: America/New_York
--------------------------------------------------
Weather: clear sky (Clear)
Temperature: 15.5°C
Feels Like: 14.2°C
Humidity: 65%
Pressure: 1013 hPa
Wind Speed: 3.5 m/s
Wind Direction: 180°
Clouds: 10%
Visibility: 10000 meters
UV Index: 5.2
==================================================
```

## MCP Stdio Mode Usage

### Starting in MCP Mode

**Option 1: Using --mcp flag**
```bash
export OPENWEATHER_API_KEY="your_key"
python main.py server --mcp
```

**Option 2: Using environment variable**
```bash
export OPENWEATHER_API_KEY="your_key"
export MCP_MODE="stdio"
python mcp_server.py
```

**Option 3: Direct Python execution**
```bash
export OPENWEATHER_API_KEY="your_key"
export MCP_MODE="stdio"
python -c "from mcp_server import run_mcp_stdio_server; run_mcp_stdio_server()"
```

### MCP Configuration File

For use with MCP CLI or multi-server setups, create a configuration file:

**mcp_config.json:**
```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/weather_mcp_server/main.py", "server", "--mcp"],
      "env": {
        "OPENWEATHER_API_KEY": "your_key_here"
      }
    }
  }
}
```

Or using direct module execution:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/weather_mcp_server/mcp_server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_key_here",
        "MCP_MODE": "stdio"
      }
    }
  }
}
```

### MCP JSON-RPC Messages

**Initialize:**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}},
    "serverInfo": {
      "name": "weather-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

**List Tools:**
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather data for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180}
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
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180}
          },
          "required": ["latitude", "longitude"]
        }
      }
    ]
  }
}
```

**Call Tool - Get Weather:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"temperature\": 15.5,\n    ...\n  }\n}"
      }
    ]
  }
}
```

**Call Tool - Get Forecast:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_forecast",
    "arguments": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}
```

## API Reference

### HTTP Endpoints

#### GET /
Service information endpoint.

**Response:**
```json
{
  "service": "Weather MCP Server",
  "version": "1.0.0",
  "endpoints": {
    "/weather": "Get current weather data for latitude and longitude",
    "/forecast": "Get current weather and forecast (hourly and daily) for latitude and longitude"
  }
}
```

#### GET /weather
Get current weather data.

**Parameters:**
- `lat` (float, required): Latitude (-90 to 90)
- `lon` (float, required): Longitude (-180 to 180)

**Response:**
```json
{
  "status": "success",
  "data": {
    "temperature": 20.5,
    "feels_like": 19.8,
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 3.5,
    "wind_deg": 180,
    "weather": "clear sky",
    "weather_main": "Clear",
    "clouds": 10,
    "visibility": 10000,
    "uvi": 5.2,
    "timezone": "America/Chicago",
    "lat": 33.44,
    "lon": -94.04
  }
}
```

#### GET /forecast
Get weather forecast (current + hourly 48h + daily 8d).

**Parameters:**
- `lat` (float, required): Latitude (-90 to 90)
- `lon` (float, required): Longitude (-180 to 180)

**Response:**
```json
{
  "status": "success",
  "data": {
    "current": { /* current weather data */ },
    "hourly": [ /* 48 hours of hourly forecasts */ ],
    "daily": [ /* 8 days of daily forecasts */ ],
    "timezone": "America/Chicago"
  }
}
```

### MCP Tools

#### get_weather
Get current weather data for a location.

**Input:**
- `latitude` (number): Latitude coordinate (-90 to 90)
- `longitude` (number): Longitude coordinate (-180 to 180)

**Output:**
Text content with JSON-formatted weather data.

#### get_forecast
Get weather forecast for a location.

**Input:**
- `latitude` (number): Latitude coordinate (-90 to 90)
- `longitude` (number): Longitude coordinate (-180 to 180)

**Output:**
Text content with JSON-formatted forecast data (current + hourly + daily).

## Troubleshooting

### Server Won't Start (HTTP Mode)

**Error:** `Address already in use`
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
python main.py server --port 8001
```

### API Key Not Found

**Error:** `Weather API client not initialized`
```bash
# Make sure to export the API key before starting
export OPENWEATHER_API_KEY="your_key"
python main.py server
```

### Client Can't Connect

**Error:** `Connection refused`
```bash
# Make sure server is running first
# Terminal 1:
python main.py server

# Terminal 2:
python main.py client --lat 33.44 --lon -94.04
```

### MCP Mode Not Working

**Issue:** Server blocks in MCP mode

**Solution:** Make sure you're using the --mcp flag:
```bash
python main.py server --mcp
# NOT just: python main.py server
```

### Invalid JSON-RPC Messages

**Error:** Parse error in MCP mode

**Solution:** Ensure messages are proper JSON-RPC 2.0 format:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

### HTTP Backend Not Starting in MCP Mode

**Issue:** Tools return connection errors

**Possible causes:**
1. Port already in use - change `MCP_SERVER_PORT`
2. Firewall blocking localhost - check firewall settings
3. Not enough time to start - increase sleep delay in code

## Performance Tips

### HTTP Mode
- Use connection pooling for multiple requests
- Cache responses when appropriate
- Set reasonable timeouts

### MCP Mode
- HTTP backend is internal and fast
- No network overhead for tool calls
- Background thread doesn't impact performance

## Security Notes

1. **API Key Protection:** Never commit API keys to version control
2. **Localhost Only:** MCP mode binds to 127.0.0.1 by default
3. **HTTP Mode:** Use 0.0.0.0 carefully in production
4. **Rate Limiting:** OpenWeatherMap free tier: 1,000 calls/day
5. **HTTPS:** Consider reverse proxy for production HTTP mode
