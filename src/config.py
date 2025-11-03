import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with support for local and GCP deployment."""
    
    # OpenWeatherMap API Configuration
    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/3.0/onecall"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Deployment Configuration
    environment: str = "local"  # local or gcp
    
    # GCP Configuration (optional)
    gcp_project_id: Optional[str] = None
    gcp_region: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
