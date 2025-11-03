#!/bin/bash
# Setup script for Weather MCP Server

set -e

echo "Setting up Weather MCP Server..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your OpenWeatherMap API key!"
    echo "   Get your API key from: https://openweathermap.org/api"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Edit .env and add your OpenWeatherMap API key"
echo "  3. Run: python main.py"
echo ""
echo "The server will be available at http://localhost:8000"
echo "API documentation will be at http://localhost:8000/docs"
