"""Weather MCP Server - Main entry point."""

import uvicorn
from src.config import settings


def main():
    """Start the FastAPI server."""
    uvicorn.run(
        "src.server:app",
        host=settings.host,
        port=settings.port,
        reload=True if settings.environment == "local" else False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
