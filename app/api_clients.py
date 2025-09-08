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
    """Client for TransLink (Vancouver public transit) API."""

    def __init__(self):
        self.api_key = settings.translink_api_key
        self.base_url = settings.translink_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_nearby_stops(self, point: Point, radius: int = 500) -> List[TransitData]:
        """Get nearby transit stops."""
        if not self.api_key:
            logger.warning("TransLink API key not configured")
            return []

        try:
            url = f"{self.base_url}/rttiapi/v1/stops"
            params = {
                "apikey": self.api_key,
                "lat": point.lat,
                "long": point.lng,
                "radius": radius
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            stops = []

            for stop in data:
                stops.append(TransitData(
                    route_id=stop.get("RouteNo", ""),
                    route_name=stop.get("RouteName", ""),
                    stop_id=stop.get("StopNo", ""),
                    stop_name=stop.get("Name", ""),
                    next_arrival=datetime.now() + timedelta(minutes=stop.get("Schedules", [{}])[0].get("ExpectedCountdown", 0)),
                    vehicle_type="bus",
                    accessibility=stop.get("WheelchairAccess", False)
                ))

            return stops

        except Exception as e:
            logger.error(f"Error fetching TransLink stops: {e}")
            return []

    async def get_route_info(self, route_id: str) -> Dict[str, Any]:
        """Get detailed route information."""
        if not self.api_key:
            return {}

        try:
            url = f"{self.base_url}/rttiapi/v1/routes/{route_id}"
            params = {"apikey": self.api_key}

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching route info: {e}")
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

    async def close(self):
        """Close all HTTP clients."""
        await self.google_maps.client.aclose()
        await self.translink.client.aclose()
        await self.lime.client.aclose()
        await self.openweather.client.aclose()
        await self.vancouver_data.client.aclose()
