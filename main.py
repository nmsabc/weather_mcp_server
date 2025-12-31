"""
Main entry point for the Weather MCP Server application.
Provides command-line interface for running server and client.
"""

import argparse
import sys

from mcp_server import run_server
from mcp_client import run_client, run_forecast_client


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Weather MCP Server - A weather data microservice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the server
  python main.py server
  
  # Run the server on a specific host and port
  python main.py server --host 0.0.0.0 --port 8080
  
  # Run the client to fetch current weather data
  python main.py client --lat 33.44 --lon -94.04
  
  # Run the client to fetch forecast data (hourly + daily)
  python main.py forecast --lat 33.44 --lon -94.04
  
  # Run the client connecting to a specific server
  python main.py client --lat 33.44 --lon -94.04 --host localhost --port 8080

Environment Variables:
  OPENWEATHER_API_KEY  - Your OpenWeatherMap API key (required)
  MCP_SERVER_HOST      - Server host (default: 0.0.0.0 for server, localhost for client)
  MCP_SERVER_PORT      - Server port (default: 8000)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the MCP server")
    server_parser.add_argument(
        "--host",
        type=str,
        help="Host address to bind to (default: MCP_SERVER_HOST env or 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port",
        type=int,
        help="Port to listen on (default: MCP_SERVER_PORT env or 8000)"
    )
    
    # Client command
    client_parser = subparsers.add_parser("client", help="Run the MCP client for current weather")
    client_parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Latitude coordinate (-90 to 90)"
    )
    client_parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="Longitude coordinate (-180 to 180)"
    )
    client_parser.add_argument(
        "--host",
        type=str,
        help="Server host to connect to (default: MCP_SERVER_HOST env or localhost)"
    )
    client_parser.add_argument(
        "--port",
        type=int,
        help="Server port to connect to (default: MCP_SERVER_PORT env or 8000)"
    )
    
    # Forecast command
    forecast_parser = subparsers.add_parser("forecast", help="Run the MCP client for weather forecast")
    forecast_parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Latitude coordinate (-90 to 90)"
    )
    forecast_parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="Longitude coordinate (-180 to 180)"
    )
    forecast_parser.add_argument(
        "--host",
        type=str,
        help="Server host to connect to (default: MCP_SERVER_HOST env or localhost)"
    )
    forecast_parser.add_argument(
        "--port",
        type=int,
        help="Server port to connect to (default: MCP_SERVER_PORT env or 8000)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "server":
        run_server(host=args.host, port=args.port)
        return 0
    elif args.command == "client":
        return run_client(
            latitude=args.lat,
            longitude=args.lon,
            host=args.host,
            port=args.port
        )
    elif args.command == "forecast":
        return run_forecast_client(
            latitude=args.lat,
            longitude=args.lon,
            host=args.host,
            port=args.port
        )
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
