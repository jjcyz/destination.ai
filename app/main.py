"""
Main FastAPI application for the Vancouver Route Recommendation System.
Provides REST API endpoints for route calculation and user management.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Optional
from datetime import datetime

from .models import (
    RouteRequest, RouteResponse, Point, UserProfile, GamificationStats,
    RoutePreference, TransportMode, Route
)
from .routing_engine import RoutingEngine
from .graph_builder import VancouverGraphBuilder
from .gamification import GamificationEngine
from .config import settings, validate_api_keys, get_api_key_instructions

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vancouver Route Recommendation System",
    description="AI-powered multi-modal route recommendation system for Vancouver, Canada",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
graph_builder = None
routing_engine = None
gamification_engine = GamificationEngine()


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global graph_builder, routing_engine

    logger.info("Starting Vancouver Route Recommendation System...")

    # Validate API keys
    validation_results = validate_api_keys()
    if not validation_results["all_required"]:
        logger.warning("Some API keys are missing. Check the configuration.")
        logger.info(get_api_key_instructions())

    # Initialize graph builder and routing engine
    graph_builder = VancouverGraphBuilder()
    routing_engine = RoutingEngine(graph_builder)

    logger.info("Application started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global graph_builder, routing_engine

    if routing_engine:
        await routing_engine.close()
    if graph_builder:
        await graph_builder.close()

    logger.info("Application shutdown complete.")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Vancouver Route Recommendation System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "route": "/api/v1/route",
            "health": "/health",
            "config": "/api/v1/config",
            "gamification": "/api/v1/gamification"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_keys": validate_api_keys()
    }


@app.get("/api/v1/config")
async def get_config():
    """Get API configuration and instructions."""
    return {
        "api_keys_status": validate_api_keys(),
        "instructions": get_api_key_instructions(),
        "vancouver_bounds": settings.vancouver_bounds,
        "supported_modes": [mode.value for mode in TransportMode],
        "supported_preferences": [pref.value for pref in RoutePreference]
    }


@app.post("/api/v1/route", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    """
    Calculate optimal routes between origin and destination.

    Args:
        request: Route request with preferences and constraints

    Returns:
        RouteResponse with calculated routes and alternatives
    """
    try:
        if not routing_engine:
            raise HTTPException(status_code=503, detail="Routing engine not initialized")

        # Validate request
        if not request.origin or not request.destination:
            raise HTTPException(status_code=400, detail="Origin and destination are required")

        # Check if points are within Vancouver bounds
        if not _is_within_vancouver_bounds(request.origin) or not _is_within_vancouver_bounds(request.destination):
            raise HTTPException(
                status_code=400,
                detail="Origin and destination must be within Vancouver city limits"
            )

        # Calculate routes
        response = await routing_engine.find_routes(request)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/route/geocode")
async def geocode_address(address: str):
    """
    Geocode an address to coordinates.

    Args:
        address: Address string to geocode

    Returns:
        Point with latitude and longitude
    """
    try:
        if not routing_engine or not routing_engine.api_client:
            raise HTTPException(status_code=503, detail="API client not initialized")

        point = await routing_engine.api_client.google_maps.geocode(address)

        if not point:
            raise HTTPException(status_code=404, detail="Address not found")

        return point

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error geocoding address: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/gamification/rewards")
async def calculate_rewards(route: dict, user_profile: dict):
    """
    Calculate gamification rewards for a completed route.

    Args:
        route: Route data
        user_profile: User profile data

    Returns:
        Rewards and statistics
    """
    try:
        # Convert dict to models (simplified for demo)
        route_obj = Route(**route)
        user_profile_obj = UserProfile(**user_profile)

        rewards = gamification_engine.calculate_route_rewards(route_obj, user_profile_obj)

        return rewards

    except Exception as e:
        logger.error(f"Error calculating rewards: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/gamification/achievements")
async def get_achievements():
    """Get all available achievements."""
    return {
        "achievements": [
            {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "points_reward": achievement.points_reward
            }
            for achievement in gamification_engine.achievements
        ]
    }


@app.get("/api/v1/gamification/badges")
async def get_badges():
    """Get all available badges."""
    return {
        "badges": [
            {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "rarity": badge.rarity
            }
            for badge in gamification_engine.badges
        ]
    }


@app.get("/api/v1/gamification/challenges")
async def get_daily_challenges():
    """Get daily challenges."""
    return {
        "challenges": gamification_engine.get_daily_challenges()
    }


@app.get("/api/v1/gamification/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get leaderboard data."""
    return {
        "leaderboard": gamification_engine.get_leaderboard_data(limit)
    }


@app.get("/api/v1/gamification/tips")
async def get_sustainability_tips():
    """Get sustainability tips."""
    return {
        "tips": gamification_engine.get_sustainability_tips()
    }


def _is_within_vancouver_bounds(point: Point) -> bool:
    """Check if a point is within Vancouver city bounds."""
    bounds = settings.vancouver_bounds
    return (
        bounds["south"] <= point.lat <= bounds["north"] and
        bounds["west"] <= point.lng <= bounds["east"]
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
