"""
TransLink real-time enhancements for route selection and filtering.
Implements delay-based route selection, service alert filtering, and alternative route suggestions.
"""

import logging
from typing import List, Dict, Optional, Tuple
from ..models import Route, RouteStep, TransportMode

logger = logging.getLogger(__name__)


def get_route_max_delay(route: Route) -> int:
    """
    Get the maximum delay (in minutes) across all transit steps in a route.

    Args:
        route: Route to analyze

    Returns:
        Maximum delay in minutes, or 0 if no delays
    """
    max_delay = 0
    for step in route.steps:
        if step.transit_details:
            delay_minutes = step.transit_details.get("delay_minutes", 0)
            max_delay = max(max_delay, delay_minutes)
    return max_delay


def get_route_total_delay(route: Route) -> int:
    """
    Get the total delay (in minutes) across all transit steps in a route.

    Args:
        route: Route to analyze

    Returns:
        Total delay in minutes
    """
    total_delay = 0
    for step in route.steps:
        if step.transit_details:
            delay_minutes = step.transit_details.get("delay_minutes", 0)
            total_delay += delay_minutes
    return total_delay


def has_service_alerts(route: Route) -> bool:
    """
    Check if a route is affected by TransLink service alerts.

    Args:
        route: Route to check

    Returns:
        True if route has service alerts, False otherwise
    """
    for step in route.steps:
        if step.transit_details:
            service_alerts = step.transit_details.get("service_alerts", [])
            if service_alerts:
                # Check if any alert has a significant effect
                for alert in service_alerts:
                    effect = alert.get("effect", "").upper()
                    # Filter out routes with major disruptions
                    if effect in ["NO_SERVICE", "REDUCED_SERVICE", "SIGNIFICANT_DELAYS"]:
                        return True
    return False


def filter_routes_with_service_alerts(routes: List[Route]) -> Tuple[List[Route], List[Route]]:
    """
    Filter routes affected by service alerts.

    Args:
        routes: List of routes to filter

    Returns:
        Tuple of (valid_routes, filtered_routes)
    """
    valid_routes = []
    filtered_routes = []

    for route in routes:
        if has_service_alerts(route):
            filtered_routes.append(route)
            logger.debug(f"Filtered route {route.id} due to service alerts")
        else:
            valid_routes.append(route)

    if filtered_routes:
        logger.info(f"Filtered {len(filtered_routes)} routes due to service alerts")

    return valid_routes, filtered_routes


def sort_routes_by_delay(routes: List[Route], prefer_on_time: bool = True) -> List[Route]:
    """
    Sort routes by delay, preferring on-time routes.

    Args:
        routes: List of routes to sort
        prefer_on_time: If True, prefer routes with minimal delays

    Returns:
        Sorted list of routes
    """
    def delay_score(route: Route) -> Tuple[int, int]:
        """Return (max_delay, total_delay) for sorting."""
        max_delay = get_route_max_delay(route)
        total_delay = get_route_total_delay(route)
        return (max_delay, total_delay)

    return sorted(routes, key=delay_score)


def filter_routes_by_delay_threshold(
    routes: List[Route],
    max_delay_minutes: int = 10
) -> Tuple[List[Route], List[Route]]:
    """
    Filter routes that exceed delay threshold.

    Args:
        routes: List of routes to filter
        max_delay_minutes: Maximum acceptable delay in minutes

    Returns:
        Tuple of (valid_routes, filtered_routes)
    """
    valid_routes = []
    filtered_routes = []

    for route in routes:
        max_delay = get_route_max_delay(route)
        if max_delay > max_delay_minutes:
            filtered_routes.append(route)
            logger.debug(f"Filtered route {route.id} due to delay ({max_delay}min > {max_delay_minutes}min)")
        else:
            valid_routes.append(route)

    if filtered_routes:
        logger.info(f"Filtered {len(filtered_routes)} routes due to delays exceeding {max_delay_minutes} minutes")

    return valid_routes, filtered_routes


def enhance_route_scoring_with_delays(route: Route) -> float:
    """
    Calculate a delay penalty score for route ranking.
    Lower score = better route (less delay).

    Args:
        route: Route to score

    Returns:
        Delay penalty score (lower is better)
    """
    max_delay = get_route_max_delay(route)
    total_delay = get_route_total_delay(route)

    # Penalty increases exponentially with delay
    # No delay = 0 penalty, 5min delay = 5 penalty, 10min delay = 20 penalty
    if max_delay == 0:
        penalty = 0
    elif max_delay <= 5:
        penalty = max_delay
    else:
        # Exponential penalty for delays > 5 minutes
        penalty = 5 + (max_delay - 5) * 3

    # Add small penalty for total delay across all steps
    penalty += total_delay * 0.1

    return penalty


def find_alternative_transit_routes(
    delayed_route: Route,
    all_routes: List[Route],
    delay_threshold: int = 10
) -> List[Route]:
    """
    Find alternative transit routes when a route is significantly delayed.

    Args:
        delayed_route: The route that is delayed
        all_routes: All available routes
        delay_threshold: Delay threshold in minutes to trigger alternative search

    Returns:
        List of alternative routes (different transit routes or modes)
    """
    max_delay = get_route_max_delay(delayed_route)

    if max_delay < delay_threshold:
        return []  # Not delayed enough to need alternatives

    alternatives = []

    # Get transit routes from the delayed route
    delayed_transit_routes = set()
    for step in delayed_route.steps:
        if step.transit_details:
            route_short_name = step.transit_details.get("short_name", "")
            if route_short_name:
                delayed_transit_routes.add(route_short_name)

    # Find routes that:
    # 1. Don't use the same delayed transit routes
    # 2. Have minimal delays
    # 3. Are transit routes (to provide alternatives)
    for route in all_routes:
        if route.id == delayed_route.id:
            continue

        # Check if route uses different transit routes
        route_transit_routes = set()
        for step in route.steps:
            if step.transit_details:
                route_short_name = step.transit_details.get("short_name", "")
                if route_short_name:
                    route_transit_routes.add(route_short_name)

        # If route uses different transit routes and has minimal delay
        if route_transit_routes and not route_transit_routes.intersection(delayed_transit_routes):
            route_max_delay = get_route_max_delay(route)
            if route_max_delay < delay_threshold:
                alternatives.append(route)

    # Sort alternatives by delay
    alternatives = sort_routes_by_delay(alternatives)

    logger.info(
        f"Found {len(alternatives)} alternative routes for delayed route "
        f"(delay: {max_delay}min, threshold: {delay_threshold}min)"
    )

    return alternatives[:3]  # Return top 3 alternatives


def apply_translink_enhancements(
    routes: List[Route],
    filter_service_alerts: bool = True,
    filter_high_delays: bool = True,
    delay_threshold: int = 10,
    prefer_on_time: bool = True
) -> Tuple[List[Route], List[Route], Dict[str, List[Route]]]:
    """
    Apply all TransLink enhancements to route list.

    Args:
        routes: List of routes to enhance
        filter_service_alerts: Whether to filter routes with service alerts
        filter_high_delays: Whether to filter routes with high delays
        delay_threshold: Maximum acceptable delay in minutes
        prefer_on_time: Whether to prefer on-time routes

    Returns:
        Tuple of (enhanced_routes, filtered_routes, alternatives_by_route)
        where alternatives_by_route maps route_id -> list of alternative routes
    """
    enhanced_routes = routes.copy()
    filtered_routes = []
    alternatives_by_route = {}

    # Step 1: Filter routes with service alerts
    if filter_service_alerts:
        enhanced_routes, service_alert_routes = filter_routes_with_service_alerts(enhanced_routes)
        filtered_routes.extend(service_alert_routes)

    # Step 2: Filter routes with high delays
    if filter_high_delays:
        enhanced_routes, high_delay_routes = filter_routes_by_delay_threshold(
            enhanced_routes,
            delay_threshold
        )
        filtered_routes.extend(high_delay_routes)

        # Find alternatives for filtered routes
        for delayed_route in high_delay_routes:
            alternatives = find_alternative_transit_routes(
                delayed_route,
                routes,  # Search in all original routes
                delay_threshold
            )
            if alternatives:
                alternatives_by_route[delayed_route.id] = alternatives

    # Step 3: Sort remaining routes by delay (prefer on-time)
    if prefer_on_time:
        enhanced_routes = sort_routes_by_delay(enhanced_routes, prefer_on_time=True)

    logger.info(
        f"TransLink enhancements: {len(enhanced_routes)} routes remaining "
        f"(filtered {len(filtered_routes)}, found {len(alternatives_by_route)} alternatives)"
    )

    return enhanced_routes, filtered_routes, alternatives_by_route

