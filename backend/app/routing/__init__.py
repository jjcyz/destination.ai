"""
Routing module for the Vancouver Route Recommendation System.

This module contains the refactored routing engine components:
- cost_functions: Cost calculation for different route preferences
- route_converter: Google Maps route conversion utilities
- route_scoring: Route scoring and sorting based on preferences
- route_utils: Utility functions for route processing
- realtime_integration: Real-time data integration
"""

from .cost_functions import get_cost_function, MODE_SPEEDS, MODE_SWITCH_COSTS
from .route_converter import convert_google_route_to_route
from .route_scoring import apply_preference_scoring, sort_routes_by_preferences, is_significantly_different
from .route_utils import (
    generate_instructions,
    calculate_sustainability_points,
    calculate_route_safety_score,
    calculate_energy_efficiency,
    calculate_scenic_score
)
from .realtime_integration import (
    calculate_weather_penalty,
    update_graph_with_real_time_data,
    get_realtime_transit_info
)

__all__ = [
    'get_cost_function',
    'MODE_SPEEDS',
    'MODE_SWITCH_COSTS',
    'convert_google_route_to_route',
    'apply_preference_scoring',
    'sort_routes_by_preferences',
    'is_significantly_different',
    'generate_instructions',
    'calculate_sustainability_points',
    'calculate_route_safety_score',
    'calculate_energy_efficiency',
    'calculate_scenic_score',
    'calculate_weather_penalty',
    'update_graph_with_real_time_data',
    'get_realtime_transit_info',
]

