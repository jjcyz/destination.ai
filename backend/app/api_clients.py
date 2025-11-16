"""
API clients for external services.
Handles communication with Google Maps, TransLink, Lime, OpenWeatherMap, and Vancouver Open Data.
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from .models import (
    Point, WeatherData, WeatherCondition, TrafficData,
    TransitData, BikeScooterData, TransportMode
)
from .config import settings
from .gtfs_parser import GTFSRTParser
from .gtfs_static import GTFSStaticParser

logger = logging.getLogger(__name__)


class GoogleMapsClient:
    """Client for Google Maps API services."""

    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.base_url = settings.google_maps_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_elevation(self, points: List[Point]) -> List[float]:
        """Get elevation data for a list of points."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return [0.0] * len(points)

        try:
            # Convert points to string format
            locations = "|".join([f"{p.lat},{p.lng}" for p in points])

            url = f"{self.base_url}/elevation/json"
            params = {
                "locations": locations,
                "key": self.api_key
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "OK":
                return [result["elevation"] for result in data.get("results", [])]
            else:
                logger.error(f"Google Elevation API error: {data.get('status')}")
                return [0.0] * len(points)

        except Exception as e:
            logger.error(f"Error fetching elevation data: {e}")
            return [0.0] * len(points)

    async def get_traffic_data(self, origin: Point, destination: Point) -> List[TrafficData]:
        """Get traffic data for a route."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return []

        try:
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": f"{origin.lat},{origin.lng}",
                "destination": f"{destination.lat},{destination.lng}",
                "departure_time": "now",
                "traffic_model": "best_guess",
                "key": self.api_key
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            traffic_data = []

            if data.get("status") == "OK" and data.get("routes"):
                route = data["routes"][0]
                for leg in route.get("legs", []):
                    for step in leg.get("steps", []):
                        # Extract traffic information from step
                        duration = step.get("duration", {}).get("value", 0)
                        duration_in_traffic = step.get("duration_in_traffic", {}).get("value", duration)

                        # Calculate congestion level
                        if duration > 0:
                            congestion = max(0, (duration_in_traffic - duration) / duration)
                        else:
                            congestion = 0

                        traffic_data.append(TrafficData(
                            edge_id=f"google_{step.get('start_location', {}).get('lat')}_{step.get('start_location', {}).get('lng')}",
                            current_speed=step.get("distance", {}).get("value", 0) / max(duration_in_traffic, 1) * 3.6,  # m/s to km/h
                            free_flow_speed=step.get("distance", {}).get("value", 0) / max(duration, 1) * 3.6,
                            congestion_level=min(1.0, congestion)
                        ))

            return traffic_data

        except Exception as e:
            logger.error(f"Error fetching traffic data: {e}")
            return []

    async def get_directions(
        self,
        origin: Point,
        destination: Point,
        mode: str = "driving",
        alternatives: bool = True,
        avoid: Optional[List[str]] = None,
        departure_time: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get directions from Google Maps Directions API.

        Args:
            origin: Starting point
            destination: Ending point
            mode: Travel mode (driving, walking, bicycling, transit)
            alternatives: Whether to return alternative routes
            avoid: List of features to avoid (tolls, highways, ferries, indoor)
            departure_time: Departure time (Unix timestamp or 'now')

        Returns:
            Directions response dictionary or None
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None

        try:
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": f"{origin.lat},{origin.lng}",
                "destination": f"{destination.lat},{destination.lng}",
                "mode": mode,
                "alternatives": "true" if alternatives else "false",
                "key": self.api_key
            }

            if avoid:
                params["avoid"] = "|".join(avoid)

            if departure_time:
                params["departure_time"] = departure_time
            else:
                params["departure_time"] = "now"
                params["traffic_model"] = "best_guess"

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "OK":
                return data

            logger.error(f"Google Directions API error: {data.get('status')} - {data.get('error_message', '')}")
            return None

        except Exception as e:
            logger.error(f"Error fetching directions: {e}")
            return None

    async def geocode(self, address: str) -> Optional[Point]:
        """Geocode an address to coordinates."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None

        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "address": address,
                "key": self.api_key
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "OK" and data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return Point(lat=location["lat"], lng=location["lng"])

            return None

        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return None


class TransLinkClient:
    """Client for TransLink (Vancouver public transit) GTFS-RT V3 API.

    Note: The old RTTI API was retired on December 3, 2024.
    This client now uses the GTFS Realtime V3 API.
    """

    def __init__(self):
        self.api_key = settings.translink_api_key
        self.base_url = settings.translink_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.parser = GTFSRTParser()
        self.gtfs_static = GTFSStaticParser()  # For stop name to ID mapping

        # Pre-load GTFS static feed in background to avoid blocking
        # This will be loaded lazily on first use, but we can trigger it early
        self._gtfs_loading_started = False
        self._gtfs_loading_lock = asyncio.Lock()

        # Cache for parsed GTFS-RT data (refresh every 30 seconds)
        self._trip_updates_cache: Optional[List[Dict]] = None
        self._vehicle_positions_cache: Optional[List[Dict]] = None
        self._service_alerts_cache: Optional[List[Dict]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 30  # seconds

    async def ensure_gtfs_loaded(self):
        """Ensure GTFS static feed is loaded (non-blocking)."""
        if not self.gtfs_static:
            return

        # Check if already loaded (fast path)
        if self.gtfs_static._loaded:
            return

        # Use lock to prevent concurrent loading
        async with self._gtfs_loading_lock:
            # Double-check after acquiring lock
            if self.gtfs_static._loaded:
                return

            # Load in thread pool to avoid blocking event loop
            if not self._gtfs_loading_started:
                self._gtfs_loading_started = True
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.gtfs_static.load)

    async def get_trip_updates(self) -> bytes:
        """Get GTFS Realtime trip updates feed (Protocol Buffer format)."""
        if not self.api_key:
            logger.warning("TransLink API key not configured")
            return b""

        try:
            url = f"{self.base_url}/gtfsrealtime"
            params = {"apikey": self.api_key}

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            return response.content  # Return raw bytes (Protocol Buffer format)

        except Exception as e:
            logger.error(f"Error fetching TransLink trip updates: {e}")
            return b""

    async def get_parsed_trip_updates(self) -> List[Dict]:
        """
        Get parsed GTFS-RT trip updates.

        Returns:
            List of parsed trip update dictionaries
        """
        # Check cache
        if self._trip_updates_cache and self._cache_timestamp:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl:
                return self._trip_updates_cache

        # Fetch and parse
        feed_data = await self.get_trip_updates()
        if not feed_data:
            return []

        self._trip_updates_cache = self.parser.parse_trip_updates(feed_data)
        self._cache_timestamp = datetime.now()

        return self._trip_updates_cache

    async def get_parsed_vehicle_positions(self) -> List[Dict]:
        """
        Get parsed GTFS-RT vehicle positions.

        Returns:
            List of parsed vehicle position dictionaries
        """
        # Check cache
        if self._vehicle_positions_cache and self._cache_timestamp:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl:
                return self._vehicle_positions_cache

        # Fetch and parse
        feed_data = await self.get_position_updates()
        if not feed_data:
            return []

        self._vehicle_positions_cache = self.parser.parse_vehicle_positions(feed_data)
        self._cache_timestamp = datetime.now()

        return self._vehicle_positions_cache

    async def get_parsed_service_alerts(self) -> List[Dict]:
        """
        Get parsed GTFS-RT service alerts.

        Returns:
            List of parsed service alert dictionaries
        """
        # Check cache
        if self._service_alerts_cache and self._cache_timestamp:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl:
                return self._service_alerts_cache

        # Fetch and parse
        feed_data = await self.get_service_alerts()
        if not feed_data:
            return []

        self._service_alerts_cache = self.parser.parse_service_alerts(feed_data)
        self._cache_timestamp = datetime.now()

        return self._service_alerts_cache

    async def get_stop_arrival_info(
        self,
        route_id: str,
        stop_identifier: str
    ) -> Optional[Dict]:
        """
        Get real-time arrival information for a specific stop and route.

        Args:
            route_id: GTFS route ID (e.g., "99") or route short name
            stop_identifier: GTFS stop ID or stop name

        Returns:
            Dictionary with arrival time and delay information, or None
        """
        # Try to resolve route short name to route ID
        resolved_route_id = route_id
        if self.gtfs_static:
            await self.ensure_gtfs_loaded()
            resolved_route_id = self.gtfs_static.get_route_id_by_short_name(route_id) or route_id

        trip_updates = await self.get_parsed_trip_updates()
        return self.parser.get_stop_arrival_time(trip_updates, resolved_route_id, stop_identifier)

    async def get_route_real_time_delays(self, route_id: str) -> List[Dict]:
        """
        Get all real-time delays for a specific route.

        Args:
            route_id: GTFS route ID

        Returns:
            List of delay information for stops on this route
        """
        trip_updates = await self.get_parsed_trip_updates()
        return self.parser.get_route_delays(trip_updates, route_id)

    async def get_position_updates(self) -> bytes:
        """Get GTFS Realtime position updates feed (Protocol Buffer format)."""
        if not self.api_key:
            logger.warning("TransLink API key not configured")
            return b""

        try:
            url = f"{self.base_url}/gtfsposition"
            params = {"apikey": self.api_key}

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            return response.content  # Return raw bytes (Protocol Buffer format)

        except Exception as e:
            logger.error(f"Error fetching TransLink position updates: {e}")
            return b""

    async def get_service_alerts(self) -> bytes:
        """Get GTFS Realtime service alerts feed (Protocol Buffer format)."""
        if not self.api_key:
            logger.warning("TransLink API key not configured")
            return b""

        try:
            url = f"{self.base_url}/gtfsalerts"
            params = {"apikey": self.api_key}

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            return response.content  # Return raw bytes (Protocol Buffer format)

        except Exception as e:
            logger.error(f"Error fetching TransLink service alerts: {e}")
            return b""

    async def get_nearby_stops(self, point: Point, radius: int = 500) -> List[TransitData]:
        """Get nearby transit stops.

        Note: The old RTTI API endpoint for querying stops by location is no longer available.
        This method is kept for backwards compatibility but returns empty list.
        To get real-time transit data, use get_trip_updates() and parse the GTFS-RT feed.
        """
        logger.warning(
            "get_nearby_stops() is deprecated. The RTTI API was retired on Dec 3, 2024. "
            "Use GTFS-RT feeds (get_trip_updates()) instead."
        )
        return []

    async def get_route_info(self, route_id: str) -> Dict[str, Any]:
        """Get detailed route information.

        Note: The old RTTI API endpoint for route info is no longer available.
        This method is kept for backwards compatibility but returns empty dict.
        """
        logger.warning(
            "get_route_info() is deprecated. The RTTI API was retired on Dec 3, 2024. "
            "Use GTFS-RT feeds instead."
        )
        return {}


class LimeClient:
    """Client for Lime bike/scooter sharing API."""

    def __init__(self):
        self.api_key = settings.lime_api_key
        self.base_url = settings.lime_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_available_vehicles(self, point: Point, radius: int = 1000) -> List[BikeScooterData]:
        """Get available bikes and scooters near a point."""
        if not self.api_key:
            logger.warning("Lime API key not configured")
            return []

        try:
            # Note: This is a simplified implementation
            # Real Lime API would require proper authentication and endpoints
            url = f"{self.base_url}/vehicles"
            params = {
                "lat": point.lat,
                "lng": point.lng,
                "radius": radius
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            vehicles = []

            for vehicle in data.get("data", {}).get("attributes", {}).get("vehicles", []):
                vehicles.append(BikeScooterData(
                    station_id=vehicle.get("id", ""),
                    location=Point(
                        lat=vehicle.get("attributes", {}).get("lat", 0),
                        lng=vehicle.get("attributes", {}).get("lng", 0)
                    ),
                    available_bikes=1 if vehicle.get("attributes", {}).get("type") == "bike" else 0,
                    available_scooters=1 if vehicle.get("attributes", {}).get("type") == "scooter" else 0
                ))

            return vehicles

        except Exception as e:
            logger.error(f"Error fetching Lime vehicles: {e}")
            return []


class OpenWeatherClient:
    """Client for OpenWeatherMap API."""

    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_current_weather(self, point: Point) -> WeatherData:
        """Get current weather conditions for a point."""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return WeatherData(
                condition=WeatherCondition.CLEAR,
                temperature=20.0,
                humidity=50.0,
                wind_speed=10.0,
                precipitation=0.0,
                visibility=10.0
            )

        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": point.lat,
                "lon": point.lng,
                "appid": self.api_key,
                "units": "metric"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            weather = data.get("weather", [{}])[0]
            main = data.get("main", {})
            wind = data.get("wind", {})
            visibility = data.get("visibility", 10000) / 1000  # Convert to km

            # Map weather condition to our enum
            condition_map = {
                "clear": WeatherCondition.CLEAR,
                "clouds": WeatherCondition.CLEAR,
                "rain": WeatherCondition.RAIN,
                "drizzle": WeatherCondition.RAIN,
                "thunderstorm": WeatherCondition.RAIN,
                "snow": WeatherCondition.SNOW,
                "mist": WeatherCondition.FOG,
                "fog": WeatherCondition.FOG,
                "haze": WeatherCondition.FOG
            }

            condition = condition_map.get(weather.get("main", "").lower(), WeatherCondition.CLEAR)

            return WeatherData(
                condition=condition,
                temperature=main.get("temp", 20.0),
                humidity=main.get("humidity", 50.0),
                wind_speed=wind.get("speed", 0.0) * 3.6,  # m/s to km/h
                precipitation=main.get("rain", {}).get("1h", 0.0),
                visibility=visibility
            )

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return WeatherData(
                condition=WeatherCondition.CLEAR,
                temperature=20.0,
                humidity=50.0,
                wind_speed=10.0,
                precipitation=0.0,
                visibility=10.0
            )


class VancouverOpenDataClient:
    """Client for City of Vancouver Open Data API."""

    def __init__(self):
        self.base_url = settings.vancouver_open_data_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_road_closures(self) -> List[Dict[str, Any]]:
        """Get current road closures and construction."""
        try:
            # This is a simplified implementation
            # Real implementation would use the actual Vancouver Open Data API
            url = f"{self.base_url}/datastore_search"
            params = {
                "resource_id": "road-closures",  # This would be the actual resource ID
                "limit": 100
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("result", {}).get("records", [])

        except Exception as e:
            logger.error(f"Error fetching road closures: {e}")
            return []

    async def get_construction_zones(self) -> List[Dict[str, Any]]:
        """Get current construction zones."""
        try:
            # Similar to road closures, this would use the actual API
            url = f"{self.base_url}/datastore_search"
            params = {
                "resource_id": "construction-zones",
                "limit": 100
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("result", {}).get("records", [])

        except Exception as e:
            logger.error(f"Error fetching construction zones: {e}")
            return []


class APIClientManager:
    """Manages all API clients and provides unified interface."""

    def __init__(self):
        self.google_maps = GoogleMapsClient()
        self.translink = TransLinkClient()
        self.lime = LimeClient()
        self.openweather = OpenWeatherClient()
        self.vancouver_data = VancouverOpenDataClient()

    async def get_all_data(self, origin: Point, destination: Point) -> Dict[str, Any]:
        """Fetch all relevant data for route calculation."""
        tasks = [
            self.openweather.get_current_weather(origin),
            self.google_maps.get_traffic_data(origin, destination),
            self.translink.get_nearby_stops(origin),
            self.translink.get_nearby_stops(destination),
            self.lime.get_available_vehicles(origin),
            self.lime.get_available_vehicles(destination),
            self.vancouver_data.get_road_closures(),
            self.vancouver_data.get_construction_zones()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "weather": results[0] if not isinstance(results[0], Exception) else None,
            "traffic": results[1] if not isinstance(results[1], Exception) else [],
            "transit_origin": results[2] if not isinstance(results[2], Exception) else [],
            "transit_destination": results[3] if not isinstance(results[3], Exception) else [],
            "lime_origin": results[4] if not isinstance(results[4], Exception) else [],
            "lime_destination": results[5] if not isinstance(results[5], Exception) else [],
            "road_closures": results[6] if not isinstance(results[6], Exception) else [],
            "construction": results[7] if not isinstance(results[7], Exception) else []
        }

    async def close(self) -> None:
        """Close all HTTP clients."""
        await self.google_maps.client.aclose()
        await self.translink.client.aclose()
        await self.lime.client.aclose()
        await self.openweather.client.aclose()
        await self.vancouver_data.client.aclose()
