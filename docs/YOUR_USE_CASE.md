# Weather MCP Server - Your Use Case Architecture

## Your Multi-Server Setup

Based on your requirements, here's how the Weather MCP Server fits into your multi-server MCP setup:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP CLI Application                       │
│                  (Main Orchestrator)                         │
│                                                              │
│  Launches all servers simultaneously via subprocess          │
└──────┬────────────────────┬────────────────────┬───────────┘
       │                    │                    │
       │ stdin/stdout       │ stdin/stdout       │ stdin/stdout
       │ JSON-RPC           │ JSON-RPC           │ JSON-RPC
       │                    │                    │
┌──────▼──────────┐  ┌─────▼──────────┐  ┌─────▼──────────┐
│ Weather Server  │  │  Main Server    │  │ Web Search     │
│                 │  │                 │  │ Server         │
│ /Users/seba/    │  │  mcp_server/    │  │ mcp_server/    │
│ GCP/weather_    │  │  mcp_server_    │  │ web_search_    │
│ mcp_server/     │  │  main.py        │  │ server_main.py │
│ mcp_server.py   │  │                 │  │                │
│                 │  │                 │  │                │
│ ┌─────────────┐ │  │                 │  │                │
│ │  Uvicorn    │ │  │                 │  │                │
│ │  (daemon    │ │  │                 │  │                │
│ │   thread)   │ │  │                 │  │                │
│ │  :8000      │ │  │                 │  │                │
│ └──────┬──────┘ │  │                 │  │                │
│        │        │  │                 │  │                │
│   Internal HTTP │  │                 │  │                │
│        ▼        │  │                 │  │                │
│  OpenWeatherMap│  │                 │  │                │
│    One Call    │  │                 │  │                │
│    API v3      │  │                 │  │                │
└────────────────┘  └─────────────────┘  └────────────────┘
```

## Your Configuration Files

### MCP Configuration (mcp_config.json or similar)

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "/Users/seba/GCP/weather_mcp_server/mcp_server.py"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "your_actual_api_key_here",
        "MCP_MODE": "stdio",
        "MCP_SERVER_PORT": "8000"
      }
    },
    "main": {
      "command": "python",
      "args": [
        "/Users/seba/GCP/mcp_server/mcp_server_main.py"
      ]
    },
    "web_search": {
      "command": "python",
      "args": [
        "/Users/seba/GCP/mcp_server/web_search_server_main.py"
      ]
    }
  }
}
```

### Alternative: Using main.py Entry Point

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "/Users/seba/GCP/weather_mcp_server/main.py",
        "server",
        "--mcp"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

## How It Works in Your Setup

### 1. Startup Sequence

```
MCP CLI starts
    │
    ├─> Launches weather server subprocess
    │   └─> Weather server:
    │       1. Starts Uvicorn in background thread (non-blocking)
    │       2. Waits 2 seconds for HTTP server to be ready
    │       3. Starts reading from stdin for MCP messages
    │       4. Returns control immediately (doesn't block)
    │
    ├─> Launches main server subprocess (non-blocking)
    │
    └─> Launches web search server subprocess (non-blocking)

All servers running simultaneously ✓
```

### 2. Message Flow Example

**User asks LLM:** "What's the weather in New York?"

```
1. LLM/MCP CLI
   │
   │ {"jsonrpc":"2.0","id":1,"method":"tools/call",
   │  "params":{"name":"get_weather",
   │            "arguments":{"latitude":40.7128,"longitude":-74.0060}}}
   │
   └─> stdin to Weather Server

2. Weather Server (main thread)
   │
   ├─> Parse JSON-RPC message
   │
   ├─> Call internal HTTP: GET http://127.0.0.1:8000/weather?lat=40.7128&lon=-74.0060
   │
   ├─> HTTP Backend (thread): Call OpenWeatherMap API
   │
   ├─> Get weather data
   │
   └─> Format and return JSON-RPC response via stdout

3. MCP CLI receives response
   │
   └─> LLM processes and responds to user
```

### 3. Key Differences from Old Implementation

**Before (Blocking - BROKEN):**
```python
def run_server(host, port):
    uvicorn.run(app, host=host, port=port)  # ← BLOCKS HERE
    # Never returns, other servers can't start
```

**After (Non-Blocking - FIXED):**
```python
def run_mcp_stdio_server(host, port):
    # Start HTTP in background
    thread = threading.Thread(target=run_uvicorn, daemon=True)
    thread.start()  # ← Doesn't block!
    
    # Main thread handles stdio
    while True:
        line = sys.stdin.readline()  # ← MCP communication
        # Process and respond
```

## Testing Your Setup

### Test 1: Verify Non-Blocking Behavior

```bash
# This should NOT hang - server should start and wait for input
export OPENWEATHER_API_KEY="your_key"
python /Users/seba/GCP/weather_mcp_server/main.py server --mcp

# If it shows "MCP stdio interface ready" and waits, it's working!
# Press Ctrl+C to exit
```

### Test 2: Send MCP Message

```bash
export OPENWEATHER_API_KEY="your_key"
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python /Users/seba/GCP/weather_mcp_server/main.py server --mcp
```

Expected output:
```json
{"jsonrpc":"2.0","id":1,"result":{"tools":[{"name":"get_weather",...},{"name":"get_forecast",...}]}}
```

### Test 3: Multi-Server Launch

Create test script `/tmp/test_multi_server.sh`:

```bash
#!/bin/bash

export OPENWEATHER_API_KEY="your_key"

# Launch weather server in background
python /Users/seba/GCP/weather_mcp_server/main.py server --mcp &
WEATHER_PID=$!

sleep 1

# Check if still running (should be waiting for stdin, not blocked)
if ps -p $WEATHER_PID > /dev/null; then
    echo "✓ Weather server started successfully (non-blocking)"
else
    echo "✗ Weather server exited (something wrong)"
fi

# Clean up
kill $WEATHER_PID 2>/dev/null
```

## Directory Structure (Your Setup)

```
/Users/seba/GCP/
├── weather_mcp_server/           # ← Your weather server
│   ├── mcp_server.py             # Main server file (MCP-enabled)
│   ├── main.py                   # CLI entry point
│   ├── weather_api.py            # OpenWeatherMap integration
│   ├── mcp_client.py             # HTTP client
│   ├── requirements.txt
│   └── docs/
│       ├── MCP_ARCHITECTURE.md   # Architecture details
│       ├── USAGE_GUIDE.md        # Complete usage guide
│       └── extend_to_5_endpoints/
│           └── mcp_fix_plan.md   # Implementation plan
│
└── mcp_server/                   # Your main MCP setup
    ├── mcp_server_main.py        # Main server
    ├── web_search_server_main.py # Web search server
    └── weather_server_main.py    # Wrapper that calls weather_mcp_server
```

## Integration Points

### If weather_server_main.py exists

Update it to use MCP mode:

```python
# /Users/seba/GCP/mcp_server/weather_server_main.py

import sys
import os

# Add weather server to path
sys.path.insert(0, '/Users/seba/GCP/weather_mcp_server')

from mcp_server import run_mcp_stdio_server

if __name__ == "__main__":
    # Run in MCP stdio mode
    run_mcp_stdio_server()
```

### Or Direct Invocation

Just call the weather server directly from your MCP config:

```json
"weather": {
  "command": "python",
  "args": ["/Users/seba/GCP/weather_mcp_server/mcp_server.py"],
  "env": {
    "OPENWEATHER_API_KEY": "your_key",
    "MCP_MODE": "stdio"
  }
}
```

## Troubleshooting Your Setup

### Issue: Weather server still blocks other servers

**Check:**
1. Are you using `--mcp` flag or `MCP_MODE=stdio`?
2. Is `run_mcp_stdio_server()` being called (not `run_server()`)?

**Fix:**
```bash
# Make sure you're using one of these:
python main.py server --mcp
# OR
export MCP_MODE=stdio && python mcp_server.py
```

### Issue: HTTP backend not starting

**Check logs:**
```bash
python main.py server --mcp 2>&1 | tee weather_server.log
```

Look for: "Weather MCP Server HTTP backend started on 127.0.0.1:8000"

### Issue: Port conflict (8000 already in use)

**Change port:**
```bash
export MCP_SERVER_PORT=8001
python main.py server --mcp
```

## Summary

✅ **Problem Solved:** Weather server no longer blocks - runs in daemon thread
✅ **MCP Compatible:** Communicates via stdin/stdout JSON-RPC
✅ **Multi-Server Ready:** Can run alongside main and web_search servers
✅ **Backwards Compatible:** HTTP mode still works for standalone use
✅ **Well Documented:** Complete architecture and usage guides included

Your weather MCP server is now ready for production multi-server setups! 🚀
