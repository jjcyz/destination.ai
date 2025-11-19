"""
Google Maps route conversion utilities.
Converts Google Maps Directions API responses to our Route model.
"""

import re
import logging
from typing import Dict, Optional
from ..models import (
    Point, Route, RouteStep, RouteRequest, TransportMode, RoutePreference,
    WeatherCondition
)
from .route_utils import (
    calculate_sustainability_points,
    calculate_route_safety_score,
    calculate_energy_efficiency,
    calculate_scenic_score
)
from .realtime_integration import calculate_weather_penalty, get_realtime_transit_info

logger = logging.getLogger(__name__)


async def convert_google_route_to_route(
    google_route: Dict[str, any],
    request: RouteRequest,
    transport_mode: TransportMode,
    real_time_data: Dict,
    api_client
) -> Optional[Route]:
    """Convert Google Maps route data to our Route model."""
    try:
        steps = []
        total_distance = 0
        total_time = 0
        total_sustainability_points = 0

        # Process each leg in the route
        for leg in google_route.get("legs", []):
            leg_distance = leg.get("distance", {}).get("value", 0)  # meters
            leg_duration = leg.get("duration", {}).get("value", 0)  # seconds
            leg_duration_in_traffic = leg.get("duration_in_traffic", {}).get("value", leg_duration)

            # Process each step in the leg
            for step_idx, step in enumerate(leg.get("steps", [])):
                step_distance = step.get("distance", {}).get("value", 0)
                step_duration = step.get("duration", {}).get("value", 0)

                start_location = step.get("start_location", {})
                end_location = step.get("end_location", {})

                start_point = Point(
                    lat=start_location.get("lat", request.origin.lat),
                    lng=start_location.get("lng", request.origin.lng)
                )
                end_point = Point(
                    lat=end_location.get("lat", request.destination.lat),
                    lng=end_location.get("lng", request.destination.lng)
                )

                # Extract polyline for accurate route rendering
                step_polyline = None
                if step.get("polyline"):
                    step_polyline = step.get("polyline", {}).get("points", None)

                # Get step instructions
                instructions = step.get("html_instructions", "")
                # Remove HTML tags
                instructions = re.sub('<[^<]+?>', '', instructions)

                # Calculate sustainability points
                sustainability_points = calculate_sustainability_points(transport_mode, step_distance)

                # Apply weather penalties to walking and biking
                weather = real_time_data.get("weather")
                if weather and transport_mode in [TransportMode.WALKING, TransportMode.BIKING]:
                    weather_penalty = calculate_weather_penalty(weather)
                    # Adjust time based on weather
                    step_duration = int(step_duration * weather_penalty)

                    # Add weather info to instructions
                    if weather.condition.value != "clear":
                        weather_note = {
                            "rain": "🌧️ Rainy conditions",
                            "snow": "❄️ Snowy conditions",
                            "fog": "🌫️ Foggy conditions",
                            "extreme": "⚠️ Extreme weather"
                        }.get(weather.condition.value, "")
                        if weather_note:
                            instructions = f"{weather_note} - {instructions}"

                # Determine effort level based on distance, mode, and weather
                effort_level = _determine_effort_level(transport_mode, step_distance, weather)

                # Get elevation data if available (skip for performance - can be enabled if needed)
                slope = None
                # Note: Elevation API calls are slow, skipping for better performance

                # Check for transit details
                transit_details = await _extract_transit_details(
                    step,
                    transport_mode,
                    real_time_data,
                    api_client,
                    step_duration
                )

                route_step = RouteStep(
                    mode=transport_mode,
                    distance=step_distance,
                    estimated_time=step_duration,
                    slope=slope,
                    effort_level=effort_level,
                    instructions=instructions or f"Continue {step_distance/1000:.1f}km",
                    start_point=start_point,
                    end_point=end_point,
                    polyline=step_polyline,
                    transit_details=transit_details,
                    sustainability_points=sustainability_points
                )

                steps.append(route_step)
                total_distance += step_distance
                total_time += step_duration
                total_sustainability_points += sustainability_points

        if not steps:
            return None

        # Calculate route quality metrics
        safety_score = calculate_route_safety_score(steps)
        energy_efficiency = calculate_energy_efficiency(steps)
        scenic_score = calculate_scenic_score(steps)

        # Use first preference for the route
        preference = request.preferences[0] if request.preferences else RoutePreference.FASTEST

        route = Route(
            origin=request.origin,
            destination=request.destination,
            steps=steps,
            total_distance=total_distance,
            total_time=total_time,
            total_sustainability_points=total_sustainability_points,
            preference=preference,
            safety_score=safety_score,
            energy_efficiency=energy_efficiency,
            scenic_score=scenic_score
        )

        return route

    except Exception as e:
        logger.error(f"Error converting Google route: {e}")
        return None


def _determine_effort_level(transport_mode: TransportMode, step_distance: float, weather: Optional) -> str:
    """Determine effort level based on distance, mode, and weather."""
    effort_level = "moderate"

    if transport_mode == TransportMode.WALKING:
        if step_distance > 1000:
            effort_level = "high"
        elif step_distance < 200:
            effort_level = "low"
        # Weather increases effort for walking
        if weather and weather.condition.value in ["rain", "snow", "extreme"]:
            if effort_level == "low":
                effort_level = "moderate"
            elif effort_level == "moderate":
                effort_level = "high"
    elif transport_mode == TransportMode.BIKING:
        if step_distance > 5000:
            effort_level = "high"
        elif step_distance < 500:
            effort_level = "low"
        # Weather increases effort for biking
        if weather and weather.condition.value in ["rain", "snow", "extreme"]:
            if effort_level == "low":
                effort_level = "moderate"
            elif effort_level == "moderate":
                effort_level = "high"
        # Wind affects biking more
        if weather and weather.wind_speed > 25:  # km/h
            if effort_level == "moderate":
                effort_level = "high"

    return effort_level


async def _extract_transit_details(
    step: Dict,
    transport_mode: TransportMode,
    real_time_data: Dict,
    api_client,
    step_duration: int
) -> Optional[Dict]:
    """Extract and enrich transit details from Google Maps step."""
    if transport_mode not in [TransportMode.BUS, TransportMode.SKYTRAIN]:
        return None

    transit_step = step.get("transit_details")
    if not transit_step:
        return None

    # Extract transit information from Google Maps
    line_info = transit_step.get("line", {})
    departure_info = transit_step.get("departure_stop", {})
    arrival_info = transit_step.get("arrival_stop", {})

    # Extract basic transit information from Google Maps
    route_short_name = line_info.get("short_name", "")
    route_name = line_info.get("name", "")
    departure_stop_name = departure_info.get("name", "")
    arrival_stop_name = arrival_info.get("name", "")

    # Try to get stop IDs from Google Maps (may not always be available)
    departure_stop_id = departure_info.get("location", {}).get("place_id") or None
    arrival_stop_id = arrival_info.get("location", {}).get("place_id") or None

    transit_details = {
        "line": route_name,
        "short_name": route_short_name,
        "vehicle": line_info.get("vehicle", {}).get("name", ""),
        "vehicle_type": line_info.get("vehicle", {}).get("type", ""),
        "departure_stop": departure_stop_name,
        "departure_stop_id": departure_stop_id,
        "departure_time": transit_step.get("departure_time", {}).get("text", ""),
        "departure_time_value": transit_step.get("departure_time", {}).get("value"),
        "arrival_stop": arrival_stop_name,
        "arrival_stop_id": arrival_stop_id,
        "arrival_time": transit_step.get("arrival_time", {}).get("text", ""),
        "arrival_time_value": transit_step.get("arrival_time", {}).get("value"),
        "num_stops": transit_step.get("num_stops", 0),
        "headsign": transit_step.get("headsign", ""),
    }

    # Try to get real-time TransLink data for this route
    translink_trip_updates = real_time_data.get("translink_trip_updates", [])
    if translink_trip_updates and route_short_name:
        try:
            # Resolve route short name to route ID for better bay selection
            resolved_route_id = route_short_name
            if api_client.translink.gtfs_static:
                await api_client.translink.ensure_gtfs_loaded()
                resolved_route_id = (
                    api_client.translink.gtfs_static.get_route_id_by_short_name(route_short_name)
                    or route_short_name
                )

            # Use stop name (GTFS parser will resolve to stop ID with route-based selection)
            stop_identifier = departure_stop_id or departure_stop_name

            # Get coordinates if available for location-based selection
            departure_lat = departure_info.get("location", {}).get("lat")
            departure_lng = departure_info.get("location", {}).get("lng")

            # Get real-time arrival info for departure stop
            real_time_arrival = await get_realtime_transit_info(
                api_client,
                translink_trip_updates,
                resolved_route_id,
                stop_identifier,
                departure_lat,
                departure_lng
            )

            if real_time_arrival:
                # Update with real-time data
                transit_details["real_time_departure"] = real_time_arrival.get("actual_time")
                transit_details["delay_seconds"] = real_time_arrival.get("delay_seconds", 0)
                transit_details["delay_minutes"] = real_time_arrival.get("delay_minutes", 0)
                transit_details["is_delayed"] = real_time_arrival.get("is_delayed", False)

                # Adjust step duration based on delay
                if real_time_arrival.get("delay_seconds", 0) > 0:
                    step_duration += real_time_arrival.get("delay_seconds", 0)

                logger.debug(
                    f"Applied real-time delay for route {route_short_name}: "
                    f"{real_time_arrival.get('delay_minutes', 0)} minutes"
                )
        except Exception as e:
            logger.debug(f"Could not get real-time data for route {route_short_name}: {e}")

    # Apply weather penalty to transit time if weather is bad
    weather = real_time_data.get("weather")
    if weather and step_duration > 0:
        weather_penalty = calculate_weather_penalty(weather)
        # Transit is less affected by weather than walking/biking
        transit_weather_factor = 1.0 + (weather_penalty - 1.0) * 0.3
        step_duration = int(step_duration * transit_weather_factor)

    # Check for service alerts affecting this route
    service_alerts = real_time_data.get("translink_service_alerts", [])
    if service_alerts and route_short_name:
        route_alerts = [
            alert for alert in service_alerts
            if any(
                entity.get("route_id") == route_short_name
                for entity in alert.get("informed_entity", [])
            )
        ]
        if route_alerts:
            transit_details["service_alerts"] = [
                {
                    "header": alert.get("header_text", ""),
                    "description": alert.get("description_text", ""),
                    "effect": alert.get("effect"),
                }
                for alert in route_alerts
            ]

    return transit_details

