# Weather MCP Server

A Python weather microservice with a Model Context Protocol (MCP) wrapper. It fetches current weather data from the OpenWeatherMap One Call API (version 3) via a FastAPI server, accessible by a separate client or LLM applications.

## Features

- **OpenWeatherMap Integration**: Fetches current weather data and forecasts using One Call API v3
- **FastAPI Server**: RESTful API endpoints for weather data retrieval
- **Python Client**: Simple client for interacting with the server
- **Forecast Support**: Get hourly (48h) and daily (8d) weather forecasts
- **Configurable**: Environment variable-based configuration for flexibility
- **Modular Design**: Clear separation of concerns with dedicated modules
- **Deployment Ready**: Structured for easy deployment to cloud platforms like GCP

## Project Structure

```
weather_mcp_server/
├── main.py           # Main entry point with CLI
├── weather_api.py    # OpenWeatherMap API integration
├── mcp_server.py     # FastAPI server implementation
├── mcp_client.py     # Client implementation
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Prerequisites

- Python 3.8 or higher
- OpenWeatherMap API key (see setup instructions below)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nmsabc/weather_mcp_server.git
cd weather_mcp_server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Obtain an OpenWeatherMap API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/)
2. Sign up for a free account
3. Navigate to "API Keys" in your account settings
4. Generate a new API key
5. Note: You'll need to subscribe to the "One Call API 3.0" (free tier available with 1,000 calls/day)

### 4. Configure Environment Variables

Set the required environment variables:

```bash
# Required: Your OpenWeatherMap API key
export OPENWEATHER_API_KEY="your_api_key_here"

# Optional: Server configuration (defaults shown)
export MCP_SERVER_HOST="0.0.0.0"  # Use "0.0.0.0" for server, "localhost" for client
export MCP_SERVER_PORT="8000"
```

For Windows (PowerShell):
```powershell
$env:OPENWEATHER_API_KEY="your_api_key_here"
$env:MCP_SERVER_HOST="0.0.0.0"
$env:MCP_SERVER_PORT="8000"
```

## Quick Start

The weather service uses a client-server architecture. You need to start the server first, then use the client.

**Terminal 1 - Start the Server:**
```bash
export OPENWEATHER_API_KEY="your_api_key_here"
python main.py server
```

**Terminal 2 - Use the Client:**
```bash
# Get current weather
python main.py client --lat 40.7128 --lon -74.0060

# Get weather forecast (hourly + daily)
python main.py forecast --lat 40.7128 --lon -74.0060
```

**Alternative - Direct API Access:**
```bash
curl "http://localhost:8000/weather?lat=40.7128&lon=-74.0060"
curl "http://localhost:8000/forecast?lat=40.7128&lon=-74.0060"
```

## Usage

### Running the Server

Start the MCP server:

```bash
python main.py server
```

With custom host and port:

```bash
python main.py server --host 0.0.0.0 --port 8080
```

The server will start and listen for requests at `http://<host>:<port>`.

### Running the Client

**Important:** The server must be running before you can use the client.

In a separate terminal, run the client to fetch current weather data:

```bash
python main.py client --lat 33.44 --lon -94.04
```

To fetch forecast data (hourly and daily):

```bash
python main.py forecast --lat 33.44 --lon -94.04
```

Connect to a server on a different host/port:

```bash
python main.py client --lat 33.44 --lon -94.04 --host localhost --port 8080
python main.py forecast --lat 33.44 --lon -94.04 --host localhost --port 8080
```

### Example Locations

Here are some coordinates you can try:

- New York, NY: `--lat 40.7128 --lon -74.0060`
- London, UK: `--lat 51.5074 --lon -0.1278`
- Tokyo, Japan: `--lat 35.6762 --lon 139.6503`
- Sydney, Australia: `--lat -33.8688 --lon 151.2093`

### API Endpoints

When the server is running, you can also access it directly:

#### Root Endpoint
```bash
curl http://localhost:8000/
```

#### Weather Endpoint (Current Weather Only)
```bash
curl "http://localhost:8000/weather?lat=33.44&lon=-94.04"
```

Response format:
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

#### Forecast Endpoint (Current + Hourly + Daily)
```bash
curl "http://localhost:8000/forecast?lat=33.44&lon=-94.04"
```

Response format:
```json
{
  "status": "success",
  "data": {
    "current": {
      "temperature": 20.5,
      "feels_like": 19.8,
      "humidity": 65,
      "weather": "clear sky",
      "...": "..."
    },
    "hourly": [
      {
        "dt": 1234567890,
        "temp": 21.0,
        "humidity": 60,
        "weather": "clear sky",
        "pop": 0.1
      }
    ],
    "daily": [
      {
        "dt": 1234567890,
        "temp_min": 15.0,
        "temp_max": 25.0,
        "temp_day": 22.0,
        "temp_night": 17.0,
        "weather": "partly cloudy",
        "pop": 0.2
      }
    ],
    "timezone": "America/Chicago"
  }
}
```

## Deployment to Google Cloud Platform (GCP)

### Option 1: Docker Deployment

1. Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

CMD ["python", "main.py", "server"]
```

2. Build and deploy:

```bash
# Build the Docker image
docker build -t weather-mcp-server .

# Run locally
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key weather-mcp-server

# Deploy to Google Cloud Run
gcloud run deploy weather-mcp-server \
  --image gcr.io/your-project/weather-mcp-server \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENWEATHER_API_KEY=your_key
```

### Option 2: Google App Engine

1. Create an `app.yaml`:

```yaml
runtime: python311

env_variables:
  OPENWEATHER_API_KEY: "your_api_key_here"

entrypoint: python main.py server
```

2. Deploy:

```bash
gcloud app deploy
```

### Security Note for Production

**Never commit API keys to version control!** Use:
- GCP Secret Manager for storing API keys
- Environment variables set during deployment
- Cloud-based configuration management

## Error Handling

The application includes error handling for:
- Missing or invalid API keys
- Invalid coordinate ranges (lat: -90 to 90, lon: -180 to 180)
- Network failures and timeouts
- API rate limiting and errors

## Development

### Running Tests

(Add tests as needed for your use case)

```bash
# Example with pytest
pip install pytest
pytest
```

### Code Style

The code follows PEP 8 guidelines. Format with:

```bash
pip install black
black *.py
```

## API Rate Limits

OpenWeatherMap free tier includes:
- 1,000 API calls per day
- 60 calls per minute

Monitor your usage in the OpenWeatherMap dashboard.

## Troubleshooting

### "API key not provided" Error
- Ensure `OPENWEATHER_API_KEY` is set in your environment
- Verify the API key is valid in your OpenWeatherMap account

### Connection Refused
- Ensure the server is running before starting the client
- Check that the host and port match between server and client
- Verify firewall rules allow traffic on the specified port

### API Errors
- Verify your API key has access to One Call API 3.0
- Check you haven't exceeded rate limits
- Ensure coordinates are valid (lat: -90 to 90, lon: -180 to 180)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
- Open an issue on GitHub
- Check OpenWeatherMap documentation: https://openweathermap.org/api/one-call-3
