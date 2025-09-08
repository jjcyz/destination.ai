"""
Demo mode for Route Recommendation System.
Provides sample data and functionality when API keys are not available.
"""

import random
import uuid
from typing import List, Dict, Optional
from datetime import datetime

from .models import (
    Point, Route, RouteStep, RouteRequest, RouteResponse,
    TransportMode, RoutePreference, WeatherData, WeatherCondition
)


class DemoDataProvider:
    """Provides demo data for testing without API keys."""

    # Vancouver landmarks and their coordinates
    VANCOUVER_LOCATIONS = {
        "vancouver downtown": Point(lat=49.2827, lng=-123.1207),
        "stanley park": Point(lat=49.3043, lng=-123.1443),
        "granville island": Point(lat=49.2726, lng=-123.1350),
        "gastown": Point(lat=49.2827, lng=-123.1087),
        "chinatown": Point(lat=49.2794, lng=-123.1087),
        "kitsilano": Point(lat=49.2726, lng=-123.1675),
        "west end": Point(lat=49.2888, lng=-123.1308),
        "yaletown": Point(lat=49.2756, lng=-123.1219),
        "coal harbour": Point(lat=49.2888, lng=-123.1207),
        "english bay": Point(lat=49.2888, lng=-123.1443),
        "robson square": Point(lat=49.2827, lng=-123.1207),
        "vancouver art gallery": Point(lat=49.2827, lng=-123.1207),
        "science world": Point(lat=49.2736, lng=-123.1036),
        "bc place": Point(lat=49.2768, lng=-123.1087),
        "rogers arena": Point(lat=49.2778, lng=-123.1087),
        "canada place": Point(lat=49.2888, lng=-123.1119),
        "vancouver convention centre": Point(lat=49.2888, lng=-123.1119),
        "seawall": Point(lat=49.2888, lng=-123.1443),
        "lions gate bridge": Point(lat=49.3043, lng=-123.1443),
        "burrard bridge": Point(lat=49.2726, lng=-123.1350),
        "granville bridge": Point(lat=49.2726, lng=-123.1350),
        "cambie bridge": Point(lat=49.2756, lng=-123.1219),
        "main street": Point(lat=49.2736, lng=-123.1036),
        "commercial drive": Point(lat=49.2736, lng=-123.1036),
        "broadway": Point(lat=49.2626, lng=-123.1207),
        "4th avenue": Point(lat=49.2626, lng=-123.1675),
        "16th avenue": Point(lat=49.2526, lng=-123.1207),
        "41st avenue": Point(lat=49.2326, lng=-123.1207),
        "marine drive": Point(lat=49.2126, lng=-123.1207),
        "airport": Point(lat=49.1967, lng=-123.1815),
    }

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

    @classmethod
    def geocode_address(cls, address: str) -> Optional[Point]:
        """Demo geocoding - returns coordinates for known Vancouver locations."""
        address_lower = address.lower().strip()

        # Direct match
        if address_lower in cls.VANCOUVER_LOCATIONS:
            return cls.VANCOUVER_LOCATIONS[address_lower]

        # Partial matches
        for location, point in cls.VANCOUVER_LOCATIONS.items():
            if any(word in location for word in address_lower.split()):
                return point

        # If no match found, return a random Vancouver location
        return random.choice(list(cls.VANCOUVER_LOCATIONS.values()))

    @classmethod
    def generate_demo_routes(cls, request: RouteRequest) -> RouteResponse:
        """Generate demo routes for testing without API keys."""
        # Calculate distance between origin and destination
        distance = request.origin.distance_to(request.destination)

        # Generate routes for each preference
        routes = []

        for preference in request.preferences:
            route_id = str(uuid.uuid4())

            # Generate steps based on preference
            steps = cls._generate_demo_steps(request, preference, distance)

            # Calculate totals
            total_distance = sum(step.distance for step in steps)
            total_time = sum(step.estimated_time for step in steps)
            total_sustainability_points = sum(step.sustainability_points for step in steps)

            # Calculate scores based on preference
            safety_score = cls._get_demo_safety_score(preference)
            energy_efficiency = cls._get_demo_energy_efficiency(preference)
            scenic_score = cls._get_demo_scenic_score(preference)

            route = Route(
                id=route_id,
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

            routes.append(route)

        # Generate a few alternative routes
        alternatives = []
        if len(routes) < 3:
            # Add some alternative routes with different preferences
            alt_preferences = [p for p in RoutePreference if p not in request.preferences]
            for alt_pref in alt_preferences[:2]:
                route_id = str(uuid.uuid4())
                steps = cls._generate_demo_steps(request, alt_pref, distance)

                route = Route(
                    id=route_id,
                    origin=request.origin,
                    destination=request.destination,
                    steps=steps,
                    total_distance=sum(step.distance for step in steps),
                    total_time=sum(step.estimated_time for step in steps),
                    total_sustainability_points=sum(step.sustainability_points for step in steps),
                    preference=alt_pref,
                    safety_score=cls._get_demo_safety_score(alt_pref),
                    energy_efficiency=cls._get_demo_energy_efficiency(alt_pref),
                    scenic_score=cls._get_demo_scenic_score(alt_pref)
                )
                alternatives.append(route)

        return RouteResponse(
            routes=routes,
            alternatives=alternatives,
            processing_time=0.5,  # Simulated processing time
            data_sources=["Demo Mode - No API Keys Required"]
        )

    @classmethod
    def _generate_demo_steps(cls, request: RouteRequest, preference: RoutePreference, total_distance: float) -> List[RouteStep]:
        """Generate demo route steps based on preference."""
        steps = []

        # Choose transport modes based on preference
        if preference == RoutePreference.FASTEST:
            modes = [TransportMode.CAR, TransportMode.SKYTRAIN, TransportMode.BUS]
        elif preference == RoutePreference.SAFEST:
            modes = [TransportMode.WALKING, TransportMode.BUS, TransportMode.SKYTRAIN]
        elif preference == RoutePreference.ENERGY_EFFICIENT:
            modes = [TransportMode.WALKING, TransportMode.BIKING, TransportMode.BUS]
        elif preference == RoutePreference.SCENIC:
            modes = [TransportMode.WALKING, TransportMode.BIKING, TransportMode.SCOOTER]
        elif preference == RoutePreference.HEALTHY:
            modes = [TransportMode.WALKING, TransportMode.BIKING]
        elif preference == RoutePreference.CHEAPEST:
            modes = [TransportMode.WALKING, TransportMode.BUS]
        else:
            modes = [TransportMode.WALKING, TransportMode.BUS]

        # Generate 2-4 steps
        num_steps = random.randint(2, 4)
        step_distance = total_distance / num_steps

        current_point = request.origin

        for i in range(num_steps):
            # Choose mode for this step
            mode = random.choice(modes)

            # Calculate next point (simplified - just move towards destination)
            progress = (i + 1) / num_steps
            lat_diff = request.destination.lat - request.origin.lat
            lng_diff = request.destination.lng - request.origin.lng

            next_point = Point(
                lat=request.origin.lat + (lat_diff * progress),
                lng=request.origin.lng + (lng_diff * progress)
            )

            # Calculate time based on mode and distance
            mode_speed = cls.MODE_SPEEDS[mode]  # km/h
            estimated_time = int((step_distance / 1000) / mode_speed * 3600)  # seconds

            # Generate instructions
            if i == 0:
                instructions = f"Start your journey using {mode.value}"
            elif i == num_steps - 1:
                instructions = f"Arrive at your destination"
            else:
                directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
                direction = random.choice(directions)
                instructions = f"Continue {step_distance/1000:.1f}km {direction} using {mode.value}"

            # Calculate sustainability points
            sustainability_points = cls._calculate_sustainability_points(mode, step_distance)

            # Calculate slope (random for demo)
            slope = random.uniform(-3, 5)

            # Determine effort level
            effort_level = "moderate"
            if slope > 3:
                effort_level = "high"
            elif slope < -1:
                effort_level = "low"

            step = RouteStep(
                id=str(uuid.uuid4()),
                mode=mode,
                distance=step_distance,
                estimated_time=estimated_time,
                slope=slope,
                effort_level=effort_level,
                instructions=instructions,
                start_point=current_point,
                end_point=next_point,
                sustainability_points=sustainability_points
            )

            steps.append(step)
            current_point = next_point

        return steps

    @classmethod
    def _calculate_sustainability_points(cls, mode: TransportMode, distance: float) -> int:
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

    @classmethod
    def _get_demo_safety_score(cls, preference: RoutePreference) -> float:
        """Get demo safety score based on preference."""
        scores = {
            RoutePreference.SAFEST: 0.95,
            RoutePreference.HEALTHY: 0.90,
            RoutePreference.ENERGY_EFFICIENT: 0.85,
            RoutePreference.SCENIC: 0.80,
            RoutePreference.CHEAPEST: 0.75,
            RoutePreference.FASTEST: 0.70
        }
        return scores.get(preference, 0.80)

    @classmethod
    def _get_demo_energy_efficiency(cls, preference: RoutePreference) -> float:
        """Get demo energy efficiency score based on preference."""
        scores = {
            RoutePreference.ENERGY_EFFICIENT: 0.95,
            RoutePreference.HEALTHY: 0.90,
            RoutePreference.SCENIC: 0.85,
            RoutePreference.SAFEST: 0.80,
            RoutePreference.CHEAPEST: 0.75,
            RoutePreference.FASTEST: 0.60
        }
        return scores.get(preference, 0.80)

    @classmethod
    def _get_demo_scenic_score(cls, preference: RoutePreference) -> float:
        """Get demo scenic score based on preference."""
        scores = {
            RoutePreference.SCENIC: 0.95,
            RoutePreference.HEALTHY: 0.85,
            RoutePreference.ENERGY_EFFICIENT: 0.80,
            RoutePreference.SAFEST: 0.75,
            RoutePreference.CHEAPEST: 0.70,
            RoutePreference.FASTEST: 0.60
        }
        return scores.get(preference, 0.75)

    @classmethod
    def get_demo_weather_data(cls) -> WeatherData:
        """Get demo weather data."""
        conditions = [
            WeatherCondition.CLEAR,
            WeatherCondition.PARTLY_CLOUDY,
            WeatherCondition.CLOUDY,
            WeatherCondition.RAIN,
            WeatherCondition.SNOW
        ]

        return WeatherData(
            temperature=random.uniform(5, 25),  # Vancouver temperature range
            condition=random.choice(conditions),
            humidity=random.uniform(40, 90),
            wind_speed=random.uniform(5, 25),
            visibility=random.uniform(5, 15),
            uv_index=random.uniform(0, 10),
            timestamp=datetime.now()
        )

    @classmethod
    def get_demo_traffic_data(cls) -> List[Dict]:
        """Get demo traffic data."""
        return [
            {
                "edge_id": f"demo_edge_{i}",
                "current_speed": random.uniform(20, 60),
                "free_flow_speed": 50,
                "congestion_level": random.choice(["low", "moderate", "high"]),
                "timestamp": datetime.now()
            }
            for i in range(5)
        ]

    @classmethod
    def get_demo_road_closures(cls) -> List[Dict]:
        """Get demo road closure data."""
        return [
            {
                "road_name": "Demo Street",
                "closure_type": "construction",
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "description": "Demo road closure for testing"
            }
        ]

    @classmethod
    def get_demo_transit_data(cls) -> List[Dict]:
        """Get demo transit data."""
        return [
            {
                "route_id": "demo_route_1",
                "route_name": "Demo Bus Route",
                "arrival_time": datetime.now(),
                "delay_minutes": random.randint(0, 10),
                "vehicle_type": "bus"
            }
        ]

    @classmethod
    def get_demo_bike_share_data(cls) -> List[Dict]:
        """Get demo bike/scooter share data."""
        return [
            {
                "station_id": f"demo_station_{i}",
                "available_bikes": random.randint(0, 20),
                "available_scooters": random.randint(0, 10),
                "location": Point(
                    lat=49.2827 + random.uniform(-0.1, 0.1),
                    lng=-123.1207 + random.uniform(-0.1, 0.1)
                )
            }
            for i in range(10)
        ]


class DemoGamificationProvider:
    """Provides demo gamification data."""

    @classmethod
    def calculate_demo_rewards(cls, route: Route, user_profile: Dict) -> Dict:
        """Calculate demo gamification rewards."""
        # Base sustainability points
        sustainability_points = route.total_sustainability_points

        # Bonus points for different preferences
        preference_bonuses = {
            RoutePreference.ENERGY_EFFICIENT: 50,
            RoutePreference.HEALTHY: 40,
            RoutePreference.SCENIC: 30,
            RoutePreference.SAFEST: 25,
            RoutePreference.CHEAPEST: 20,
            RoutePreference.FASTEST: 10
        }

        bonus_points = preference_bonuses.get(route.preference, 0)
        total_points = sustainability_points + bonus_points

        # Random achievements and badges for demo
        achievements_unlocked = []
        badges_earned = []

        if total_points > 100:
            achievements_unlocked.append({
                "id": "eco_warrior",
                "name": "Eco Warrior",
                "description": "Earned 100+ sustainability points in a single route"
            })

        if route.preference == RoutePreference.HEALTHY:
            badges_earned.append({
                "id": "health_enthusiast",
                "name": "Health Enthusiast",
                "description": "Completed a healthy route"
            })

        return {
            "sustainability_points": total_points,
            "co2_saved": round(route.total_distance / 1000 * 0.2, 2),  # kg CO2
            "achievements_unlocked": achievements_unlocked,
            "badges_earned": badges_earned,
            "level_up": total_points > 500,
            "streak_bonus": 0
        }

    @classmethod
    def get_demo_achievements(cls) -> List[Dict]:
        """Get demo achievements."""
        return [
            {
                "id": "first_route",
                "name": "First Steps",
                "description": "Complete your first route",
                "icon": "🚶",
                "points_reward": 10
            },
            {
                "id": "eco_warrior",
                "name": "Eco Warrior",
                "description": "Earn 100+ sustainability points in a single route",
                "icon": "🌱",
                "points_reward": 50
            },
            {
                "id": "speed_demon",
                "name": "Speed Demon",
                "description": "Complete 10 fastest routes",
                "icon": "⚡",
                "points_reward": 30
            },
            {
                "id": "scenic_explorer",
                "name": "Scenic Explorer",
                "description": "Complete 5 scenic routes",
                "icon": "🏞️",
                "points_reward": 40
            },
            {
                "id": "health_enthusiast",
                "name": "Health Enthusiast",
                "description": "Complete 10 healthy routes",
                "icon": "💪",
                "points_reward": 60
            }
        ]

    @classmethod
    def get_demo_badges(cls) -> List[Dict]:
        """Get demo badges."""
        return [
            {
                "id": "vancouver_explorer",
                "name": "Vancouver Explorer",
                "description": "Explore all major Vancouver neighborhoods",
                "icon": "🏙️",
                "rarity": "common"
            },
            {
                "id": "sustainability_champion",
                "name": "Sustainability Champion",
                "description": "Earn 1000+ sustainability points",
                "icon": "🌍",
                "rarity": "rare"
            },
            {
                "id": "multi_modal_master",
                "name": "Multi-Modal Master",
                "description": "Use all transportation modes",
                "icon": "🚌",
                "rarity": "epic"
            },
            {
                "id": "weather_warrior",
                "name": "Weather Warrior",
                "description": "Complete routes in all weather conditions",
                "icon": "🌧️",
                "rarity": "legendary"
            }
        ]

    @classmethod
    def get_demo_daily_challenges(cls) -> List[Dict]:
        """Get demo daily challenges."""
        return [
            {
                "id": "walk_5km",
                "name": "Walk 5km Today",
                "description": "Complete a 5km walking route",
                "reward_points": 25,
                "progress": 0,
                "target": 5000,
                "unit": "meters"
            },
            {
                "id": "eco_route",
                "name": "Eco-Friendly Route",
                "description": "Complete an energy-efficient route",
                "reward_points": 30,
                "progress": 0,
                "target": 1,
                "unit": "routes"
            },
            {
                "id": "explore_neighborhood",
                "name": "Explore New Neighborhood",
                "description": "Visit a new Vancouver neighborhood",
                "reward_points": 40,
                "progress": 0,
                "target": 1,
                "unit": "neighborhoods"
            }
        ]

    @classmethod
    def get_demo_leaderboard(cls) -> List[Dict]:
        """Get demo leaderboard data."""
        names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Avery", "Quinn", "Sage", "River"]
        return [
            {
                "rank": i + 1,
                "username": names[i],
                "total_points": random.randint(1000, 5000),
                "routes_completed": random.randint(50, 200),
                "sustainability_score": random.randint(80, 100)
            }
            for i in range(10)
        ]

    @classmethod
    def get_demo_sustainability_tips(cls) -> List[Dict]:
        """Get demo sustainability tips."""
        return [
            {
                "id": "walking_tip",
                "title": "Walk for Short Trips",
                "description": "Walking for trips under 1km can save significant emissions and improve your health.",
                "category": "transportation",
                "impact": "high"
            },
            {
                "id": "bike_tip",
                "title": "Use Bike Lanes",
                "description": "Vancouver has extensive bike lane networks. Use them for safer and more efficient cycling.",
                "category": "safety",
                "impact": "medium"
            },
            {
                "id": "transit_tip",
                "title": "Combine Transit Modes",
                "description": "Combine walking, biking, and transit for the most efficient and sustainable journeys.",
                "category": "efficiency",
                "impact": "high"
            },
            {
                "id": "weather_tip",
                "title": "Check Weather Before You Go",
                "description": "Plan your route based on weather conditions to ensure a comfortable and safe journey.",
                "category": "planning",
                "impact": "medium"
            }
        ]
