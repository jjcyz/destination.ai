"""
Real-time data integration for route calculation.
Handles weather, traffic, transit, and other real-time data updates.
"""

import logging
from typing import Dict, Optional, List
from ..models import WeatherData, WeatherCondition

logger = logging.getLogger(__name__)


def calculate_weather_penalty(weather: WeatherData) -> float:
    """Calculate weather penalty for different transport modes."""
    base_penalty = 1.0

    if weather.condition == WeatherCondition.RAIN:
        base_penalty = 1.3
    elif weather.condition == WeatherCondition.SNOW:
        base_penalty = 1.5
    elif weather.condition == WeatherCondition.FOG:
        base_penalty = 1.2
    elif weather.condition == WeatherCondition.EXTREME:
        base_penalty = 2.0

    # Adjust for wind speed
    if weather.wind_speed > 30:  # km/h
        base_penalty *= 1.2

    return base_penalty


async def update_graph_with_real_time_data(graph_builder, real_time_data: Dict):
    """Update graph edges with real-time data."""
    try:
        # Update weather penalties
        weather = real_time_data.get("weather")
        if weather:
            weather_penalty = calculate_weather_penalty(weather)
            for edge in graph_builder.edges.values():
                edge.weather_penalty = weather_penalty

        # Update traffic data
        traffic_data = real_time_data.get("traffic", [])
        for traffic in traffic_data:
            if traffic.edge_id in graph_builder.edges:
                edge = graph_builder.edges[traffic.edge_id]
                edge.current_traffic_speed = traffic.current_speed

        # Update event penalties (road closures, construction)
        road_closures = real_time_data.get("road_closures", [])
        construction = real_time_data.get("construction", [])

        # This would be implemented based on actual road closure data
        # For now, we'll use default values

    except Exception as e:
        logger.error(f"Error updating graph with real-time data: {e}")


async def get_realtime_transit_info(
    api_client,
    trip_updates: List[Dict],
    route_id: str,
    stop_identifier: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Optional[Dict]:
    """
    Get real-time transit information for a route and stop.

    Args:
        api_client: API client manager
        trip_updates: Parsed GTFS-RT trip updates
        route_id: Route ID (e.g., "6641" for route 99)
        stop_identifier: Stop ID or stop name
        lat: Optional latitude for location-based bay selection
        lng: Optional longitude for location-based bay selection

    Returns:
        Dictionary with real-time arrival info or None
    """
    if not trip_updates:
        return None

    # Use GTFS parser to find matching stop arrival info
    from ..gtfs_parser import GTFSRTParser

    # Try route-based stop selection if GTFS static feed available
    if api_client.translink.gtfs_static and lat is not None and lng is not None:
        # Ensure GTFS static feed is loaded (non-blocking)
        await api_client.translink.ensure_gtfs_loaded()
        # Use route-based selection with location
        route_stop_id = api_client.translink.gtfs_static.get_route_stops_at_location(
            route_id,
            stop_identifier,
            lat,
            lng
        )
        if route_stop_id:
            stop_identifier = route_stop_id

    # Try with stop_id, using route-based selection
    arrival_info = GTFSRTParser.get_stop_arrival_time(
        trip_updates,
        route_id,
        stop_identifier
    )

    return arrival_info

