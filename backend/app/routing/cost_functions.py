"""
Cost functions for different route preferences.
Each function calculates the cost of traversing an edge based on the preference.
"""

from typing import Optional
from ..models import Edge, TransportMode, RoutePreference


# Transport mode speeds (km/h)
MODE_SPEEDS = {
    TransportMode.WALKING: 5.0,
    TransportMode.BIKING: 15.0,
    TransportMode.SCOOTER: 20.0,
    TransportMode.CAR: 50.0,
    TransportMode.BUS: 25.0,
    TransportMode.SKYTRAIN: 40.0,
    TransportMode.SEABUS: 15.0,
    TransportMode.WESTCOAST_EXPRESS: 60.0
}

# Mode switching costs (seconds)
MODE_SWITCH_COSTS = {
    (TransportMode.WALKING, TransportMode.BIKING): 60,
    (TransportMode.WALKING, TransportMode.SCOOTER): 120,
    (TransportMode.WALKING, TransportMode.CAR): 300,
    (TransportMode.WALKING, TransportMode.BUS): 180,
    (TransportMode.BIKING, TransportMode.WALKING): 30,
    (TransportMode.BIKING, TransportMode.SCOOTER): 90,
    (TransportMode.BIKING, TransportMode.CAR): 240,
    (TransportMode.BIKING, TransportMode.BUS): 120,
    (TransportMode.SCOOTER, TransportMode.WALKING): 60,
    (TransportMode.SCOOTER, TransportMode.BIKING): 60,
    (TransportMode.SCOOTER, TransportMode.CAR): 180,
    (TransportMode.SCOOTER, TransportMode.BUS): 90,
    (TransportMode.CAR, TransportMode.WALKING): 120,
    (TransportMode.CAR, TransportMode.BIKING): 180,
    (TransportMode.CAR, TransportMode.SCOOTER): 150,
    (TransportMode.CAR, TransportMode.BUS): 300,
    (TransportMode.BUS, TransportMode.WALKING): 60,
    (TransportMode.BUS, TransportMode.BIKING): 90,
    (TransportMode.BUS, TransportMode.SCOOTER): 90,
    (TransportMode.BUS, TransportMode.CAR): 240,
}


def fastest_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for fastest route (time-based)."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)  # seconds

    # Apply penalties
    effective_time = base_time * edge.weather_penalty * edge.event_penalty

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        effective_time += switch_cost

    return effective_time


def safest_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for safest route (safety-weighted time)."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)

    # Safety penalty based on mode and road conditions
    safety_penalty = 1.0
    if mode == TransportMode.CAR and not edge.is_bike_lane:
        safety_penalty = 1.2  # Cars are less safe
    elif mode in [TransportMode.BIKING, TransportMode.SCOOTER] and not edge.is_bike_lane:
        safety_penalty = 1.5  # Bikes/scooters on roads without bike lanes

    effective_time = base_time * edge.weather_penalty * edge.event_penalty * safety_penalty

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        effective_time += switch_cost

    return effective_time


def energy_efficient_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for energy-efficient route."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)

    # Energy efficiency weights
    energy_weights = {
        TransportMode.WALKING: 0.1,
        TransportMode.BIKING: 0.2,
        TransportMode.SCOOTER: 0.3,
        TransportMode.BUS: 0.4,
        TransportMode.SKYTRAIN: 0.4,
        TransportMode.CAR: 1.0
    }

    energy_cost = edge.distance * energy_weights.get(mode, 0.5)
    effective_time = base_time + energy_cost

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        effective_time += switch_cost

    return effective_time


def scenic_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for scenic route."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)

    # Scenic bonus (negative cost) for slower, more scenic modes
    scenic_bonus = {
        TransportMode.WALKING: -0.2,
        TransportMode.BIKING: -0.1,
        TransportMode.SCOOTER: 0.0,
        TransportMode.BUS: 0.0,
        TransportMode.CAR: 0.1
    }

    effective_time = base_time * (1 + scenic_bonus.get(mode, 0))

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        effective_time += switch_cost

    return effective_time


def healthy_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for healthy route (encourages active transportation)."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)

    # Health bonus for active modes
    health_bonus = {
        TransportMode.WALKING: -0.3,
        TransportMode.BIKING: -0.2,
        TransportMode.SCOOTER: -0.1,
        TransportMode.BUS: 0.0,
        TransportMode.CAR: 0.2
    }

    effective_time = base_time * (1 + health_bonus.get(mode, 0))

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        effective_time += switch_cost

    return effective_time


def cheapest_cost_function(edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
    """Cost function for cheapest route."""
    base_time = edge.distance / (MODE_SPEEDS[mode] * 1000 / 3600)

    # Cost per mode (relative)
    cost_weights = {
        TransportMode.WALKING: 0.0,
        TransportMode.BIKING: 0.1,
        TransportMode.SCOOTER: 0.5,
        TransportMode.BUS: 0.3,
        TransportMode.SKYTRAIN: 0.4,
        TransportMode.CAR: 1.0
    }

    cost = base_time + (edge.distance / 1000) * cost_weights.get(mode, 0.5)

    # Add mode switching cost
    if previous_mode and previous_mode != mode:
        switch_cost = MODE_SWITCH_COSTS.get((previous_mode, mode), 0)
        cost += switch_cost

    return cost


def get_cost_function(preference: RoutePreference):
    """Get cost function based on route preference."""
    cost_functions = {
        RoutePreference.FASTEST: fastest_cost_function,
        RoutePreference.SAFEST: safest_cost_function,
        RoutePreference.ENERGY_EFFICIENT: energy_efficient_cost_function,
        RoutePreference.SCENIC: scenic_cost_function,
        RoutePreference.HEALTHY: healthy_cost_function,
        RoutePreference.CHEAPEST: cheapest_cost_function,
    }
    return cost_functions.get(preference, fastest_cost_function)

