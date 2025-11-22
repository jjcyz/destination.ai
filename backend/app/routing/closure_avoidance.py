"""
Road closure and construction zone avoidance for routes.
Filters routes through closures and injects waypoints to route around them.
"""

import logging
from typing import List, Dict, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from ..models import Route, RouteStep, Point

logger = logging.getLogger(__name__)

# Distance threshold for considering a route step "near" a closure (in meters)
CLOSURE_PROXIMITY_THRESHOLD = 50  # 50 meters


def haversine_distance(point1: Point, point2: Point) -> float:
    """
    Calculate the great circle distance between two points on Earth (in meters).

    Args:
        point1: First point (lat, lng)
        point2: Second point (lat, lng)

    Returns:
        Distance in meters
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(point1.lat), radians(point1.lng)
    lat2, lon2 = radians(point2.lat), radians(point2.lng)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # Radius of Earth in meters
    r = 6371000

    return c * r


def point_in_bounds(point: Point, bounds: Dict[str, float]) -> bool:
    """
    Check if a point is within given bounds.

    Args:
        point: Point to check
        bounds: Dictionary with 'north', 'south', 'east', 'west' keys

    Returns:
        True if point is within bounds
    """
    return (bounds['south'] <= point.lat <= bounds['north'] and
            bounds['west'] <= point.lng <= bounds['east'])


def extract_closure_location(closure: Dict) -> Optional[Point]:
    """
    Extract location from a closure/construction record.
    Handles various data formats from Vancouver Open Data.

    Args:
        closure: Closure/construction record

    Returns:
        Point if location can be extracted, None otherwise
    """
    # Vancouver Open Data format: geo_point_2d with lat/lon
    if 'geo_point_2d' in closure:
        geo_point = closure['geo_point_2d']
        if isinstance(geo_point, dict):
            if 'lat' in geo_point and 'lon' in geo_point:
                try:
                    return Point(lat=float(geo_point['lat']), lng=float(geo_point['lon']))
                except (ValueError, TypeError):
                    pass

    # Try various other possible field names
    if 'latitude' in closure and 'longitude' in closure:
        try:
            return Point(lat=float(closure['latitude']), lng=float(closure['longitude']))
        except (ValueError, TypeError):
            pass

    if 'lat' in closure and 'lng' in closure:
        try:
            return Point(lat=float(closure['lat']), lng=float(closure['lng']))
        except (ValueError, TypeError):
            pass

    if 'location' in closure:
        loc = closure['location']
        if isinstance(loc, dict):
            if 'latitude' in loc and 'longitude' in loc:
                try:
                    return Point(lat=float(loc['latitude']), lng=float(loc['longitude']))
                except (ValueError, TypeError):
                    pass
            if 'lat' in loc and 'lng' in loc:
                try:
                    return Point(lat=float(loc['lat']), lng=float(loc['lng']))
                except (ValueError, TypeError):
                    pass

    # Try GeoJSON geometry format (from geom field)
    if 'geom' in closure:
        geom = closure['geom']
        if isinstance(geom, dict) and 'geometry' in geom:
            geometry = geom['geometry']
            if 'coordinates' in geometry:
                coords = geometry['coordinates']
                # Handle MultiLineString format: [[[lng, lat], [lng, lat]], ...]
                # Use first coordinate of first line
                if isinstance(coords, list) and len(coords) > 0:
                    first_line = coords[0]
                    if isinstance(first_line, list) and len(first_line) > 0:
                        first_point = first_line[0]
                        if isinstance(first_point, list) and len(first_point) >= 2:
                            try:
                                # GeoJSON format is [longitude, latitude]
                                return Point(lat=float(first_point[1]), lng=float(first_point[0]))
                            except (ValueError, TypeError):
                                pass

    # Try coordinates array [lng, lat] (GeoJSON format)
    if 'coordinates' in closure:
        coords = closure['coordinates']
        if isinstance(coords, list) and len(coords) >= 2:
            try:
                # GeoJSON format is [longitude, latitude]
                return Point(lat=float(coords[1]), lng=float(coords[0]))
            except (ValueError, TypeError):
                pass

    return None


def get_closure_severity(closure: Dict) -> str:
    """
    Determine closure severity from closure data.

    Args:
        closure: Closure/construction record

    Returns:
        'major', 'minor', or 'unknown'
    """
    # Check for severity indicators in various fields
    project = closure.get('project', '').lower()
    location = closure.get('location', '').lower()
    street = closure.get('street', '').lower()
    closure_type = closure.get('closure_type', '').lower()
    status = closure.get('status', '').lower()
    description = closure.get('description', '').lower()

    # Combine all text fields for keyword search
    all_text = ' '.join([project, location, street, closure_type, status, description])

    # Major closures - full road closures, complete closures
    major_keywords = [
        'full closure', 'complete closure', 'road closed', 'bridge closed',
        'major', 'full', 'closed', 'blocked', 'no access'
    ]
    if any(keyword in all_text for keyword in major_keywords):
        return 'major'

    # Minor closures - partial closures, lane closures, construction
    minor_keywords = [
        'partial', 'lane closure', 'shoulder', 'minor', 'construction',
        'lane', 'sidewalk', 'shoulder work'
    ]
    if any(keyword in all_text for keyword in minor_keywords):
        return 'minor'

    # Default: if it's in the dataset, assume it's at least minor
    # This ensures we don't miss closures due to missing severity info
    return 'minor'  # Default to minor to be safe


def step_passes_near_closure(step: RouteStep, closure: Dict, threshold: float = CLOSURE_PROXIMITY_THRESHOLD) -> bool:
    """
    Check if a route step passes near a closure.

    Args:
        step: Route step to check
        closure: Closure/construction record
        threshold: Distance threshold in meters

    Returns:
        True if step passes near closure
    """
    closure_point = extract_closure_location(closure)
    if not closure_point:
        return False

    # Check start and end points
    start_distance = haversine_distance(step.start_point, closure_point)
    end_distance = haversine_distance(step.end_point, closure_point)

    # Check midpoint
    midpoint = Point(
        lat=(step.start_point.lat + step.end_point.lat) / 2,
        lng=(step.start_point.lng + step.end_point.lng) / 2
    )
    midpoint_distance = haversine_distance(midpoint, closure_point)

    # If any point is within threshold, consider it passing near
    return (start_distance < threshold or
            end_distance < threshold or
            midpoint_distance < threshold)


def route_passes_through_closures(route: Route, closures: List[Dict], severity_filter: Optional[str] = None) -> Tuple[bool, List[Dict]]:
    """
    Check if a route passes through any closures.

    Args:
        route: Route to check
        closures: List of closure/construction records
        severity_filter: If 'major', only check major closures

    Returns:
        Tuple of (has_closure, list of closures route passes through)
    """
    if not closures:
        return False, []

    route_closures = []

    for closure in closures:
        # Filter by severity if specified
        if severity_filter == 'major':
            if get_closure_severity(closure) != 'major':
                continue

        # Check each step in the route
        for step in route.steps:
            if step_passes_near_closure(step, closure):
                route_closures.append(closure)
                break  # Don't count same closure multiple times

    return len(route_closures) > 0, route_closures


def filter_routes_with_closures(
    routes: List[Route],
    closures: List[Dict],
    construction: List[Dict],
    filter_major_only: bool = True
) -> Tuple[List[Route], List[Route], Dict[str, List[Dict]]]:
    """
    Filter routes that pass through closures or construction zones.

    Args:
        routes: List of routes to filter
        closures: List of road closure records
        construction: List of construction zone records
        filter_major_only: If True, only filter routes through major closures

    Returns:
        Tuple of (valid_routes, filtered_routes, closures_by_route)
        where closures_by_route maps route_id -> list of closures it passes through
    """
    all_closures = closures + construction
    valid_routes = []
    filtered_routes = []
    closures_by_route = {}

    for route in routes:
        has_closure, route_closures = route_passes_through_closures(
            route,
            all_closures,
            severity_filter='major' if filter_major_only else None
        )

        if has_closure:
            filtered_routes.append(route)
            closures_by_route[route.id] = route_closures
            logger.debug(
                f"Filtered route {route.id} due to {len(route_closures)} closure(s): "
                f"{[c.get('description', 'Unknown')[:50] for c in route_closures]}"
            )
        else:
            valid_routes.append(route)

    if filtered_routes:
        logger.info(
            f"Filtered {len(filtered_routes)} routes due to closures/construction "
            f"(total closures: {len(all_closures)})"
        )

    return valid_routes, filtered_routes, closures_by_route


def calculate_avoidance_waypoints(
    origin: Point,
    destination: Point,
    closures: List[Dict],
    max_waypoints: int = 3
) -> List[Point]:
    """
    Calculate waypoints to route around closures.

    This is a simplified implementation. In production, you'd want to:
    - Use a routing graph to find actual detour paths
    - Consider road network topology
    - Avoid creating waypoints that create longer routes

    Args:
        origin: Route origin point
        destination: Route destination point
        closures: List of closures to avoid
        max_waypoints: Maximum number of waypoints to add

    Returns:
        List of waypoint points to route around closures
    """
    if not closures:
        return []

    waypoints = []

    # Simple approach: Calculate waypoints that avoid closure areas
    # For each major closure, add a waypoint that routes around it

    for closure in closures[:max_waypoints]:  # Limit to max_waypoints
        closure_point = extract_closure_location(closure)
        if not closure_point:
            continue

        # Calculate a waypoint that routes around the closure
        # Simple approach: offset perpendicular to the route direction

        # Calculate route direction vector
        route_lat_diff = destination.lat - origin.lat
        route_lng_diff = destination.lng - origin.lng

        # Calculate perpendicular offset (90 degrees rotated)
        # Scale offset based on distance from route
        offset_distance = 0.002  # ~200 meters in degrees (rough approximation)

        # Perpendicular vector (swap and negate one component)
        perp_lat = route_lng_diff * offset_distance
        perp_lng = -route_lat_diff * offset_distance

        # Create waypoint offset from closure
        waypoint = Point(
            lat=closure_point.lat + perp_lat,
            lng=closure_point.lng + perp_lng
        )

        waypoints.append(waypoint)

    return waypoints


def create_avoidance_waypoints_string(waypoints: List[Point]) -> str:
    """
    Convert waypoints to Google Maps waypoints format.

    Args:
        waypoints: List of waypoint points

    Returns:
        Waypoints string in format "lat1,lng1|lat2,lng2|..."
    """
    return "|".join([f"{wp.lat},{wp.lng}" for wp in waypoints])


def apply_closure_avoidance(
    routes: List[Route],
    closures: List[Dict],
    construction: List[Dict],
    filter_major_only: bool = True
) -> Tuple[List[Route], List[Route], Dict[str, List[Dict]]]:
    """
    Apply closure avoidance to routes.

    Args:
        routes: List of routes to process
        closures: List of road closure records
        construction: List of construction zone records
        filter_major_only: If True, only filter major closures

    Returns:
        Tuple of (valid_routes, filtered_routes, closures_by_route)
    """
    return filter_routes_with_closures(
        routes,
        closures,
        construction,
        filter_major_only=filter_major_only
    )

