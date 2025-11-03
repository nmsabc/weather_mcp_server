# Weather MCP Server

A Python weather microservice with an MCP (Model Context Protocol) wrapper. It fetches OpenWeatherMap One Call API data (current weather for lat/lon) via a FastAPI server, usable by a separate client or LLM. Configurable for local or GCP deployment, enabling flexible access to weather info.

## Features

- 🌤️ Fetch current weather data using latitude/longitude coordinates
- 🚀 FastAPI server with RESTful API endpoints
- 🤖 MCP wrapper for LLM integration
- 🔧 Configurable for local or GCP deployment
- 📊 Comprehensive error handling and logging
- 🌍 Support for multiple unit systems (metric, imperial, standard)
- 🗣️ Multi-language support for weather descriptions

## Prerequisites

- Python 3.11+
- OpenWeatherMap API key ([Get one here](https://openweathermap.org/api))
- For GCP deployment: Google Cloud Platform account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nmsabc/weather_mcp_server.git
cd weather_mcp_server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

## Configuration

Edit the `.env` file with your configuration:

```env
# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/3.0/onecall

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Deployment Configuration
ENVIRONMENT=local  # local or gcp

# GCP Configuration (optional, for GCP deployment)
GCP_PROJECT_ID=your_project_id
GCP_REGION=us-central1
```

## Usage

### Running Locally

Start the server:
```bash
python main.py
```

The server will be available at `http://localhost:8000`

### API Endpoints

#### Root Endpoint
```bash
GET /
```
Returns API information and available endpoints.

#### Health Check
```bash
GET /health
```
Returns server health status.

#### Get Weather (GET)
```bash
GET /weather?latitude=40.7128&longitude=-74.0060&units=metric
```

Parameters:
- `latitude` (required): Latitude coordinate (-90 to 90)
- `longitude` (required): Longitude coordinate (-180 to 180)
- `units` (optional): Unit system - `metric`, `imperial`, or `standard` (default: `metric`)
- `lang` (optional): Language code (default: `en`)
- `formatted` (optional): Return formatted response (default: `true`)

Example response:
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

#### Get Weather (POST)
```bash
POST /weather
Content-Type: application/json

{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "lang": "en"
}
```

### Using with cURL

```bash
# Get weather for New York City
curl "http://localhost:8000/weather?latitude=40.7128&longitude=-74.0060&units=metric"

# POST request
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "units": "metric"}'
```

### MCP Wrapper for LLM Integration

The MCP wrapper allows LLMs to interact with the weather service:

```python
from src.mcp_wrapper import MCPWeatherWrapper

# Initialize wrapper
mcp = MCPWeatherWrapper()

# Get available tools
tools = mcp.get_tools()

# Execute tool
result = mcp.execute_tool("get_current_weather", {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "units": "metric"
})

# Create natural language response
response = mcp.create_llm_response(result)
print(response)
```

## Deployment

### Local Deployment

Simply run:
```bash
python main.py
```

### Docker Deployment

Build and run with Docker:
```bash
docker build -t weather-mcp-server .
docker run -p 8000:8000 --env-file .env weather-mcp-server
```

### GCP App Engine Deployment

1. Install Google Cloud SDK
2. Configure your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

3. Update `app.yaml` if needed
4. Deploy:
```bash
gcloud app deploy
```

5. Set environment variables in GCP Console:
   - Navigate to App Engine > Settings > Environment variables
   - Add `OPENWEATHER_API_KEY` and other required variables

## Project Structure

```
weather_mcp_server/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── server.py           # FastAPI server
│   ├── weather_service.py  # OpenWeatherMap API integration
│   └── mcp_wrapper.py      # MCP wrapper for LLM integration
├── tests/                  # Test files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker configuration
├── app.yaml               # GCP App Engine configuration
└── README.md              # This file
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful request
- `400`: Bad request (invalid parameters)
- `401`: Invalid API key
- `404`: Location not found
- `500`: Internal server error

## Unit Systems

- **metric**: Temperature in Celsius, wind speed in m/s
- **imperial**: Temperature in Fahrenheit, wind speed in mph
- **standard**: Temperature in Kelvin, wind speed in m/s

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather data
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
