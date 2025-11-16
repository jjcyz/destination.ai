"""
GTFS Static Feed Parser for TransLink.

Parses GTFS static feed files (stops.txt, routes.txt, etc.) to create
mappings between stop names and stop IDs, route names and route IDs, etc.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GTFSStop:
    """GTFS stop information."""
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lng: float
    stop_code: Optional[str] = None
    location_type: int = 0  # 0 = stop, 1 = station
    parent_station: Optional[str] = None


@dataclass
class GTFSRoute:
    """GTFS route information."""
    route_id: str
    route_short_name: str
    route_long_name: str
    route_type: int  # 0=Tram, 1=Subway, 3=Bus, etc.


class GTFSStaticParser:
    """Parser for GTFS static feed files."""

    def __init__(self, gtfs_path: Optional[Path] = None):
        """
        Initialize GTFS static parser.

        Args:
            gtfs_path: Path to directory containing GTFS files (stops.txt, routes.txt, etc.)
                      If None, will look for 'gtfs' directory in project root
        """
        if gtfs_path is None:
            # Default to 'gtfs' directory in project root
            project_root = Path(__file__).parent.parent.parent
            gtfs_path = project_root / "gtfs"

        self.gtfs_path = Path(gtfs_path)
        self.stops: Dict[str, GTFSStop] = {}
        self.stops_by_name: Dict[str, List[GTFSStop]] = {}
        self.routes: Dict[str, GTFSRoute] = {}
        self.routes_by_short_name: Dict[str, List[GTFSRoute]] = {}

        # Route to stop mapping (which bay serves which route)
        self.route_to_stops: Dict[str, List[str]] = {}  # route_id -> [stop_ids]
        self.trips: Dict[str, Dict] = {}  # trip_id -> {route_id, ...}

        self._loaded = False

    def load(self) -> bool:
        """
        Load GTFS static feed files.

        Returns:
            True if loaded successfully, False otherwise
        """
        if self._loaded:
            return True

        if not self.gtfs_path.exists():
            logger.warning(f"GTFS directory not found: {self.gtfs_path}")
            logger.info("To use GTFS static feed:")
            logger.info("1. Download TransLink GTFS feed from: https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources")
            logger.info(f"2. Extract to: {self.gtfs_path}")
            return False

        try:
            # Load stops.txt
            stops_file = self.gtfs_path / "stops.txt"
            if stops_file.exists():
                self._load_stops(stops_file)
                logger.info(f"Loaded {len(self.stops)} stops from GTFS static feed")
            else:
                logger.warning(f"stops.txt not found in {self.gtfs_path}")

            # Load routes.txt
            routes_file = self.gtfs_path / "routes.txt"
            if routes_file.exists():
                self._load_routes(routes_file)
                logger.info(f"Loaded {len(self.routes)} routes from GTFS static feed")
            else:
                logger.warning(f"routes.txt not found in {self.gtfs_path}")

            # Load trips.txt (for route → trip mapping)
            trips_file = self.gtfs_path / "trips.txt"
            if trips_file.exists():
                self._load_trips(trips_file)
                logger.info(f"Loaded {len(self.trips)} trips from GTFS static feed")
            else:
                logger.warning(f"trips.txt not found in {self.gtfs_path}")

            # Load stop_times.txt (for trip → stop mapping)
            stop_times_file = self.gtfs_path / "stop_times.txt"
            if stop_times_file.exists():
                self._load_stop_times(stop_times_file)
                logger.info(f"Built route-to-stop mapping for {len(self.route_to_stops)} routes")
            else:
                logger.warning(f"stop_times.txt not found in {self.gtfs_path}")

            self._loaded = True
            return True

        except Exception as e:
            logger.error(f"Error loading GTFS static feed: {e}")
            return False

    def _load_stops(self, stops_file: Path) -> None:
        """Load stops from stops.txt."""
        with open(stops_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    stop = GTFSStop(
                        stop_id=row.get('stop_id', '').strip(),
                        stop_name=row.get('stop_name', '').strip(),
                        stop_lat=float(row.get('stop_lat', 0)),
                        stop_lng=float(row.get('stop_lon', 0)),  # Note: GTFS uses 'stop_lon' not 'stop_lng'
                        stop_code=row.get('stop_code', '').strip() or None,
                        location_type=int(row.get('location_type', 0)),
                        parent_station=row.get('parent_station', '').strip() or None,
                    )

                    if stop.stop_id:
                        self.stops[stop.stop_id] = stop

                        # Index by name (multiple stops can have same name)
                        stop_name_lower = stop.stop_name.lower()
                        if stop_name_lower not in self.stops_by_name:
                            self.stops_by_name[stop_name_lower] = []
                        self.stops_by_name[stop_name_lower].append(stop)

                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid stop row: {e}")
                    continue

    def _load_routes(self, routes_file: Path) -> None:
        """Load routes from routes.txt."""
        with open(routes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    route_short_name = row.get('route_short_name', '').strip()
                    route_long_name = row.get('route_long_name', '').strip()

                    route = GTFSRoute(
                        route_id=row.get('route_id', '').strip(),
                        route_short_name=route_short_name,
                        route_long_name=route_long_name,
                        route_type=int(row.get('route_type', 3)),  # Default to bus
                    )

                    if route.route_id:
                        self.routes[route.route_id] = route

                        # Index by short name (if available)
                        if route_short_name:
                            if route_short_name not in self.routes_by_short_name:
                                self.routes_by_short_name[route_short_name] = []
                            self.routes_by_short_name[route_short_name].append(route)

                        # Also index by long name for routes without short names (e.g., "Canada Line")
                        # Extract key words from long name for matching
                        if not route_short_name and route_long_name:
                            # For routes like "Canada Line", index by key words
                            long_name_lower = route_long_name.lower()
                            # Index by full long name
                            if long_name_lower not in self.routes_by_short_name:
                                self.routes_by_short_name[long_name_lower] = []
                            self.routes_by_short_name[long_name_lower].append(route)

                            # Also index by individual words (e.g., "canada", "line")
                            words = long_name_lower.split()
                            for word in words:
                                if len(word) > 2:  # Skip short words
                                    if word not in self.routes_by_short_name:
                                        self.routes_by_short_name[word] = []
                                    self.routes_by_short_name[word].append(route)

                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid route row: {e}")
                    continue

    def _load_trips(self, trips_file: Path) -> None:
        """Load trips from trips.txt."""
        with open(trips_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    trip_id = row.get('trip_id', '').strip()
                    route_id = row.get('route_id', '').strip()

                    if trip_id and route_id:
                        self.trips[trip_id] = {
                            'route_id': route_id,
                            'service_id': row.get('service_id', '').strip(),
                            'trip_headsign': row.get('trip_headsign', '').strip(),
                            'direction_id': row.get('direction_id', '').strip(),
                        }

                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid trip row: {e}")
                    continue

    def _load_stop_times(self, stop_times_file: Path) -> None:
        """Load stop_times.txt and build route → stop mapping."""
        # Build trip_id → route_id mapping
        trip_to_route = {trip_id: trip_data['route_id']
                        for trip_id, trip_data in self.trips.items()}

        # Build route_id → set of stop_ids mapping
        route_stops: Dict[str, set] = {}

        with open(stop_times_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    trip_id = row.get('trip_id', '').strip()
                    stop_id = row.get('stop_id', '').strip()

                    if trip_id and stop_id:
                        # Get route_id for this trip
                        route_id = trip_to_route.get(trip_id)
                        if route_id:
                            if route_id not in route_stops:
                                route_stops[route_id] = set()
                            route_stops[route_id].add(stop_id)

                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid stop_times row: {e}")
                    continue

        # Convert sets to lists
        self.route_to_stops = {route_id: list(stop_ids)
                              for route_id, stop_ids in route_stops.items()}

    def get_stop_id_by_name(
        self,
        stop_name: str,
        route_id: Optional[str] = None,
        prefer_station: bool = True
    ) -> Optional[str]:
        """
        Get stop ID by stop name (exact match, then partial match).

        For stops with multiple bays (e.g., "UBC Exchange @ Bay 9"), this will:
        - Return the first match if no route_id provided
        - Try to match by route if route_id provided (requires trips.txt)
        - Prefer station stops (location_type=1) if prefer_station=True

        Args:
            stop_name: Stop name (e.g., "Commercial-Broadway Station" or "UBC Exchange")
            route_id: Optional route ID to help select the correct bay
            prefer_station: If True, prefer station stops over bay stops

        Returns:
            Stop ID if found, None otherwise
        """
        if not self._loaded:
            self.load()

        stop_name_lower = stop_name.lower().strip()

        # Try exact match first
        stops = self.stops_by_name.get(stop_name_lower)
        if stops:
            return self._select_best_stop(stops, route_id, prefer_station)

        # Try partial match (e.g., "UBC Exchange" matches "UBC Exchange @ Bay 9")
        # Find stops where the search name is a prefix or contained in the stop name
        matching_stops = []
        for name, stop_list in self.stops_by_name.items():
            # Check if search name is contained in stop name or vice versa
            if stop_name_lower in name or name.startswith(stop_name_lower):
                # Prefer exact prefix matches
                if name.startswith(stop_name_lower):
                    matching_stops.extend(stop_list)

        if matching_stops:
            return self._select_best_stop(matching_stops, route_id, prefer_station)

        return None

    def _select_best_stop(
        self,
        stops: List['GTFSStop'],
        route_id: Optional[str] = None,
        prefer_station: bool = True
    ) -> Optional[str]:
        """
        Select the best stop from a list of matching stops.

        Priority:
        1. Station stops (location_type=1) if prefer_station=True
        2. Stops matching the route (if route_id provided and route_to_stops mapping available)
        3. First stop in list

        Args:
            stops: List of matching stops
            route_id: Optional route ID to filter by route
            prefer_station: Prefer station stops over bay stops

        Returns:
            Best stop ID, or None if no stops provided
        """
        if not stops:
            return None

        # If only one stop, return it
        if len(stops) == 1:
            return stops[0].stop_id

        # Filter by station preference
        if prefer_station:
            station_stops = [s for s in stops if s.location_type == 1]
            if station_stops:
                stops = station_stops

        # If route_id provided, try to find stop that serves this route
        if route_id and self.route_to_stops:
            # Get all stops that serve this route
            route_stop_ids = set(self.route_to_stops.get(route_id, []))

            if route_stop_ids:
                # Find stops that match both the name AND serve this route
                matching_route_stops = [
                    s for s in stops
                    if s.stop_id in route_stop_ids
                ]

                if matching_route_stops:
                    logger.debug(
                        f"Found {len(matching_route_stops)} stops matching route {route_id} "
                        f"out of {len(stops)} total matches"
                    )
                    return matching_route_stops[0].stop_id

        # Fallback: return first stop
        return stops[0].stop_id

    def get_stops_for_route(self, route_id: str) -> List[str]:
        """
        Get all stop IDs that serve a specific route.

        Args:
            route_id: GTFS route ID

        Returns:
            List of stop IDs that serve this route
        """
        if not self._loaded:
            self.load()

        return self.route_to_stops.get(route_id, [])

    def get_route_stops_at_location(
        self,
        route_id: str,
        stop_name: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> Optional[str]:
        """
        Get the stop ID for a route at a specific location, considering:
        1. Route-specific stops (which bay serves this route)
        2. Location proximity (closest bay to coordinates)
        3. Stop name matching

        Args:
            route_id: GTFS route ID
            stop_name: Stop name (e.g., "UBC Exchange")
            lat: Optional latitude for location-based selection
            lng: Optional longitude for location-based selection

        Returns:
            Best matching stop ID, or None
        """
        if not self._loaded:
            self.load()

        # Get all stops matching the name
        matching_stops = self.get_all_stops_by_name(stop_name)
        if not matching_stops:
            return None

        # Get stops that serve this route
        route_stop_ids = set(self.get_stops_for_route(route_id))

        if route_stop_ids:
            # Filter to stops that both match the name AND serve this route
            route_matching_stops = [
                s for s in matching_stops
                if s.stop_id in route_stop_ids
            ]

            if route_matching_stops:
                # If location provided, find closest
                if lat is not None and lng is not None:
                    return self._find_closest_stop(route_matching_stops, lat, lng)
                return route_matching_stops[0].stop_id

        # Fallback: if no route match, use location if provided
        if lat is not None and lng is not None:
            return self._find_closest_stop(matching_stops, lat, lng)

        # Final fallback: first matching stop
        return matching_stops[0].stop_id

    def _find_closest_stop(
        self,
        stops: List['GTFSStop'],
        lat: float,
        lng: float
    ) -> Optional[str]:
        """
        Find the closest stop to given coordinates.

        Args:
            stops: List of stops to choose from
            lat: Latitude
            lng: Longitude

        Returns:
            Stop ID of closest stop, or None
        """
        if not stops:
            return None

        from math import sqrt

        closest_stop = None
        min_distance = float('inf')

        for stop in stops:
            # Calculate distance in meters
            lat_diff = stop.stop_lat - lat
            lng_diff = stop.stop_lng - lng
            # Approximate meters (1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat))
            distance_m = sqrt(
                (lat_diff * 111000) ** 2 +
                (lng_diff * 111000 * abs(lat / 90)) ** 2
            )

            if distance_m < min_distance:
                min_distance = distance_m
                closest_stop = stop

        return closest_stop.stop_id if closest_stop else None

    def get_all_stops_by_name(self, stop_name: str) -> List['GTFSStop']:
        """
        Get all stops matching a name (useful for multi-bay stops).

        Args:
            stop_name: Stop name (e.g., "UBC Exchange")

        Returns:
            List of all matching stops
        """
        if not self._loaded:
            self.load()

        stop_name_lower = stop_name.lower().strip()

        # Try exact match first
        stops = self.stops_by_name.get(stop_name_lower)
        if stops:
            return stops

        # Try partial match
        matching_stops = []
        for name, stop_list in self.stops_by_name.items():
            if stop_name_lower in name or name.startswith(stop_name_lower):
                if name.startswith(stop_name_lower):
                    matching_stops.extend(stop_list)

        return matching_stops

    def get_stop_ids_by_name_fuzzy(self, stop_name: str) -> List[str]:
        """
        Get stop IDs by name (fuzzy match - partial name matching).

        Args:
            stop_name: Partial stop name (e.g., "Commercial")

        Returns:
            List of stop IDs matching the name
        """
        if not self._loaded:
            self.load()

        stop_name_lower = stop_name.lower().strip()
        matching_stops = []

        for name, stops in self.stops_by_name.items():
            if stop_name_lower in name or name in stop_name_lower:
                matching_stops.extend([s.stop_id for s in stops])

        return matching_stops

    def get_stop_by_id(self, stop_id: str) -> Optional[GTFSStop]:
        """Get stop information by stop ID."""
        if not self._loaded:
            self.load()

        return self.stops.get(stop_id)

    def get_route_id_by_short_name(self, short_name: str) -> Optional[str]:
        """
        Get route ID by route short name (with normalization).

        Args:
            short_name: Route short name (e.g., "99", "099", "4", "004")

        Returns:
            Route ID if found, None otherwise
        """
        if not self._loaded:
            self.load()

        # Try exact match first
        routes = self.routes_by_short_name.get(short_name)
        if routes:
            return routes[0].route_id

        # Try normalized match (e.g., "99" matches "099", "4" matches "004")
        # Remove leading zeros for comparison
        normalized = short_name.lstrip('0')
        if normalized != short_name:
            routes = self.routes_by_short_name.get(normalized)
            if routes:
                return routes[0].route_id

        # Try with leading zeros (e.g., "99" -> "099", "4" -> "004")
        if short_name.isdigit():
            padded = short_name.zfill(3)  # "99" -> "099", "4" -> "004"
            routes = self.routes_by_short_name.get(padded)
            if routes:
                return routes[0].route_id

        # Try case-insensitive match (for route names like "Canada Line")
        short_name_lower = short_name.lower()
        routes = self.routes_by_short_name.get(short_name_lower)
        if routes:
            return routes[0].route_id

        return None

    def find_stop_by_location(
        self,
        lat: float,
        lng: float,
        radius_meters: float = 100.0
    ) -> Optional[GTFSStop]:
        """
        Find stop by location (nearest stop within radius).

        Args:
            lat: Latitude
            lng: Longitude
            radius_meters: Search radius in meters

        Returns:
            Nearest GTFSStop within radius, or None
        """
        if not self._loaded:
            self.load()

        from math import sqrt

        nearest_stop = None
        min_distance = float('inf')

        for stop in self.stops.values():
            # Simple distance calculation (for small distances)
            lat_diff = stop.stop_lat - lat
            lng_diff = stop.stop_lng - lng
            # Approximate meters (1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat))
            distance_m = sqrt(
                (lat_diff * 111000) ** 2 +
                (lng_diff * 111000 * abs(lat / 90)) ** 2
            )

            if distance_m <= radius_meters and distance_m < min_distance:
                min_distance = distance_m
                nearest_stop = stop

        return nearest_stop

    def get_all_stops(self) -> List[GTFSStop]:
        """Get all stops."""
        if not self._loaded:
            self.load()

        return list(self.stops.values())

    def get_all_routes(self) -> List[GTFSRoute]:
        """Get all routes."""
        if not self._loaded:
            self.load()

        return list(self.routes.values())

