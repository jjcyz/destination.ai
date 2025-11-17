"""
Data models for the Route Recommendation System.
Defines the core data structures for routes, nodes, edges, and user preferences.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, time
import uuid


class TransportMode(str, Enum):
    """Available transportation modes."""
    WALKING = "walking"
    BIKING = "biking"
    SCOOTER = "scooter"
    CAR = "car"
    BUS = "bus"
    SKYTRAIN = "skytrain"
    SEABUS = "seabus"
    WESTCOAST_EXPRESS = "westcoast_express"


class RoutePreference(str, Enum):
    """User route preferences."""
    FASTEST = "fastest"
    SAFEST = "safest"
    ENERGY_EFFICIENT = "energy_efficient"
    SCENIC = "scenic"
    HEALTHY = "healthy"
    CHEAPEST = "cheapest"


class WeatherCondition(str, Enum):
    """Weather conditions that affect routing."""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    WIND = "wind"
    EXTREME = "extreme"


class Point(BaseModel):
    """Geographic point with latitude and longitude."""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

    def distance_to(self, other: 'Point') -> float:
        """Calculate distance to another point in meters using Haversine formula."""
        from math import radians, cos, sin, asin, sqrt

        # Convert decimal degrees to radians
        lat1, lng1, lat2, lng2 = map(radians, [self.lat, self.lng, other.lat, other.lng])

        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))

        # Radius of earth in meters
        r = 6371000
        return c * r


class Node(BaseModel):
    """Graph node representing intersections, stops, or POIs."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    point: Point
    node_type: str = Field(..., description="Type: intersection, bus_stop, skytrain_station, poi")
    name: Optional[str] = None
    accessibility_features: List[str] = Field(default_factory=list)
    safety_score: float = Field(default=1.0, ge=0.0, le=1.0)
    elevation: Optional[float] = None  # meters above sea level


class Edge(BaseModel):
    """Graph edge representing street segments or transit connections."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_node: str
    to_node: str
    distance: float = Field(..., description="Distance in meters")
    allowed_modes: List[TransportMode] = Field(..., description="Allowed transportation modes")

    # Dynamic attributes (updated in real-time)
    current_traffic_speed: Optional[float] = None  # km/h
    slope: Optional[float] = None  # percentage grade
    weather_penalty: float = Field(default=1.0, ge=0.0)
    event_penalty: float = Field(default=1.0, ge=0.0)
    energy_cost: Dict[TransportMode, float] = Field(default_factory=dict)

    # Static attributes
    is_bike_lane: bool = False
    is_sidewalk: bool = True
    has_transit_service: bool = False
    transit_route_ids: List[str] = Field(default_factory=list)

    def get_effective_cost(self, mode: TransportMode, base_speed: float) -> float:
        """Calculate effective cost for a given transport mode."""
        if mode not in self.allowed_modes:
            return float('inf')

        # Base time cost
        base_time = self.distance / (base_speed * 1000 / 3600)  # seconds

        # Apply penalties
        effective_time = base_time * self.weather_penalty * self.event_penalty

        # Add energy cost if available
        energy_cost = self.energy_cost.get(mode, 0)

        return effective_time + energy_cost


class RouteStep(BaseModel):
    """Individual step in a route."""
    mode: TransportMode
    distance: float = Field(..., description="Distance in meters")
    estimated_time: int = Field(..., description="Estimated time in seconds")
    slope: Optional[float] = None
    effort_level: str = Field(default="moderate", description="low, moderate, high")
    instructions: str
    start_point: Point
    end_point: Point
    polyline: Optional[str] = Field(None, description="Google Maps encoded polyline for accurate route rendering")
    transit_details: Optional[Dict[str, Any]] = None  # For transit steps
    sustainability_points: int = Field(default=0)


class Route(BaseModel):
    """Complete route from origin to destination."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: Point
    destination: Point
    steps: List[RouteStep]
    total_distance: float = Field(..., description="Total distance in meters")
    total_time: int = Field(..., description="Total estimated time in seconds")
    total_sustainability_points: int = Field(default=0)
    preference: RoutePreference
    created_at: datetime = Field(default_factory=datetime.now)

    # Route quality metrics
    safety_score: float = Field(default=1.0, ge=0.0, le=1.0)
    energy_efficiency: float = Field(default=1.0, ge=0.0, le=1.0)
    scenic_score: float = Field(default=0.5, ge=0.0, le=1.0)


class RouteRequest(BaseModel):
    """Request for route calculation."""
    origin: Point
    destination: Point
    preferences: List[RoutePreference] = Field(default=[RoutePreference.FASTEST])
    departure_time: Optional[datetime] = None
    transport_modes: List[TransportMode] = Field(
        default=[TransportMode.WALKING, TransportMode.BIKING, TransportMode.CAR, TransportMode.BUS]
    )
    max_walking_distance: float = Field(default=2000, description="Max walking distance in meters")
    avoid_highways: bool = False
    accessibility_requirements: List[str] = Field(default_factory=list)


class RouteResponse(BaseModel):
    """Response containing calculated routes."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    routes: List[Route]
    alternatives: List[Route] = Field(default_factory=list)
    processing_time: float = Field(..., description="Processing time in seconds")
    data_sources: List[str] = Field(..., description="Data sources used")


class WeatherData(BaseModel):
    """Current weather conditions."""
    condition: WeatherCondition
    temperature: float  # Celsius
    humidity: float  # Percentage
    wind_speed: float  # km/h
    precipitation: float  # mm/h
    visibility: float  # km
    timestamp: datetime = Field(default_factory=datetime.now)


class TrafficData(BaseModel):
    """Real-time traffic information."""
    edge_id: str
    current_speed: float  # km/h
    free_flow_speed: float  # km/h
    congestion_level: float = Field(ge=0.0, le=1.0)  # 0 = no congestion, 1 = severe
    timestamp: datetime = Field(default_factory=datetime.now)


class TransitData(BaseModel):
    """Public transit information."""
    route_id: str
    route_name: str
    stop_id: str
    stop_name: str
    next_arrival: Optional[datetime] = None
    delay_minutes: int = Field(default=0)
    vehicle_type: str  # bus, skytrain, seabus, etc.
    accessibility: bool = False


class BikeScooterData(BaseModel):
    """Bike and scooter sharing availability."""
    station_id: str
    location: Point
    available_bikes: int = 0
    available_scooters: int = 0
    available_docks: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """User profile for personalization."""
    user_id: str
    preferred_modes: List[TransportMode] = Field(default_factory=list)
    fitness_level: str = Field(default="moderate")  # low, moderate, high
    sustainability_goals: bool = True
    accessibility_needs: List[str] = Field(default_factory=list)
    budget_preferences: Dict[str, float] = Field(default_factory=dict)
    time_preferences: Dict[str, int] = Field(default_factory=dict)  # max time per mode

    # Gamification attributes
    level: int = Field(default=1)
    total_sustainability_points: int = Field(default=0)
    total_distance_saved: float = Field(default=0.0)  # CO2 saved in kg
    streak_days: int = Field(default=0)
    achievements: List[str] = Field(default_factory=list)
    badges: List[str] = Field(default_factory=list)


class GamificationStats(BaseModel):
    """User gamification statistics."""
    user_id: str
    total_sustainability_points: int = 0
    total_distance_saved: float = 0  # CO2 saved in kg
    streak_days: int = 0
    achievements: List[str] = Field(default_factory=list)
    level: int = 1
    badges: List[str] = Field(default_factory=list)
