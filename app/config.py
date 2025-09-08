"""
Configuration settings for the Vancouver Route Recommendation System.
Handles environment variables and API configurations.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    translink_api_key: str = os.getenv("TRANSLINK_API_KEY", "")
    lime_api_key: str = os.getenv("LIME_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./route_recommendation.db")

    # Application settings
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080,http://10.0.0.225:3000").split(",")

    # Gamification settings
    sustainability_points_bike: int = int(os.getenv("SUSTAINABILITY_POINTS_BIKE", "10"))
    sustainability_points_walk: int = int(os.getenv("SUSTAINABILITY_POINTS_WALK", "15"))
    sustainability_points_transit: int = int(os.getenv("SUSTAINABILITY_POINTS_TRANSIT", "8"))
    sustainability_points_car: int = int(os.getenv("SUSTAINABILITY_POINTS_CAR", "0"))

    # Vancouver-specific settings
    vancouver_bounds: dict = {
        "north": 49.3,
        "south": 49.2,
        "east": -123.0,
        "west": -123.3
    }

    # API endpoints
    google_maps_base_url: str = "https://maps.googleapis.com/maps/api"
    translink_base_url: str = "https://api.translink.ca"
    lime_base_url: str = "https://web-production.lime.bike/api/rider/v1"
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    vancouver_open_data_base_url: str = "https://opendata.vancouver.ca/api/3/action"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_api_keys() -> dict:
    """
    Validate that required API keys are present.
    Returns a dictionary with validation results.
    """
    validation_results = {
        "google_maps": bool(settings.google_maps_api_key),
        "translink": bool(settings.translink_api_key),
        "lime": bool(settings.lime_api_key),
        "openweather": bool(settings.openweather_api_key),
        "all_required": True
    }

    # Check if all required keys are present
    required_keys = ["google_maps", "openweather"]  # Minimum required
    validation_results["all_required"] = all(validation_results[key] for key in required_keys)

    return validation_results


def get_api_key_instructions() -> str:
    """
    Return instructions for obtaining API keys.
    """
    return """
    API Key Setup Instructions:

    1. Google Maps API:
       - Go to https://console.cloud.google.com/
       - Create a new project or select existing one
       - Enable the following APIs:
         * Maps JavaScript API
         * Directions API
         * Distance Matrix API
         * Elevation API
         * Roads API
       - Create credentials (API Key)
       - Set GOOGLE_MAPS_API_KEY in your .env file

    2. OpenWeatherMap API:
       - Go to https://openweathermap.org/api
       - Sign up for a free account
       - Get your API key from the dashboard
       - Set OPENWEATHER_API_KEY in your .env file

    3. TransLink API (Vancouver Public Transit):
       - Go to https://developer.translink.ca/
       - Register for an account
       - Request API access
       - Set TRANSLINK_API_KEY in your .env file

    4. Lime API (Bike/Scooter Sharing):
       - Contact Lime for API access
       - Set LIME_API_KEY in your .env file

    5. City of Vancouver Open Data:
       - No API key required
       - Free access to road closures and construction data

    Copy env.example to .env and fill in your API keys.
    """
