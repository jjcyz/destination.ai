"""
Shared pytest fixtures and configuration for all tests.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path if not already there
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from typing import Dict, Any
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.models import (
    Point, RouteRequest, RouteResponse, Route, RouteStep,
    TransportMode, RoutePreference, UserProfile
)


@pytest.fixture
def sample_point_vancouver() -> Point:
    """Sample point in Vancouver downtown."""
    return Point(lat=49.2827, lng=-123.1207)


@pytest.fixture
def sample_point_ubc() -> Point:
    """Sample point at UBC."""
    return Point(lat=49.2606, lng=-123.2460)


@pytest.fixture
def sample_route_request(sample_point_vancouver, sample_point_ubc) -> RouteRequest:
    """Sample route request from Vancouver downtown to UBC."""
    return RouteRequest(
        origin=sample_point_vancouver,
        destination=sample_point_ubc,
        preferences=[RoutePreference.FASTEST],
        transport_modes=[TransportMode.WALKING, TransportMode.BUS],
        departure_time=None,
        max_walking_distance=2000
    )


@pytest.fixture
def sample_route_step_walking(sample_point_vancouver, sample_point_ubc) -> RouteStep:
    """Sample walking route step."""
    return RouteStep(
        mode=TransportMode.WALKING,
        distance=1000.0,
        estimated_time=600,
        instructions="Walk north on Main Street",
        start_point=sample_point_vancouver,
        end_point=sample_point_ubc,
        sustainability_points=15
    )


@pytest.fixture
def sample_route(sample_point_vancouver, sample_point_ubc, sample_route_step_walking) -> Route:
    """Sample route with one step."""
    return Route(
        origin=sample_point_vancouver,
        destination=sample_point_ubc,
        steps=[sample_route_step_walking],
        total_distance=1000.0,
        total_time=600,
        preference=RoutePreference.FASTEST,
        total_sustainability_points=15
    )


@pytest.fixture
def sample_user_profile() -> UserProfile:
    """Sample user profile."""
    return UserProfile(
        user_id="test_user_123",
        preferred_modes=[TransportMode.WALKING, TransportMode.BIKING],
        fitness_level="moderate",
        sustainability_goals=True,
        level=1,
        total_sustainability_points=100
    )


@pytest.fixture
def mock_google_maps_response() -> Dict[str, Any]:
    """Mock Google Maps Directions API response."""
    return {
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
                "overview_polyline": {"points": "test_overview_polyline"},
                "summary": "Main Street"
            }
        ],
        "status": "OK"
    }


@pytest.fixture
def mock_geocode_response() -> Dict[str, Any]:
    """Mock Google Maps Geocoding API response."""
    return {
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


@pytest.fixture
def mock_translink_gtfs_response() -> bytes:
    """Mock TransLink GTFS-RT response (empty protobuf)."""
    # Return empty bytes - actual tests will use proper protobuf mocking
    return b""


@pytest.fixture
def mock_api_client_manager():
    """Mock APIClientManager."""
    mock_manager = MagicMock()
    mock_manager.google_maps = MagicMock()
    mock_manager.google_maps.get_directions = AsyncMock()
    mock_manager.google_maps.geocode = AsyncMock()
    mock_manager.translink = MagicMock()
    mock_manager.translink.get_trip_updates = AsyncMock(return_value=[])
    mock_manager.translink.get_service_alerts = AsyncMock(return_value=[])
    return mock_manager


@pytest.fixture
def mock_graph_builder():
    """Mock VancouverGraphBuilder."""
    mock_builder = MagicMock()
    mock_builder.graph = MagicMock()
    return mock_builder

