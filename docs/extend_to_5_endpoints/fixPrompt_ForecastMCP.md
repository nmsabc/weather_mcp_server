# Fix Weather MCP Server - Non-Blocking Stdio Interface

## Problem
The `mcp_server.py` on the `copilot/add-weather-data-microservice` branch uses `uvicorn.run()` which is a **blocking call**. 

When launched via subprocess (as the MCP CLI does), it:
- Blocks the entire process indefinitely
- Never returns control to the caller
- Prevents subsequent MCP servers from starting
- Causes the entire application to hang

### Current Behavior
```
Start MCP CLI → Launch weather server → Server blocks → No other servers can start → App hangs
```

### Expected Behavior
```
Start MCP CLI → Launch weather server (background) → CLI can launch other servers → All work together
```

## Solution Requirements

The `mcp_server.py` must:

1. **Expose a stdio-based MCP interface** 
   - Accept JSON-RPC messages via stdin
   - Return responses via stdout
   - This allows the MCP CLI to communicate with the server

2. **Run HTTP backend non-blocking**
   - The Uvicorn HTTP server for `/weather` and `/forecast` endpoints should run in background
   - Use `subprocess` or `threading` to run Uvicorn without blocking main thread
   - OR: Run async/await with proper event loop handling

3. **Handle both interfaces**
   - Maintain the `/weather` and `/forecast` HTTP endpoints
   - Add a stdio/JSON-RPC interface that bridges to those endpoints
   - Accept tool calls via stdin and route them to HTTP endpoints

4. **Graceful lifecycle management**
   - Start: Initialize HTTP server in background, then read from stdin
   - Running: Process stdin messages, forward to HTTP endpoints
   - Shutdown: Clean up on EOF from stdin or signal

## Technical Context

The MCP (Model Context Protocol) CLI expects servers to:
- Read JSON-RPC formatted messages from stdin
- Write JSON responses to stdout
- Not block or wait indefinitely
- Exit cleanly when stdin closes

The weather server is part of a **multi-server setup** where:
- Main MCP server: `mcp_server/mcp_server_main.py`
- Weather server: `mcp_server/weather_server_main.py` (calls `/Users/seba/GCP/weather_mcp_server/mcp_server.py`)
- Web search server: `mcp_server/web_search_server_main.py`

All servers launch simultaneously and must not block each other.

## Implementation Options

### Option A: Uvicorn in Thread (Simpler)
```python
import threading
import uvicorn
from fastapi import FastAPI

app = FastAPI(...)

def run_uvicorn():
    """Run Uvicorn in background thread."""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    # Start HTTP server in background
    server_thread = threading.Thread(target=run_uvicorn, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    # Main thread: handle stdio/MCP messages
    # Read from stdin, convert to HTTP calls, write to stdout
```

### Option B: Pure Async with Uvicorn Server (Better)
```python
import asyncio
from uvicorn.server import Server
from uvicorn.config import Config

async def main():
    config = Config(app=app, host="127.0.0.1", port=8000)
    server = Server(config)
    
    # Run server in background task
    server_task = asyncio.create_task(server.serve())
    
    # Process stdin in main task
    # while True: read line, process, write response
    
    # Cleanup on exit
    server.should_exit = True
    await server_task
```

## Tasks

1. Modify `mcp_server.py` to run Uvicorn non-blocking
2. Add stdio-based MCP interface to process JSON-RPC messages
3. Map MCP tool calls to HTTP endpoints:
   - `get_weather` → `GET /weather?lat=X&lon=Y`
   - `get_forecast` → `GET /forecast?lat=X&lon=Y`
4. Test that:
   - Server starts and doesn't block
   - Can accept stdin messages while HTTP server runs
   - Tools are properly exposed via MCP
   - Gracefully exits when stdin closes

## Files to Modify
- `mcp_server.py` - Main entry point (make non-blocking + add stdio interface)
- `weather_api.py` - Keep as-is (used by HTTP endpoints)

## Testing
After implementation, the server should:
1. Start without blocking
2. Accept stdin input while running
3. Respond to JSON-RPC messages
4. Allow multiple servers to launch together
5. Clean shutdown on stdin EOF
