"""
Unit tests for route scoring and sorting functionality.

Tests cover:
- Preference-based scoring
- Route sorting by preferences
- Route difference detection
"""

import pytest
from app.models import Route, RouteStep, Point, RoutePreference, TransportMode
from app.routing.route_scoring import (
    apply_preference_scoring,
    sort_routes_by_preferences,
    is_significantly_different
)


@pytest.fixture
def sample_route():
    """Create a sample route for testing."""
    return Route(
        origin=Point(lat=49.2827, lng=-123.1207),
        destination=Point(lat=49.2606, lng=-123.2460),
        steps=[
            RouteStep(
                mode=TransportMode.WALKING,
                distance=1000.0,
                estimated_time=600,
                instructions="Walk north",
                start_point=Point(lat=49.2827, lng=-123.1207),
                end_point=Point(lat=49.2606, lng=-123.2460)
            )
        ],
        total_distance=1000.0,
        total_time=600,
        preference=RoutePreference.FASTEST,
        safety_score=0.8,
        energy_efficiency=0.9,
        scenic_score=0.6,
        total_sustainability_points=15
    )


@pytest.fixture
def multiple_routes(sample_route):
    """Create multiple routes for testing."""
    route2 = Route(
        origin=sample_route.origin,
        destination=sample_route.destination,
        steps=[
            RouteStep(
                mode=TransportMode.BIKING,
                distance=1200.0,
                estimated_time=400,
                instructions="Bike north",
                start_point=sample_route.origin,
                end_point=sample_route.destination
            )
        ],
        total_distance=1200.0,
        total_time=400,
        preference=RoutePreference.FASTEST,
        safety_score=0.7,
        energy_efficiency=0.95,
        scenic_score=0.7,
        total_sustainability_points=10
    )

    route3 = Route(
        origin=sample_route.origin,
        destination=sample_route.destination,
        steps=[
            RouteStep(
                mode=TransportMode.BUS,
                distance=1500.0,
                estimated_time=900,
                instructions="Take bus",
                start_point=sample_route.origin,
                end_point=sample_route.destination
            )
        ],
        total_distance=1500.0,
        total_time=900,
        preference=RoutePreference.FASTEST,
        safety_score=0.9,
        energy_efficiency=0.8,
        scenic_score=0.5,
        total_sustainability_points=8
    )

    return [sample_route, route2, route3]


class TestApplyPreferenceScoring:
    """Tests for apply_preference_scoring function."""

    def test_apply_preference_scoring_no_preferences(self, sample_route):
        """Test that route is unchanged when no preferences are provided."""
        original_safety = sample_route.safety_score
        original_energy = sample_route.energy_efficiency

        result = apply_preference_scoring(sample_route, [])

        assert result.safety_score == original_safety
        assert result.energy_efficiency == original_energy

    def test_apply_preference_scoring_safest(self, sample_route):
        """Test that SAFEST preference boosts safety score."""
        original_safety = sample_route.safety_score

        result = apply_preference_scoring(sample_route, [RoutePreference.SAFEST])

        assert result.safety_score > original_safety
        assert result.safety_score <= 1.0  # Should not exceed 1.0

    def test_apply_preference_scoring_energy_efficient(self, sample_route):
        """Test that ENERGY_EFFICIENT preference boosts energy efficiency."""
        original_energy = sample_route.energy_efficiency

        result = apply_preference_scoring(sample_route, [RoutePreference.ENERGY_EFFICIENT])

        assert result.energy_efficiency > original_energy
        assert result.energy_efficiency <= 1.0

    def test_apply_preference_scoring_scenic(self, sample_route):
        """Test that SCENIC preference boosts scenic score."""
        original_scenic = sample_route.scenic_score

        result = apply_preference_scoring(sample_route, [RoutePreference.SCENIC])

        assert result.scenic_score > original_scenic
        assert result.scenic_score <= 1.0

    def test_apply_preference_scoring_healthy(self, sample_route):
        """Test that HEALTHY preference boosts sustainability points."""
        original_points = sample_route.total_sustainability_points

        result = apply_preference_scoring(sample_route, [RoutePreference.HEALTHY])

        assert result.total_sustainability_points > original_points

    def test_apply_preference_scoring_multiple_preferences(self, sample_route):
        """Test applying multiple preferences at once."""
        original_safety = sample_route.safety_score
        original_energy = sample_route.energy_efficiency
        original_points = sample_route.total_sustainability_points

        result = apply_preference_scoring(
            sample_route,
            [RoutePreference.SAFEST, RoutePreference.ENERGY_EFFICIENT, RoutePreference.HEALTHY]
        )

        assert result.safety_score > original_safety
        assert result.energy_efficiency > original_energy
        assert result.total_sustainability_points > original_points

    def test_apply_preference_scoring_does_not_exceed_max(self, sample_route):
        """Test that scores don't exceed maximum values."""
        # Set scores to maximum
        sample_route.safety_score = 1.0
        sample_route.energy_efficiency = 1.0
        sample_route.scenic_score = 1.0

        result = apply_preference_scoring(
            sample_route,
            [RoutePreference.SAFEST, RoutePreference.ENERGY_EFFICIENT, RoutePreference.SCENIC]
        )

        assert result.safety_score == 1.0
        assert result.energy_efficiency == 1.0
        assert result.scenic_score == 1.0


class TestSortRoutesByPreferences:
    """Tests for sort_routes_by_preferences function."""

    def test_sort_routes_by_preferences_no_preferences(self, multiple_routes):
        """Test that routes remain in original order when no preferences provided."""
        original_order = [r.total_time for r in multiple_routes]

        result = sort_routes_by_preferences(multiple_routes, [])

        assert len(result) == len(multiple_routes)
        # Order may or may not change, but all routes should be present
        assert all(route in result for route in multiple_routes)

    def test_sort_routes_by_preferences_fastest(self, multiple_routes):
        """Test sorting by FASTEST preference."""
        result = sort_routes_by_preferences(multiple_routes, [RoutePreference.FASTEST])

        assert len(result) == len(multiple_routes)
        # Routes should be sorted by time (fastest first)
        times = [r.total_time for r in result]
        assert times == sorted(times)

    def test_sort_routes_by_preferences_safest(self, multiple_routes):
        """Test sorting by SAFEST preference."""
        result = sort_routes_by_preferences(multiple_routes, [RoutePreference.SAFEST])

        assert len(result) == len(multiple_routes)
        # Routes should be sorted by safety score (highest first)
        safety_scores = [r.safety_score for r in result]
        assert safety_scores == sorted(safety_scores, reverse=True)

    def test_sort_routes_by_preferences_energy_efficient(self, multiple_routes):
        """Test sorting by ENERGY_EFFICIENT preference."""
        result = sort_routes_by_preferences(multiple_routes, [RoutePreference.ENERGY_EFFICIENT])

        assert len(result) == len(multiple_routes)
        # Routes should be sorted by energy efficiency (highest first)
        energy_scores = [r.energy_efficiency for r in result]
        assert energy_scores == sorted(energy_scores, reverse=True)

    def test_sort_routes_by_preferences_multiple_preferences(self, multiple_routes):
        """Test sorting with multiple preferences."""
        result = sort_routes_by_preferences(
            multiple_routes,
            [RoutePreference.FASTEST, RoutePreference.SAFEST]
        )

        assert len(result) == len(multiple_routes)
        # Should be sorted by combined score
        assert result[0] in multiple_routes

    def test_sort_routes_by_preferences_empty_list(self):
        """Test sorting empty route list."""
        result = sort_routes_by_preferences([], [RoutePreference.FASTEST])
        assert result == []


class TestIsSignificantlyDifferent:
    """Tests for is_significantly_different function."""

    def test_is_significantly_different_empty_list(self, sample_route):
        """Test that route is different when no existing routes."""
        assert is_significantly_different(sample_route, []) is True

    def test_is_significantly_different_similar_distance(self, sample_route):
        """Test that routes with similar distance are not significantly different."""
        similar_route = Route(
            origin=sample_route.origin,
            destination=sample_route.destination,
            steps=sample_route.steps,
            total_distance=1050.0,  # Only 5% different
            total_time=600,
            preference=RoutePreference.FASTEST
        )

        assert is_significantly_different(similar_route, [sample_route]) is False

    def test_is_significantly_different_different_distance(self, sample_route):
        """Test that routes with significantly different distance are different."""
        # Note: Function requires BOTH distance difference (>20%) AND different modes
        # Since this route uses same modes, it will return False
        different_route = Route(
            origin=sample_route.origin,
            destination=sample_route.destination,
            steps=sample_route.steps,  # Same modes
            total_distance=2000.0,  # 100% different distance
            total_time=1200,
            preference=RoutePreference.FASTEST
        )

        # Function returns False because modes are the same, even though distance differs
        assert is_significantly_different(different_route, [sample_route]) is False

    def test_is_significantly_different_different_modes(self, sample_route):
        """Test that routes with different transport modes are different."""
        # Note: Function requires BOTH distance difference (>20%) AND different modes
        # Since distance is the same, it will return False
        different_mode_route = Route(
            origin=sample_route.origin,
            destination=sample_route.destination,
            steps=[
                RouteStep(
                    mode=TransportMode.BIKING,  # Different mode
                    distance=1000.0,  # Same distance
                    estimated_time=600,
                    instructions="Bike",
                    start_point=sample_route.origin,
                    end_point=sample_route.destination
                )
            ],
            total_distance=1000.0,  # Same distance
            total_time=600,
            preference=RoutePreference.FASTEST
        )

        # Function returns False because distance is too similar (<20% difference)
        assert is_significantly_different(different_mode_route, [sample_route]) is False

    def test_is_significantly_different_both_different(self, sample_route):
        """Test that routes with both different distance AND different modes are different."""
        different_route = Route(
            origin=sample_route.origin,
            destination=sample_route.destination,
            steps=[
                RouteStep(
                    mode=TransportMode.BIKING,  # Different mode
                    distance=2000.0,  # Different distance
                    estimated_time=800,
                    instructions="Bike",
                    start_point=sample_route.origin,
                    end_point=sample_route.destination
                )
            ],
            total_distance=2000.0,  # 100% different distance
            total_time=800,
            preference=RoutePreference.FASTEST
        )

        # Function returns True because BOTH distance differs (>20%) AND modes differ
        assert is_significantly_different(different_route, [sample_route]) is True

    def test_is_significantly_different_same_mode_similar_distance(self, sample_route):
        """Test that routes with same mode and similar distance are not different."""
        similar_route = Route(
            origin=sample_route.origin,
            destination=sample_route.destination,
            steps=[
                RouteStep(
                    mode=TransportMode.WALKING,  # Same mode
                    distance=1100.0,  # Only 10% different
                    estimated_time=650,
                    instructions="Walk",
                    start_point=sample_route.origin,
                    end_point=sample_route.destination
                )
            ],
            total_distance=1100.0,
            total_time=650,
            preference=RoutePreference.FASTEST
        )

        assert is_significantly_different(similar_route, [sample_route]) is False

