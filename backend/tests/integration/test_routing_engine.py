"""
Integration tests for RoutingEngine.

Tests cover:
- Route finding with different transport modes
- Route preference application
- Real-time data integration
- Error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routing_engine import RoutingEngine
from app.models import (
    RouteRequest, Point, TransportMode, RoutePreference,
    RouteResponse, Route, RouteStep
)
from app.graph_builder import VancouverGraphBuilder


@pytest.fixture
def mock_graph_builder():
    """Mock graph builder."""
    mock_builder = MagicMock(spec=VancouverGraphBuilder)
    mock_builder.graph = MagicMock()
    return mock_builder


@pytest.fixture
def mock_api_client():
    """Mock API client manager."""
    mock_client = MagicMock()
    mock_client.google_maps = MagicMock()
    mock_client.google_maps.get_directions = AsyncMock()
    mock_client.translink = MagicMock()
    mock_client.translink.get_trip_updates = AsyncMock(return_value=[])
    mock_client.translink.get_service_alerts = AsyncMock(return_value=[])
    mock_client.openweather = MagicMock()
    mock_client.openweather.get_weather = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def routing_engine(mock_graph_builder, mock_api_client):
    """Create routing engine with mocked dependencies."""
    engine = RoutingEngine(mock_graph_builder)
    engine.api_client = mock_api_client
    return engine


@pytest.fixture
def sample_route_request():
    """Sample route request."""
    return RouteRequest(
        origin=Point(lat=49.2827, lng=-123.1207),
        destination=Point(lat=49.2606, lng=-123.2460),
        preferences=[RoutePreference.FASTEST],
        transport_modes=[TransportMode.WALKING]
    )


@pytest.fixture
def mock_google_maps_response():
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


class TestRoutingEngineFindRoutes:
    """Tests for RoutingEngine.find_routes method."""

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_demo_mode(self, mock_validate_keys, routing_engine, sample_route_request):
        """Test route finding in demo mode (no API keys)."""
        mock_validate_keys.return_value = {"all_required": False}

        response = await routing_engine.find_routes(sample_route_request)

        assert isinstance(response, RouteResponse)
        assert len(response.routes) > 0
        assert "demo" in response.data_sources[0].lower() or "mock" in response.data_sources[0].lower()

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_walking_mode(
        self, mock_validate_keys, routing_engine, sample_route_request, mock_google_maps_response
    ):
        """Test route finding for walking mode."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(return_value=mock_google_maps_response)

        response = await routing_engine.find_routes(sample_route_request)

        assert isinstance(response, RouteResponse)
        assert len(response.routes) > 0
        assert response.routes[0].steps[0].mode == TransportMode.WALKING

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_multiple_modes(
        self, mock_validate_keys, routing_engine, mock_google_maps_response
    ):
        """Test route finding with multiple transport modes."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(return_value=mock_google_maps_response)

        request = RouteRequest(
            origin=Point(lat=49.2827, lng=-123.1207),
            destination=Point(lat=49.2606, lng=-123.2460),
            transport_modes=[TransportMode.WALKING, TransportMode.BIKING]
        )

        response = await routing_engine.find_routes(request)

        assert isinstance(response, RouteResponse)
        # Should have routes for different modes
        assert len(response.routes) > 0

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_api_timeout(
        self, mock_validate_keys, routing_engine, sample_route_request
    ):
        """Test handling of API timeout."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(side_effect=TimeoutError())

        # Should handle timeout gracefully
        response = await routing_engine.find_routes(sample_route_request)

        # Should either return empty routes or fallback to demo
        assert isinstance(response, RouteResponse)

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_api_error(
        self, mock_validate_keys, routing_engine, sample_route_request
    ):
        """Test handling of API errors."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(side_effect=Exception("API Error"))

        # Should handle error gracefully
        response = await routing_engine.find_routes(sample_route_request)

        assert isinstance(response, RouteResponse)

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_no_routes_found(
        self, mock_validate_keys, routing_engine, sample_route_request
    ):
        """Test handling when no routes are found."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(return_value={"routes": []})

        response = await routing_engine.find_routes(sample_route_request)

        assert isinstance(response, RouteResponse)
        # May have empty routes or fallback routes
        assert isinstance(response.routes, list)

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_with_preferences(
        self, mock_validate_keys, routing_engine, mock_google_maps_response
    ):
        """Test route finding with different preferences."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(return_value=mock_google_maps_response)

        request = RouteRequest(
            origin=Point(lat=49.2827, lng=-123.1207),
            destination=Point(lat=49.2606, lng=-123.2460),
            preferences=[RoutePreference.SAFEST, RoutePreference.SCENIC],
            transport_modes=[TransportMode.WALKING]
        )

        response = await routing_engine.find_routes(request)

        assert isinstance(response, RouteResponse)
        assert len(response.routes) > 0

    @patch('app.config.validate_api_keys')
    @pytest.mark.asyncio
    async def test_find_routes_processing_time(
        self, mock_validate_keys, routing_engine, sample_route_request, mock_google_maps_response
    ):
        """Test that processing time is recorded."""
        mock_validate_keys.return_value = {"all_required": True}
        routing_engine.api_client.google_maps.get_directions = AsyncMock(return_value=mock_google_maps_response)

        response = await routing_engine.find_routes(sample_route_request)

        assert isinstance(response, RouteResponse)
        assert response.processing_time > 0
        assert isinstance(response.processing_time, float)

