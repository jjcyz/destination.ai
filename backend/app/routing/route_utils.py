"""
Utility functions for route calculation and processing.
Includes instruction generation, sustainability calculations, and route quality metrics.
"""

from typing import List
from ..models import Node, Edge, RouteStep, TransportMode

# Transport mode speeds (km/h) - shared with cost_functions
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


def generate_instructions(
    from_node: Node,
    to_node: Node,
    mode: TransportMode,
    step_index: int,
    total_steps: int,
    edge: Edge
) -> str:
    """Generate human-readable instructions for a route step."""
    if step_index == 0:
        if mode == TransportMode.WALKING:
            return f"Start walking from {from_node.name or 'your location'}"
        elif mode == TransportMode.BIKING:
            return f"Start biking from {from_node.name or 'your location'}"
        elif mode == TransportMode.CAR:
            return f"Start driving from {from_node.name or 'your location'}"
        elif mode == TransportMode.BUS:
            return f"Take the bus from {from_node.name or 'the bus stop'}"
        else:
            return f"Start your journey using {mode.value}"

    if step_index == total_steps - 1:
        return f"Arrive at {to_node.name or 'your destination'}"

    # Calculate direction
    lat_diff = to_node.point.lat - from_node.point.lat
    lng_diff = to_node.point.lng - from_node.point.lng

    if abs(lat_diff) > abs(lng_diff):
        direction = "north" if lat_diff > 0 else "south"
    else:
        direction = "east" if lng_diff > 0 else "west"

    distance_km = edge.distance / 1000

    if mode == TransportMode.WALKING:
        return f"Walk {distance_km:.1f}km {direction}"
    elif mode == TransportMode.BIKING:
        return f"Bike {distance_km:.1f}km {direction}"
    elif mode == TransportMode.CAR:
        return f"Drive {distance_km:.1f}km {direction}"
    elif mode == TransportMode.BUS:
        return f"Take bus {distance_km:.1f}km {direction}"
    else:
        return f"Continue {distance_km:.1f}km {direction} using {mode.value}"


def calculate_sustainability_points(mode: TransportMode, distance: float) -> int:
    """Calculate sustainability points for a route step."""
    points_per_km = {
        TransportMode.WALKING: 15,
        TransportMode.BIKING: 10,
        TransportMode.SCOOTER: 8,
        TransportMode.BUS: 8,
        TransportMode.SKYTRAIN: 8,
        TransportMode.CAR: 0
    }

    return int((distance / 1000) * points_per_km.get(mode, 0))


def calculate_route_safety_score(steps: List[RouteStep]) -> float:
    """Calculate overall safety score for a route."""
    if not steps:
        return 1.0

    safety_scores = []
    for step in steps:
        if step.mode in [TransportMode.WALKING, TransportMode.BIKING, TransportMode.SCOOTER]:
            # Active modes are generally safer
            safety_scores.append(0.9)
        elif step.mode == TransportMode.CAR:
            # Cars have moderate safety
            safety_scores.append(0.7)
        else:
            # Public transit is generally safe
            safety_scores.append(0.8)

    return sum(safety_scores) / len(safety_scores)


def calculate_energy_efficiency(steps: List[RouteStep]) -> float:
    """Calculate energy efficiency score for a route."""
    if not steps:
        return 1.0

    efficiency_scores = []
    for step in steps:
        if step.mode == TransportMode.WALKING:
            efficiency_scores.append(1.0)
        elif step.mode == TransportMode.BIKING:
            efficiency_scores.append(0.9)
        elif step.mode in [TransportMode.BUS, TransportMode.SKYTRAIN]:
            efficiency_scores.append(0.7)
        elif step.mode == TransportMode.SCOOTER:
            efficiency_scores.append(0.6)
        elif step.mode == TransportMode.CAR:
            efficiency_scores.append(0.3)
        else:
            efficiency_scores.append(0.5)

    return sum(efficiency_scores) / len(efficiency_scores)


def calculate_scenic_score(steps: List[RouteStep]) -> float:
    """Calculate scenic score for a route."""
    if not steps:
        return 0.5

    scenic_scores = []
    for step in steps:
        if step.mode in [TransportMode.WALKING, TransportMode.BIKING]:
            # Active modes allow for better scenery appreciation
            scenic_scores.append(0.8)
        elif step.mode == TransportMode.CAR:
            scenic_scores.append(0.4)
        else:
            scenic_scores.append(0.6)

    return sum(scenic_scores) / len(scenic_scores)

