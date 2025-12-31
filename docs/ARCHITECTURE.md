# Weather MCP Server - Architecture

## Overview

The Weather MCP Server is a Python-based microservice that provides weather data through the Model Context Protocol (MCP), enabling Large Language Models (LLMs) to access weather information in a standardized, structured format.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Client                               │
│                  (Claude, GPT, etc.)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    (stdin/stdout)
                    (JSON-RPC 2.0)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              MCP Server (mcp_server.py)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP Server Instance                                    │   │
│  │  - list_tools()                                        │   │
│  │  - call_tool()                                         │   │
│  │  - list_resources()                                    │   │
│  └────┬────────────────────────────────────┬──────────────┘   │
│       │                                    │                    │
│       │ Tool Registry                      │                    │
│   ┌───▼──────────────┐          ┌────────▼─────────────┐      │
│   │ get_current_     │          │ get_forecast        │      │
│   │ weather()        │          │ ()                  │      │
│   └───┬──────────────┘          └────────┬─────────────┘      │
│       │                                   │                     │
└───────┼───────────────────────────────────┼─────────────────────┘
        │                                   │
        │                                   │
    ┌───▼───────────────────────────────────▼──┐
    │     Helper Functions (mcp_server.py)     │
    ├──────────────────────────────────────────┤
    │  geocode_location()                      │
    │  - Converts place names to lat/lon       │
    │  - Uses OpenWeatherMap Geocoding API    │
    └──────────────┬───────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ OpenWeatherMap API  │
        │  (Geocoding)        │
        └─────────────────────┘
        
        ┌──────────────────────────────────────────────────────┐
        │     WeatherService (src/weather_service.py)          │
        ├──────────────────────────────────────────────────────┤
        │                                                      │
        │  ┌────────────────────────────────────────────────┐ │
        │  │ get_current_weather()                          │ │
        │  │  - Fetches current conditions                 │ │
        │  │  - Excludes hourly/daily from API call       │ │
        │  └────────────────┬───────────────────────────────┘ │
        │                   │                                  │
        │  ┌────────────────▼───────────────────────────────┐ │
        │  │ get_forecast()                                 │ │
        │  │  - Fetches full One Call API data             │ │
        │  │  - Includes current + daily + hourly          │ │
        │  └────────────────┬───────────────────────────────┘ │
        │                   │                                  │
        │  ┌────────────────▼───────────────────────────────┐ │
        │  │ format_weather_response()                      │ │
        │  │  - Formats current weather data               │ │
        │  │  - Uses safe dict.get() access patterns       │ │
        │  └────────────────┬───────────────────────────────┘ │
        │                   │                                  │
        │  ┌────────────────▼───────────────────────────────┐ │
        │  │ format_forecast_data()                         │ │
        │  │  - Formats daily + hourly forecast            │ │
        │  │  - Safe weather description access            │ │
        │  │  - Returns 8-day daily + 48h hourly          │ │
        │  └────────────────┬───────────────────────────────┘ │
        │                   │                                  │
        └───────────────────┼──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  OpenWeatherMap One Call API v3.0    │
        │  (Current + Daily + Hourly Forecast) │
        └──────────────────────────────────────┘
```

## Components

### 1. **MCP Server** (`mcp_server.py`)

**Purpose**: Main entry point implementing the Model Context Protocol

**Key Functions**:
- `list_tools()`: Returns available tools (get_current_weather, get_forecast)
- `call_tool()`: Routes tool calls to appropriate handlers
- `geocode_location(location)`: Async function converting place names to coordinates

**Tool Definitions**:
```
┌─ get_current_weather
│  ├─ Input: latitude, longitude, location, units, lang
│  └─ Output: Current conditions + formatted response
│
└─ get_forecast
   ├─ Input: latitude, longitude, location, units, lang
   └─ Output: 8-day daily + 48h hourly forecast + formatted response
```

**Communication Protocol**:
- **Transport**: stdin/stdout pipes
- **Protocol**: JSON-RPC 2.0
- **Flow**: LLM → MCP Server → OpenWeatherMap API → MCP Server → LLM

### 2. **Weather Service** (`src/weather_service.py`)

**Purpose**: Encapsulates all weather data fetching and formatting logic

**API Methods**:

#### `get_current_weather(latitude, longitude, units='metric', lang='en')`
- **API Endpoint**: One Call API with `exclude=hourly,daily,minutely,alerts`
- **Returns**: Current weather only (faster, smaller payload)
- **Validation**: Latitude (-90 to 90), Longitude (-180 to 180)

#### `get_forecast(latitude, longitude, units='metric', lang='en')`
- **API Endpoint**: One Call API (full data)
- **Returns**: Current + Daily (8 days) + Hourly (48 hours)
- **Validation**: Same coordinate ranges

#### `format_weather_response(raw_data)`
- **Input**: Raw OpenWeatherMap API response
- **Output**: Structured weather data with safe dict.get() access
- **Key Fix**: Safely accesses weather description from weather array

#### `format_forecast_data(raw_data)`
- **Input**: Raw One Call API response
- **Output**: Structured forecast with:
  - Location (lat, lon, timezone)
  - Current conditions
  - Daily forecast (8 days)
  - Hourly forecast (48 hours)
- **Key Fix**: Safe weather array access preventing IndexError

### 3. **Configuration** (`src/config.py`)

**Environment Variables**:
```python
OPENWEATHER_API_KEY      # Your API key from openweathermap.org
OPENWEATHER_BASE_URL     # API endpoint (default: https://api.openweathermap.org/data/3.0/onecall)
```

## Data Flow

### Current Weather Flow

```
User/LLM Request
    ↓
MCP call_tool("get_current_weather", {"location": "Baden bei Wien"})
    ↓
geocode_location("Baden bei Wien")
    → OpenWeatherMap Geocoding API
    → Returns: (48.0047, 16.2511)
    ↓
get_current_weather(48.0047, 16.2511)
    → OpenWeatherMap One Call API (exclude hourly, daily)
    → Returns: Current conditions only
    ↓
format_weather_response()
    → Safe dict.get() access to weather array
    → Structured response
    ↓
Natural Language Response (formatted with emoji)
    ↓
LLM Receives: "🌡️ Temperature: 5.2°C, 🌤️ Conditions: Partly Cloudy, ..."
```

### Forecast Flow

```
User/LLM Request
    ↓
MCP call_tool("get_forecast", {"location": "New York, NY"})
    ↓
geocode_location("New York, NY")
    → OpenWeatherMap Geocoding API
    → Returns: (40.7128, -74.0060)
    ↓
get_forecast(40.7128, -74.0060)
    → OpenWeatherMap One Call API (full data)
    → Returns: Current + Daily (8d) + Hourly (48h)
    ↓
format_forecast_data()
    → Extracts and structures:
        - Current conditions
        - Daily forecast (8 days with temp ranges)
        - Hourly forecast (48 hours)
    → Safe weather description access
    ↓
Natural Language Forecast Response
    ↓
LLM Receives: "📅 8-Day Forecast: Tomorrow 15-8°C with rain, ..."
```

## Data Models

### Weather Response Format

```json
{
  "location": {
    "latitude": 48.0047,
    "longitude": 16.2511,
    "timezone": "Europe/Vienna"
  },
  "current": {
    "timestamp": 1735689600,
    "temperature": 5.2,
    "feels_like": 2.1,
    "humidity": 72,
    "wind_speed": 3.5,
    "wind_deg": 240,
    "pressure": 1015,
    "visibility": 10000,
    "clouds": 45,
    "weather": {
      "id": 801,
      "main": "Clouds",
      "description": "scattered clouds",
      "icon": "03d"
    }
  }
}
```

### Forecast Response Format

```json
{
  "location": { /* Same as above */ },
  "current": { /* Same as above */ },
  "daily": [
    {
      "dt": 1735689600,
      "temp": {
        "day": 8.2,
        "min": 4.1,
        "max": 10.5,
        "night": 3.8,
        "eve": 6.2,
        "morn": 4.1
      },
      "feels_like": {
        "day": 5.2,
        "night": 1.2,
        "eve": 3.2,
        "morn": 1.5
      },
      "wind_speed": 4.2,
      "humidity": 65,
      "rain": 2.5,
      "weather": {
        "id": 500,
        "main": "Rain",
        "description": "light rain",
        "icon": "10d"
      }
    }
    /* ... 7 more days ... */
  ],
  "hourly": [
    {
      "dt": 1735689600,
      "temperature": 5.2,
      "feels_like": 2.1,
      "humidity": 72,
      "wind_speed": 3.5,
      "weather": {
        "id": 801,
        "main": "Clouds",
        "description": "scattered clouds",
        "icon": "03d"
      }
    }
    /* ... 47 more hours ... */
  ]
}
```

## Error Handling

### Validation Layer
- **Coordinate Validation**: Latitude (-90 to 90), Longitude (-180 to 180)
- **Location Validation**: Geocoding API returns error if location not found
- **API Key Validation**: 401 error if API key invalid

### Safe Data Access
```python
# OLD (causes IndexError):
weather_description = day.get('weather', [{}])[0].get('description')

# NEW (safe):
weather = day.get('weather', [{}])[0] if day.get('weather') else {}
description = weather.get('description', 'N/A')
```

### Exception Handling
- `ValueError`: Invalid coordinates or location not found
- `requests.exceptions.HTTPError`: API errors (401, 404, 500)
- `requests.exceptions.RequestException`: Network/timeout errors
- All errors logged with `logger.error()` for debugging

## API Optimization

### Current Weather Request
- **Exclude Parameters**: `exclude=hourly,daily,minutely,alerts`
- **Benefits**: Faster response, smaller payload, lower API quota usage
- **Use Case**: When only current conditions needed

### Forecast Request
- **Full API**: No exclude parameters
- **Benefits**: Complete data for multi-day planning
- **Use Case**: "What will the weather be like tomorrow?"

## Deployment Architecture

### Development
- **Server Type**: `stdio_server` (MCP standard)
- **Transport**: stdin/stdout pipes
- **Configuration**: `.env` file in project root
- **Logging**: Console output (level: INFO)

### Production (GCP)
- **Deployment**: Cloud Run or App Engine
- **Configuration**: Environment variables from Secret Manager
- **Scaling**: Automatic (per MCP protocol - stateless)
- **Monitoring**: Cloud Logging integration

## Performance Characteristics

| Operation | API Calls | Time (approx) | Data Size |
|-----------|-----------|---------------|-----------|
| get_current_weather | 2 (geocode + weather) | 500-800ms | 2-3 KB |
| get_forecast | 2 (geocode + forecast) | 600-1000ms | 15-25 KB |
| Direct coordinates | 1 (weather/forecast) | 300-500ms | 2-3 KB (current), 15-25 KB (forecast) |

## Security Considerations

1. **API Key**: Stored in `.env`, never committed to Git
2. **Input Validation**: All coordinates and locations validated
3. **Error Messages**: Generic messages to users, detailed logs for debugging
4. **Rate Limiting**: OpenWeatherMap API has rate limits (depends on plan)
5. **HTTPS**: All API calls to OpenWeatherMap use HTTPS

## Future Extensions

1. **Air Quality Data**: OpenWeatherMap Air Pollution API
2. **Alerts**: Weather alerts and warnings
3. **Historical Data**: Past weather records
4. **Geospatial**: Weather alerts for geographic regions
5. **Caching**: Redis cache for recent location queries
