# Fix Weather MCP Server - Non-Blocking Stdio Interface Plan

## Problem Understood ✅

The current `mcp_server.py` implementation has a critical issue:
- Uses `uvicorn.run()` which is a **blocking call**
- When launched via subprocess (as MCP CLI does), it blocks the entire process
- Prevents other MCP servers from starting
- Never returns control to the caller
- Causes the application to hang in multi-server setups

### Current Flow (Broken)
```
MCP CLI → Launch weather server → uvicorn.run() BLOCKS → Other servers can't start → Hang
```

### Required Flow (Fixed)
```
MCP CLI → Launch weather server (background HTTP) → Read stdin for MCP messages → All servers work together
```

## Resolution Plan

### Core Changes Required

1. **Make Uvicorn Non-Blocking**
   - Run Uvicorn HTTP server in a background thread or async task
   - Free up main thread to handle stdin/stdout communication
   - Keep existing `/weather` and `/forecast` endpoints working

2. **Add Stdio-Based MCP Interface**
   - Read JSON-RPC messages from stdin
   - Write JSON responses to stdout
   - Bridge MCP tool calls to HTTP endpoints:
     - `get_weather` tool → calls `GET /weather?lat=X&lon=Y`
     - `get_forecast` tool → calls `GET /forecast?lat=X&lon=Y`

3. **Graceful Lifecycle Management**
   - Start: Launch HTTP server in background, then process stdin
   - Running: Handle stdin messages, route to endpoints
   - Shutdown: Clean up on EOF or signal

### Implementation Approach

**Option: Uvicorn in Background Thread (Simpler & Reliable)**
```python
import threading
import time
import sys
import json
import requests

# Start HTTP server in daemon thread
def run_uvicorn():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

server_thread = threading.Thread(target=run_uvicorn, daemon=True)
server_thread.start()
time.sleep(2)  # Give server time to start

# Main thread: Process stdin/stdout for MCP
while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    # Parse JSON-RPC message
    # Route to appropriate endpoint
    # Return response via stdout
```

## Files to Modify

1. **`mcp_server.py`** (Major changes)
   - Add MCP stdio interface
   - Run Uvicorn in background thread
   - Add JSON-RPC message handling
   - Map MCP tools to HTTP endpoints
   - Keep existing FastAPI app and endpoints unchanged

2. **`weather_api.py`** (No changes needed)
   - Keep as-is

3. **`main.py`** (Minor update)
   - Update server command to support MCP mode
   - Add flag for MCP vs standalone mode

4. **`README.md`** (Update documentation)
   - Document MCP mode usage
   - Explain stdio interface

## Testing Strategy

After implementation, verify:
1. ✅ Server starts without blocking
2. ✅ Accepts stdin input while HTTP server runs
3. ✅ Responds to MCP JSON-RPC tool calls
4. ✅ Multiple servers can launch together
5. ✅ HTTP endpoints still work (`curl http://localhost:8000/weather?lat=33.44&lon=-94.04`)
6. ✅ Clean shutdown on stdin EOF

## Key Points

- **Backwards compatible**: Existing HTTP endpoints and CLI commands still work
- **Non-blocking**: Main thread handles MCP communication, HTTP in background
- **Multi-server friendly**: Allows other MCP servers to run simultaneously
- **Standard MCP protocol**: Uses JSON-RPC over stdin/stdout

Ready to proceed with implementation? 🔧
