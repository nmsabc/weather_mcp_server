# API Specification

## Weather MCP Server API v1.0

### Base URL
```
http://localhost:8000
```

### Authentication
All requests require an OpenWeatherMap API key configured in the `.env` file. No authentication headers are needed for API requests.

---

## Endpoints

### 1. Root Endpoint

**GET /**

Returns API information and metadata.

**Response:**
```json
{
  "service": "Weather MCP Server",
  "version": "1.0.0",
  "description": "Fetches current weather data from OpenWeatherMap One Call API",
  "environment": "local",
  "endpoints": {
    "/weather": "GET - Fetch current weather for lat/lon coordinates",
    "/health": "GET - Health check endpoint"
  }
}
```

---

### 2. Health Check

**GET /health**

Check server health status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "local"
}
```

---

### 3. Get Weather (GET)

**GET /weather**

Fetch current weather data for coordinates.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| latitude | float | Yes | - | Latitude coordinate (-90 to 90) |
| longitude | float | Yes | - | Longitude coordinate (-180 to 180) |
| units | string | No | metric | Unit system: `metric`, `imperial`, or `standard` |
| lang | string | No | en | Language code for descriptions |
| formatted | boolean | No | true | Return formatted response |

**Example Request:**
```
GET /weather?latitude=40.7128&longitude=-74.0060&units=metric
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "location": {
      "latitude": 40.7128,
      "longitude": -74.006,
      "timezone": "America/New_York"
    },
    "current": {
      "timestamp": 1699036800,
      "temperature": 15.5,
      "feels_like": 14.8,
      "pressure": 1013,
      "humidity": 65,
      "dew_point": 10.2,
      "uvi": 3.5,
      "clouds": 20,
      "visibility": 10000,
      "wind_speed": 3.5,
      "wind_deg": 180,
      "weather": {
        "id": 801,
        "main": "Clouds",
        "description": "few clouds",
        "icon": "02d"
      }
    }
  }
}
```

**Error Response (400):**
```json
{
  "detail": "Invalid latitude: 95. Must be between -90 and 90."
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid API key"
}
```

**Error Response (500):**
```json
{
  "detail": "Internal server error"
}
```

---

### 4. Get Weather (POST)

**POST /weather**

Fetch current weather data for coordinates using POST method.

**Request Body:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "lang": "en"
}
```

**Response:**
Same as GET /weather

---

## Data Models

### WeatherRequest
```json
{
  "latitude": "float (-90 to 90)",
  "longitude": "float (-180 to 180)",
  "units": "string (metric|imperial|standard)",
  "lang": "string"
}
```

### WeatherResponse
```json
{
  "success": "boolean",
  "data": "object or null",
  "error": "string or null"
}
```

### Location Object
```json
{
  "latitude": "float",
  "longitude": "float",
  "timezone": "string"
}
```

### Current Weather Object
```json
{
  "timestamp": "integer (Unix timestamp)",
  "temperature": "float",
  "feels_like": "float",
  "pressure": "integer (hPa)",
  "humidity": "integer (%)",
  "dew_point": "float",
  "uvi": "float",
  "clouds": "integer (%)",
  "visibility": "integer (meters)",
  "wind_speed": "float",
  "wind_deg": "integer (degrees)",
  "weather": {
    "id": "integer",
    "main": "string",
    "description": "string",
    "icon": "string"
  }
}
```

---

## Unit Systems

### Metric (default)
- Temperature: Celsius
- Wind speed: meters/second
- Pressure: hPa

### Imperial
- Temperature: Fahrenheit
- Wind speed: miles/hour
- Pressure: hPa

### Standard
- Temperature: Kelvin
- Wind speed: meters/second
- Pressure: hPa

---

## Language Support

The API supports language codes for weather descriptions. Common codes:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `ja` - Japanese
- `zh_cn` - Chinese Simplified

Full list: https://openweathermap.org/api/one-call-api#multi

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (invalid API key) |
| 404 | Not Found (location not found) |
| 500 | Internal Server Error |

---

## Rate Limits

Rate limits depend on your OpenWeatherMap subscription plan:
- Free: 60 calls/minute, 1,000,000 calls/month
- Startup: 600 calls/minute, 3,000,000 calls/month
- Developer: 3,000 calls/minute, 100,000,000 calls/month

---

## Examples

### cURL Examples

**Basic request:**
```bash
curl "http://localhost:8000/weather?latitude=40.7128&longitude=-74.0060"
```

**With imperial units:**
```bash
curl "http://localhost:8000/weather?latitude=51.5074&longitude=-0.1278&units=imperial"
```

**POST request:**
```bash
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 35.6762,
    "longitude": 139.6503,
    "units": "metric",
    "lang": "ja"
  }'
```

### Python Examples

**Using requests:**
```python
import requests

response = requests.get(
    "http://localhost:8000/weather",
    params={
        "latitude": 40.7128,
        "longitude": -74.0060,
        "units": "metric"
    }
)

data = response.json()
print(data)
```

**Using the provided client:**
```python
from example_client import WeatherClient

client = WeatherClient()
weather = client.get_weather(40.7128, -74.0060, units="metric")
print(weather)
```

### JavaScript Example

```javascript
fetch('http://localhost:8000/weather?latitude=40.7128&longitude=-74.0060&units=metric')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```
