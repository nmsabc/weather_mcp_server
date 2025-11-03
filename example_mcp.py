#!/usr/bin/env python3
"""
Example usage of the MCP wrapper for LLM integration.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_wrapper import MCPWeatherWrapper


def main():
    """Demonstrate MCP wrapper usage."""
    print("Weather MCP Wrapper Example")
    print("="*50)
    
    # Initialize MCP wrapper
    mcp = MCPWeatherWrapper()
    
    # Show available tools
    print("\nAvailable Tools:")
    tools = mcp.get_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Execute tool
    print("\nExecuting 'get_current_weather' tool...")
    print("Coordinates: New York City (40.7128, -74.0060)")
    
    result = mcp.execute_tool("get_current_weather", {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "units": "metric"
    })
    
    # Create LLM-friendly response
    llm_response = mcp.create_llm_response(result)
    
    print("\n" + "="*50)
    print("LLM Response:")
    print("="*50)
    print(llm_response)
    print("="*50)


if __name__ == "__main__":
    main()
