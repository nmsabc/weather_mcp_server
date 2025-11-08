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

4. run the server via http

```bash
python mcp_server_http.py --host 0.0.0.0 --port 8001
```

5. call the new server like this

```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_current_weather",
      "arguments": {"location": "Baden bei Wien"}
    },
    "id": 1
  }' | jq
```

6. call the mcp server from the chat-cli

```bash
cd /Users/seba/GCP/mcp_cli_model_agnostic
workon mcp_cli_model_agnostic
python3 -m mcp_cli.cli chat --mcp-server "python examples/mcp_server.py" --mcp-server "python examples/weather_http_bridge.py"
```

7. or access the API at `http://localhost:8000`

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
