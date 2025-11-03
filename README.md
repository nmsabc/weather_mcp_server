# Weather MCP Server

A Python weather microservice with an MCP wrapper. It fetches OpenWeatherMap One Call API data (current weather for lat/lon) via a FastAPI server, usable by a separate client or LLM. Configurable for local or GCP deployment, enabling flexible access to weather info.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Add your OpenWeatherMap API key to .env
```

3. Run the server:
```bash
python main.py
```

4. Access the API at `http://localhost:8000`

## Features

- 🌤️ Current weather data via OpenWeatherMap One Call API
- 🚀 FastAPI REST API server
- 🤖 MCP wrapper for LLM integration
- 🔧 Local and GCP deployment support
- 📊 Comprehensive error handling
- 🌍 Multiple unit systems and languages

## API Usage

Get weather for coordinates:
```bash
curl "http://localhost:8000/weather?latitude=40.7128&longitude=-74.0060&units=metric"
```

See [DOCS.md](DOCS.md) for complete documentation.

## Deployment

- **Local**: `python main.py`
- **Docker**: `docker build -t weather-mcp-server . && docker run -p 8000:8000 --env-file .env weather-mcp-server`
- **GCP**: `gcloud app deploy`

## Documentation

- Full documentation: [DOCS.md](DOCS.md)
- API docs: `http://localhost:8000/docs` (when running)

