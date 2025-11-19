"""
Route scoring and sorting based on user preferences.
"""

from typing import List
from ..models import Route, RoutePreference


def apply_preference_scoring(route: Route, preferences: List[RoutePreference]) -> Route:
    """Apply preference-based scoring to enhance route metrics."""
    if not preferences:
        return route

    # Adjust scores based on preferences
    for preference in preferences:
        if preference == RoutePreference.SAFEST:
            route.safety_score = min(1.0, route.safety_score * 1.1)
        elif preference == RoutePreference.ENERGY_EFFICIENT:
            route.energy_efficiency = min(1.0, route.energy_efficiency * 1.1)
        elif preference == RoutePreference.SCENIC:
            route.scenic_score = min(1.0, route.scenic_score * 1.1)
        elif preference == RoutePreference.HEALTHY:
            # Boost sustainability points for healthy routes
            route.total_sustainability_points = int(route.total_sustainability_points * 1.2)

    return route


def sort_routes_by_preferences(routes: List[Route], preferences: List[RoutePreference]) -> List[Route]:
    """Sort routes by preference priority."""
    if not preferences:
        return routes

    def route_score(route: Route) -> float:
        score = 0.0
        for pref in preferences:
            if pref == RoutePreference.FASTEST:
                score += 1000.0 / max(route.total_time, 1)  # Higher score for faster routes
            elif pref == RoutePreference.SAFEST:
                score += route.safety_score * 100
            elif pref == RoutePreference.ENERGY_EFFICIENT:
                score += route.energy_efficiency * 100
            elif pref == RoutePreference.SCENIC:
                score += route.scenic_score * 100
            elif pref == RoutePreference.HEALTHY:
                score += route.total_sustainability_points
            elif pref == RoutePreference.CHEAPEST:
                # Assume cheaper = less distance for walking/biking
                score += 1000.0 / max(route.total_distance, 1)
        return score

    return sorted(routes, key=route_score, reverse=True)


def is_significantly_different(route: Route, existing_routes: List[Route]) -> bool:
    """Check if a route is significantly different from existing routes."""
    if not existing_routes:
        return True

    # Check if route uses different modes or has significantly different distance
    for existing_route in existing_routes:
        # Compare total distance (should be at least 20% different)
        distance_ratio = abs(route.total_distance - existing_route.total_distance) / existing_route.total_distance
        if distance_ratio < 0.2:
            return False

        # Compare modes used
        route_modes = set(step.mode for step in route.steps)
        existing_modes = set(step.mode for step in existing_route.steps)
        if route_modes == existing_modes:
            return False

    return True

