# Weather MCP Server Architecture

## Overview

The Weather MCP Server now supports two modes of operation:

1. **HTTP Mode (Standalone)**: Traditional server-client architecture with blocking Uvicorn
2. **MCP Stdio Mode (Multi-Server)**: Non-blocking server with JSON-RPC over stdin/stdout for MCP protocol

## Architecture Diagrams

### Mode 1: HTTP Mode (Standalone)

```
┌─────────────────┐
│   Terminal 1    │
│                 │
│  python main.py │
│     server      │
│                 │
│  ┌───────────┐  │
│  │ Uvicorn   │  │
│  │ (blocking)│  │
│  │ :8000     │  │
│  └───────────┘  │
└────────┬────────┘
         │ HTTP
         │
┌────────▼────────┐
│   Terminal 2    │
│                 │
│  python main.py │
│    client       │
│                 │
│  OR curl        │
│  localhost:8000 │
└─────────────────┘
```

### Mode 2: MCP Stdio Mode (Multi-Server)

```
┌──────────────────────────────────────────────────────┐
│             MCP CLI / Main Application                │
│                                                       │
│  Launches multiple servers via subprocess             │
└────┬─────────────────┬─────────────────┬────────────┘
     │                 │                 │
     │ stdin/stdout    │ stdin/stdout    │ stdin/stdout
     │ JSON-RPC        │ JSON-RPC        │ JSON-RPC
     │                 │                 │
┌────▼────────┐  ┌────▼────────┐  ┌────▼────────┐
│  Weather    │  │   Main      │  │  Web Search │
│  Server     │  │   Server    │  │  Server     │
│             │  │             │  │             │
│ ┌─────────┐ │  │             │  │             │
│ │Uvicorn  │ │  │             │  │             │
│ │(thread) │ │  │             │  │             │
│ │:8000    │ │  │             │  │             │
│ └────┬────┘ │  │             │  │             │
│      │      │  │             │  │             │
│   Internal  │  │             │  │             │
│   HTTP Calls│  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Component Details

### MCP Server Components

```
┌────────────────────────────────────────────────────────┐
│                   mcp_server.py                        │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │         FastAPI Application (app)             │    │
│  │                                               │    │
│  │  Endpoints:                                   │    │
│  │  - GET /        (service info)                │    │
│  │  - GET /weather (current weather)             │    │
│  │  - GET /forecast (hourly + daily forecast)    │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │      run_server() - HTTP Mode                 │    │
│  │                                               │    │
│  │  uvicorn.run(app) - BLOCKING                  │    │
│  │  Used for: standalone HTTP server             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │   run_mcp_stdio_server() - MCP Mode           │    │
│  │                                               │    │
│  │  1. Start Uvicorn in daemon thread            │    │
│  │     (non-blocking, background HTTP server)    │    │
│  │                                               │    │
│  │  2. Main thread handles stdin/stdout          │    │
│  │     - Read JSON-RPC from stdin                │    │
│  │     - Call internal HTTP endpoints            │    │
│  │     - Write JSON-RPC to stdout                │    │
│  │                                               │    │
│  │  MCP Tools:                                   │    │
│  │  - get_weather (lat, lon)                     │    │
│  │  - get_forecast (lat, lon)                    │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

## Message Flow: MCP Mode

### Initialize Sequence
```
MCP CLI                    Weather Server
   │                            │
   │──── initialize ────────────>│
   │                            │
   │<─── capabilities ──────────│
   │     (tools: get_weather,   │
   │      get_forecast)         │
   │                            │
```

### Tool Call Sequence
```
MCP CLI                    Weather Server                  HTTP Backend
   │                            │                                │
   │─── tools/call ─────────────>│                                │
   │    (get_weather,            │                                │
   │     lat=33.44, lon=-94.04)  │                                │
   │                            │                                │
   │                            │─── GET /weather?lat=33.44&... ─>│
   │                            │                                │
   │                            │<─── HTTP 200 + weather data ───│
   │                            │                                │
   │<─── result ────────────────│                                │
   │     (formatted weather)     │                                │
```

## Usage Examples

### Standalone HTTP Mode
```bash
# Terminal 1 - Server
export OPENWEATHER_API_KEY="your_key"
python main.py server

# Terminal 2 - Client
python main.py client --lat 33.44 --lon -94.04
# OR
curl "http://localhost:8000/weather?lat=33.44&lon=-94.04"
```

### MCP Stdio Mode
```bash
# Option 1: Using --mcp flag
export OPENWEATHER_API_KEY="your_key"
python main.py server --mcp

# Option 2: Using environment variable
export MCP_MODE=stdio
python mcp_server.py

# Server reads JSON-RPC from stdin, writes to stdout
# Example input:
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_weather","arguments":{"latitude":33.44,"longitude":-94.04}}}

# Example output:
{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"...weather data..."}]}}
```

### MCP Multi-Server Configuration

In your MCP configuration file (e.g., `mcp_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/weather_mcp_server/mcp_server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_key_here",
        "MCP_MODE": "stdio",
        "MCP_SERVER_PORT": "8000"
      }
    },
    "main": {
      "command": "python",
      "args": ["/path/to/mcp_server/mcp_server_main.py"]
    },
    "web_search": {
      "command": "python",
      "args": ["/path/to/mcp_server/web_search_server_main.py"]
    }
  }
}
```

## Key Differences

| Feature | HTTP Mode | MCP Stdio Mode |
|---------|-----------|----------------|
| **Blocking** | Yes (uvicorn.run blocks) | No (uvicorn in thread) |
| **Communication** | HTTP requests | JSON-RPC via stdin/stdout |
| **Use Case** | Standalone server | Multi-server MCP setups |
| **Launch** | `python main.py server` | `python main.py server --mcp` |
| **Client** | HTTP client / curl | MCP CLI / tools |
| **Port** | Listens on 0.0.0.0:8000 | Listens on 127.0.0.1:8000 |

## Benefits of MCP Mode

1. **Non-Blocking**: Allows multiple MCP servers to run simultaneously
2. **Standard Protocol**: Uses JSON-RPC 2.0 over stdin/stdout
3. **Composable**: Works with other MCP servers in the same application
4. **Internal HTTP**: Still uses FastAPI/Uvicorn internally for logic
5. **Backwards Compatible**: HTTP mode still available for standalone use

## Implementation Notes

- HTTP backend runs in daemon thread (auto-cleanup on exit)
- 2-second startup delay ensures HTTP server is ready
- Error handling for malformed JSON-RPC messages
- Graceful shutdown on stdin EOF or SIGINT
- Logging to stderr (stdout reserved for JSON-RPC)
