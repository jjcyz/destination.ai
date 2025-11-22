"""
Unit tests for app.models module.

Tests cover:
- Point distance calculations
- Edge cost calculations
- Model validation
- Enum values
"""

import pytest
from app.models import (
    Point, Node, Edge, Route, RouteStep, RouteRequest,
    TransportMode, RoutePreference, WeatherCondition,
    UserProfile
)


class TestPoint:
    """Tests for Point model."""

    def test_point_creation(self):
        """Test creating a Point with valid coordinates."""
        point = Point(lat=49.2827, lng=-123.1207)
        assert point.lat == 49.2827
        assert point.lng == -123.1207

    def test_point_distance_calculation_same_point(self):
        """Test distance calculation between identical points."""
        point = Point(lat=49.2827, lng=-123.1207)
        distance = point.distance_to(point)
        assert distance == 0.0

    def test_point_distance_calculation_vancouver_to_ubc(self):
        """Test distance calculation from Vancouver downtown to UBC."""
        vancouver = Point(lat=49.2827, lng=-123.1207)
        ubc = Point(lat=49.2606, lng=-123.2460)
        distance = vancouver.distance_to(ubc)

        # Distance should be approximately 9-10 km
        assert distance > 8000  # At least 8 km
        assert distance < 12000  # At most 12 km
        assert isinstance(distance, float)

    def test_point_distance_calculation_known_distance(self):
        """Test distance calculation with known coordinates."""
        # Two points approximately 1 km apart
        point1 = Point(lat=49.2827, lng=-123.1207)
        point2 = Point(lat=49.2917, lng=-123.1207)  # ~1 km north
        distance = point1.distance_to(point2)

        # Should be approximately 1000 meters
        assert 900 < distance < 1100

    def test_point_serialization(self):
        """Test Point model serialization."""
        point = Point(lat=49.2827, lng=-123.1207)
        data = point.model_dump()
        assert data["lat"] == 49.2827
        assert data["lng"] == -123.1207


class TestEdge:
    """Tests for Edge model."""

    def test_edge_creation(self):
        """Test creating an Edge with required fields."""
        edge = Edge(
            from_node="node1",
            to_node="node2",
            distance=1000.0,
            allowed_modes=[TransportMode.WALKING]
        )
        assert edge.from_node == "node1"
        assert edge.to_node == "node2"
        assert edge.distance == 1000.0
        assert TransportMode.WALKING in edge.allowed_modes

    def test_edge_cost_calculation_walking(self):
        """Test edge cost calculation for walking mode."""
        edge = Edge(
            from_node="node1",
            to_node="node2",
            distance=1000.0,  # 1 km
            allowed_modes=[TransportMode.WALKING]
        )
        # Walking speed ~5 km/h = 1.39 m/s
        base_speed = 5.0  # km/h
        cost = edge.get_effective_cost(TransportMode.WALKING, base_speed)

        # Should take approximately 720 seconds (12 minutes) for 1 km at 5 km/h
        assert cost > 600
        assert cost < 900
        assert isinstance(cost, float)

    def test_edge_cost_calculation_biking(self):
        """Test edge cost calculation for biking mode."""
        edge = Edge(
            from_node="node1",
            to_node="node2",
            distance=1000.0,  # 1 km
            allowed_modes=[TransportMode.BIKING]
        )
        # Biking speed ~15 km/h = 4.17 m/s
        base_speed = 15.0  # km/h
        cost = edge.get_effective_cost(TransportMode.BIKING, base_speed)

        # Should take approximately 240 seconds (4 minutes) for 1 km at 15 km/h
        assert cost > 200
        assert cost < 300
        assert isinstance(cost, float)

    def test_edge_cost_calculation_disallowed_mode(self):
        """Test edge cost calculation for disallowed mode returns infinity."""
        edge = Edge(
            from_node="node1",
            to_node="node2",
            distance=1000.0,
            allowed_modes=[TransportMode.WALKING]
        )
        cost = edge.get_effective_cost(TransportMode.CAR, 50.0)
        assert cost == float('inf')

    def test_edge_cost_with_penalties(self):
        """Test edge cost calculation with weather and event penalties."""
        edge = Edge(
            from_node="node1",
            to_node="node2",
            distance=1000.0,
            allowed_modes=[TransportMode.WALKING],
            weather_penalty=1.5,  # 50% slower due to weather
            event_penalty=1.2  # 20% slower due to event
        )
        base_speed = 5.0
        cost = edge.get_effective_cost(TransportMode.WALKING, base_speed)

        # Cost should be higher than without penalties
        base_cost = 1000.0 / (5.0 * 1000 / 3600)  # ~720 seconds
        expected_cost = base_cost * 1.5 * 1.2  # ~1296 seconds
        assert cost > expected_cost * 0.9
        assert cost < expected_cost * 1.1


class TestRouteStep:
    """Tests for RouteStep model."""

    def test_route_step_creation(self, sample_point_vancouver, sample_point_ubc):
        """Test creating a RouteStep."""
        step = RouteStep(
            mode=TransportMode.WALKING,
            distance=1000.0,
            estimated_time=600,
            instructions="Walk north",
            start_point=sample_point_vancouver,
            end_point=sample_point_ubc
        )
        assert step.mode == TransportMode.WALKING
        assert step.distance == 1000.0
        assert step.estimated_time == 600
        assert step.instructions == "Walk north"

    def test_route_step_default_values(self, sample_point_vancouver, sample_point_ubc):
        """Test RouteStep default values."""
        step = RouteStep(
            mode=TransportMode.WALKING,
            distance=1000.0,
            estimated_time=600,
            instructions="Walk",
            start_point=sample_point_vancouver,
            end_point=sample_point_ubc
        )
        assert step.effort_level == "moderate"
        assert step.sustainability_points == 0


class TestRoute:
    """Tests for Route model."""

    def test_route_creation(self, sample_point_vancouver, sample_point_ubc, sample_route_step_walking):
        """Test creating a Route."""
        route = Route(
            origin=sample_point_vancouver,
            destination=sample_point_ubc,
            steps=[sample_route_step_walking],
            total_distance=1000.0,
            total_time=600,
            preference=RoutePreference.FASTEST
        )
        assert route.origin == sample_point_vancouver
        assert route.destination == sample_point_ubc
        assert len(route.steps) == 1
        assert route.total_distance == 1000.0
        assert route.total_time == 600

    def test_route_default_values(self, sample_point_vancouver, sample_point_ubc, sample_route_step_walking):
        """Test Route default values."""
        route = Route(
            origin=sample_point_vancouver,
            destination=sample_point_ubc,
            steps=[sample_route_step_walking],
            total_distance=1000.0,
            total_time=600,
            preference=RoutePreference.FASTEST
        )
        assert route.safety_score == 1.0
        assert route.energy_efficiency == 1.0
        assert route.scenic_score == 0.5
        assert route.created_at is not None


class TestRouteRequest:
    """Tests for RouteRequest model."""

    def test_route_request_creation(self, sample_point_vancouver, sample_point_ubc):
        """Test creating a RouteRequest."""
        request = RouteRequest(
            origin=sample_point_vancouver,
            destination=sample_point_ubc,
            preferences=[RoutePreference.FASTEST],
            transport_modes=[TransportMode.WALKING]
        )
        assert request.origin == sample_point_vancouver
        assert request.destination == sample_point_ubc
        assert RoutePreference.FASTEST in request.preferences

    def test_route_request_default_values(self, sample_point_vancouver, sample_point_ubc):
        """Test RouteRequest default values."""
        request = RouteRequest(
            origin=sample_point_vancouver,
            destination=sample_point_ubc
        )
        assert RoutePreference.FASTEST in request.preferences
        assert TransportMode.WALKING in request.transport_modes
        assert request.max_walking_distance == 2000
        assert request.avoid_highways is False


class TestEnums:
    """Tests for Enum classes."""

    def test_transport_mode_values(self):
        """Test TransportMode enum values."""
        assert TransportMode.WALKING.value == "walking"
        assert TransportMode.BIKING.value == "biking"
        assert TransportMode.BUS.value == "bus"
        assert TransportMode.CAR.value == "car"

    def test_route_preference_values(self):
        """Test RoutePreference enum values."""
        assert RoutePreference.FASTEST.value == "fastest"
        assert RoutePreference.SAFEST.value == "safest"
        assert RoutePreference.SCENIC.value == "scenic"

    def test_weather_condition_values(self):
        """Test WeatherCondition enum values."""
        assert WeatherCondition.CLEAR.value == "clear"
        assert WeatherCondition.RAIN.value == "rain"
        assert WeatherCondition.SNOW.value == "snow"


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_user_profile_creation(self):
        """Test creating a UserProfile."""
        profile = UserProfile(
            user_id="test_user",
            preferred_modes=[TransportMode.WALKING],
            fitness_level="moderate"
        )
        assert profile.user_id == "test_user"
        assert TransportMode.WALKING in profile.preferred_modes
        assert profile.fitness_level == "moderate"

    def test_user_profile_default_values(self):
        """Test UserProfile default values."""
        profile = UserProfile(user_id="test_user")
        assert profile.sustainability_goals is True
        assert profile.level == 1
        assert profile.total_sustainability_points == 0
        assert profile.streak_days == 0
        assert isinstance(profile.achievements, list)
        assert isinstance(profile.badges, list)

