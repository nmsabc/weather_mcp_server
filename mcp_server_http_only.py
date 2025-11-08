#!/usr/bin/env python3
"""
HTTP MCP Server for Weather Service
"""

import asyncio
import logging
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.fastapi import FastAPIServer
import uvicorn

# Import your existing MCP server setup
from mcp_server import server, weather_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-http-server")


def create_app() -> FastAPI:
    """Create FastAPI app with MCP server."""
    fastapi_server = FastAPIServer(server)
    app = fastapi_server.get_app()

    @app.get("/")
    async def root():
        return {"message": "Weather MCP HTTP Server", "status": "running"}

    return app


async def main():
    """Run the HTTP MCP server."""
    logger.info("Starting Weather MCP HTTP Server on http://localhost:8001")

    app = create_app()
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()

if __name__ == "__main__":
    asyncio.run(main())
