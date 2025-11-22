"""
Sample test data for use across tests.

This module provides reusable sample data structures that can be used
across multiple test files to ensure consistency.
"""

from app.models import (
    Point, Route, RouteStep, RouteRequest, RouteResponse,
    TransportMode, RoutePreference, UserProfile
)
from datetime import datetime


# Sample geographic points
VANCOUVER_DOWNTOWN = Point(lat=49.2827, lng=-123.1207)
UBC = Point(lat=49.2606, lng=-123.2460)
STANLEY_PARK = Point(lat=49.3017, lng=-123.1417)
RICHMOND = Point(lat=49.1666, lng=-123.1364)
BURNABY = Point(lat=49.2488, lng=-122.9805)


def create_sample_route_request(
    origin: Point = VANCOUVER_DOWNTOWN,
    destination: Point = UBC,
    modes: list = None,
    preferences: list = None
) -> RouteRequest:
    """Create a sample route request."""
    if modes is None:
        modes = [TransportMode.WALKING]
    if preferences is None:
        preferences = [RoutePreference.FASTEST]

    return RouteRequest(
        origin=origin,
        destination=destination,
        transport_modes=modes,
        preferences=preferences
    )


def create_sample_walking_step(
    start: Point = VANCOUVER_DOWNTOWN,
    end: Point = UBC,
    distance: float = 1000.0,
    time: int = 600
) -> RouteStep:
    """Create a sample walking route step."""
    return RouteStep(
        mode=TransportMode.WALKING,
        distance=distance,
        estimated_time=time,
        instructions="Walk north on Main Street",
        start_point=start,
        end_point=end,
        sustainability_points=15
    )


def create_sample_route(
    origin: Point = VANCOUVER_DOWNTOWN,
    destination: Point = UBC,
    steps: list = None,
    preference: RoutePreference = RoutePreference.FASTEST
) -> Route:
    """Create a sample route."""
    if steps is None:
        steps = [create_sample_walking_step(origin, destination)]

    total_distance = sum(step.distance for step in steps)
    total_time = sum(step.estimated_time for step in steps)
    total_points = sum(step.sustainability_points for step in steps)

    return Route(
        origin=origin,
        destination=destination,
        steps=steps,
        total_distance=total_distance,
        total_time=total_time,
        preference=preference,
        total_sustainability_points=total_points
    )


def create_sample_route_response(
    routes: list = None,
    alternatives: list = None
) -> RouteResponse:
    """Create a sample route response."""
    if routes is None:
        routes = [create_sample_route()]
    if alternatives is None:
        alternatives = []

    return RouteResponse(
        routes=routes,
        alternatives=alternatives,
        processing_time=0.5,
        data_sources=["google_maps"]
    )


def create_sample_user_profile(
    user_id: str = "test_user_123",
    preferred_modes: list = None,
    level: int = 1
) -> UserProfile:
    """Create a sample user profile."""
    if preferred_modes is None:
        preferred_modes = [TransportMode.WALKING, TransportMode.BIKING]

    return UserProfile(
        user_id=user_id,
        preferred_modes=preferred_modes,
        fitness_level="moderate",
        sustainability_goals=True,
        level=level,
        total_sustainability_points=100
    )


# Sample Google Maps API responses
SAMPLE_GOOGLE_MAPS_WALKING_RESPONSE = {
    "routes": [
        {
            "legs": [
                {
                    "distance": {"value": 1000, "text": "1.0 km"},
                    "duration": {"value": 600, "text": "10 mins"},
                    "steps": [
                        {
                            "distance": {"value": 1000, "text": "1.0 km"},
                            "duration": {"value": 600, "text": "10 mins"},
                            "start_location": {"lat": 49.2827, "lng": -123.1207},
                            "end_location": {"lat": 49.2606, "lng": -123.2460},
                            "html_instructions": "Walk north on Main Street",
                            "polyline": {"points": "test_polyline"},
                            "travel_mode": "WALKING"
                        }
                    ],
                    "start_location": {"lat": 49.2827, "lng": -123.1207},
                    "end_location": {"lat": 49.2606, "lng": -123.2460}
                }
            ],
            "overview_polyline": {"points": "overview_polyline"},
            "summary": "Main Street"
        }
    ],
    "status": "OK"
}


SAMPLE_GOOGLE_MAPS_GEOCODE_RESPONSE = {
    "results": [
        {
            "geometry": {
                "location": {
                    "lat": 49.2827,
                    "lng": -123.1207
                }
            },
            "formatted_address": "Vancouver, BC, Canada"
        }
    ],
    "status": "OK"
}

