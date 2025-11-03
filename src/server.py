import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.weather_service import WeatherService
from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Weather MCP Server",
    description="A Python weather microservice with MCP wrapper. Fetches OpenWeatherMap One Call API data.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize weather service
weather_service = WeatherService()


class WeatherRequest(BaseModel):
    """Request model for weather data."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    units: str = Field("metric", description="Unit system: metric, imperial, or standard")
    lang: str = Field("en", description="Language code for weather descriptions")


class WeatherResponse(BaseModel):
    """Response model for weather data."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Weather MCP Server",
        "version": "1.0.0",
        "description": "Fetches current weather data from OpenWeatherMap One Call API",
        "environment": settings.environment,
        "endpoints": {
            "/weather": "GET - Fetch current weather for lat/lon coordinates",
            "/health": "GET - Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@app.get("/weather", response_model=WeatherResponse)
async def get_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    units: str = Query("metric", description="Unit system: metric, imperial, or standard"),
    lang: str = Query("en", description="Language code"),
    formatted: bool = Query(True, description="Return formatted response")
):
    """
    Fetch current weather data for given coordinates.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        units: Unit system (metric, imperial, or standard)
        lang: Language code for weather descriptions
        formatted: Whether to return formatted response
        
    Returns:
        Weather data from OpenWeatherMap One Call API
    """
    try:
        logger.info("Received weather request")
        
        # Fetch weather data
        raw_data = weather_service.get_current_weather(
            latitude=latitude,
            longitude=longitude,
            units=units,
            lang=lang
        )
        
        # Format response if requested
        data = weather_service.format_weather_response(raw_data) if formatted else raw_data
        
        return WeatherResponse(success=True, data=data)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing weather request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/weather", response_model=WeatherResponse)
async def post_weather(request: WeatherRequest):
    """
    Fetch current weather data for given coordinates (POST method).
    
    Args:
        request: Weather request with coordinates and options
        
    Returns:
        Weather data from OpenWeatherMap One Call API
    """
    try:
        logger.info("Received weather POST request")
        
        # Fetch weather data
        raw_data = weather_service.get_current_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            units=request.units,
            lang=request.lang
        )
        
        # Format response
        data = weather_service.format_weather_response(raw_data)
        
        return WeatherResponse(success=True, data=data)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing weather request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
