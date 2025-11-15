"""
Routing engine implementing A* algorithm with dynamic edge costs.
Handles multi-modal routing with real-time data integration.
"""

import heapq
import math
import re
from typing import List, Dict, Set, Tuple, Optional, Callable
from datetime import datetime, timedelta
import logging
import asyncio

from .models import (
    Point, Node, Edge, Route, RouteStep, RouteRequest, RouteResponse,
    TransportMode, RoutePreference, WeatherData, TrafficData
)
from .graph_builder import VancouverGraphBuilder
from .api_clients import APIClientManager

logger = logging.getLogger(__name__)


class RoutingEngine:
    """A* routing engine with multi-modal support and dynamic costs."""

    def __init__(self, graph_builder: VancouverGraphBuilder):
        self.graph_builder = graph_builder
        self.api_client = APIClientManager()

        # Transport mode speeds (km/h)
        self.mode_speeds = {
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
        self.mode_switch_costs = {
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

    async def find_routes(self, request: RouteRequest) -> RouteResponse:
        """
        Find optimal routes using Google Maps Directions API directly.

        Args:
            request: Route request with preferences and constraints

        Returns:
            RouteResponse with calculated routes
        """
        start_time = datetime.now()

        try:
            # Check if we have API keys for real data
            from .config import validate_api_keys
            api_keys_status = validate_api_keys()

            if not api_keys_status["all_required"]:
                logger.info("API keys not available, using demo mode")
                from .demo import DemoDataProvider
                return DemoDataProvider.generate_demo_routes(request)

            # Get real-time data (weather, transit, etc.) for enhancement
            real_time_data = await self.api_client.get_all_data(request.origin, request.destination)

            # Get routes from Google Maps for each transport mode and preference
            routes = []
            alternatives = []

            # Map our transport modes to Google Maps modes
            mode_mapping = {
                TransportMode.WALKING: "walking",
                TransportMode.BIKING: "bicycling",
                TransportMode.CAR: "driving",
                TransportMode.BUS: "transit",
                TransportMode.SKYTRAIN: "transit",
                TransportMode.SCOOTER: "walking",  # Approximate with walking
            }

            # Group transit modes together (they use the same Google Maps mode)
            transit_modes = {TransportMode.BUS, TransportMode.SKYTRAIN}
            processed_modes = set()

            # Get routes for each requested transport mode
            for transport_mode in request.transport_modes:
                # Skip if we already processed transit modes
                if transport_mode in transit_modes and "transit" in processed_modes:
                    continue

                google_mode = mode_mapping.get(transport_mode, "driving")
                processed_modes.add(google_mode)

                # Build avoid list based on preferences
                avoid_list = []
                if request.avoid_highways:
                    avoid_list.append("highways")

                # Get directions from Google Maps
                directions_data = await self.api_client.google_maps.get_directions(
                    origin=request.origin,
                    destination=request.destination,
                    mode=google_mode,
                    alternatives=True,
                    avoid=avoid_list if avoid_list else None,
                    departure_time="now" if request.departure_time else None
                )

                if not directions_data or not directions_data.get("routes"):
                    logger.warning(f"No routes found for mode {google_mode}")
                    continue

                # Process each route from Google Maps
                for route_idx, google_route in enumerate(directions_data.get("routes", [])):
                    # Determine actual transport mode from route data
                    actual_mode = transport_mode
                    if google_mode == "transit":
                        # Check if route uses bus or train
                        for leg in google_route.get("legs", []):
                            for step in leg.get("steps", []):
                                transit_details = step.get("transit_details")
                                if transit_details:
                                    vehicle_type = transit_details.get("line", {}).get("vehicle", {}).get("type", "")
                                    if vehicle_type == "SUBWAY" or "train" in vehicle_type.lower():
                                        actual_mode = TransportMode.SKYTRAIN
                                    else:
                                        actual_mode = TransportMode.BUS
                                    break
                            if actual_mode != transport_mode:
                                break

                    # Convert Google Maps route to our Route model
                    route = await self._convert_google_route_to_route(
                        google_route,
                        request,
                        actual_mode,
                        real_time_data
                    )

                    if route:
                        # Apply preference-based scoring
                        route = self._apply_preference_scoring(route, request.preferences)

                        if route_idx == 0:
                            routes.append(route)
                        else:
                            alternatives.append(route)

            # If no routes found, try with default mode
            if not routes:
                logger.warning("No routes found with requested modes, trying default")
                directions_data = await self.api_client.google_maps.get_directions(
                    origin=request.origin,
                    destination=request.destination,
                    mode="driving",
                    alternatives=True
                )

                if directions_data and directions_data.get("routes"):
                    route = await self._convert_google_route_to_route(
                        directions_data["routes"][0],
                        request,
                        TransportMode.CAR,
                        real_time_data
                    )
                    if route:
                        route = self._apply_preference_scoring(route, request.preferences)
                        routes.append(route)

            # Sort routes by preference priority
            routes = self._sort_routes_by_preferences(routes, request.preferences)

            processing_time = (datetime.now() - start_time).total_seconds()

            return RouteResponse(
                routes=routes[:3],  # Limit to top 3 routes
                alternatives=alternatives[:3],  # Limit to top 3 alternatives
                processing_time=processing_time,
                data_sources=["Google Maps", "TransLink", "Lime", "OpenWeatherMap", "Vancouver Open Data"]
            )

        except Exception as e:
            logger.error(f"Error finding routes: {e}")
            # Fallback to demo mode if real routing fails
            logger.info("Falling back to demo mode due to error")
            from .demo import DemoDataProvider
            return DemoDataProvider.generate_demo_routes(request)

    async def _find_route_for_preference(
        self,
        request: RouteRequest,
        origin_node: str,
        destination_node: str,
        preference: RoutePreference,
        real_time_data: Dict
    ) -> Optional[Route]:
        """Find route for a specific preference."""

        # Define cost function based on preference
        cost_function = self._get_cost_function(preference)
        heuristic_function = self._get_heuristic_function(preference)

        # Run A* algorithm
        path = await self._astar_search(
            origin_node,
            destination_node,
            cost_function,
            heuristic_function,
            request.transport_modes
        )

        if not path:
            return None

        # Convert path to route
        route = await self._path_to_route(path, request, preference, real_time_data)
        return route

    async def _astar_search(
        self,
        start: str,
        goal: str,
        cost_function: Callable,
        heuristic_function: Callable,
        allowed_modes: List[TransportMode]
    ) -> Optional[List[Tuple[str, str, TransportMode]]]:
        """
        A* search algorithm implementation.

        Returns:
            List of (from_node, to_node, mode) tuples representing the path
        """
        # Priority queue: (f_score, node, path, current_mode)
        open_set = [(0, start, [], None)]
        closed_set = set()

        # g_score[node] = cost from start to node
        g_score = {start: 0}

        # f_score[node] = g_score[node] + h_score[node]
        f_score = {start: heuristic_function(start, goal)}

        while open_set:
            current_f, current, path, current_mode = heapq.heappop(open_set)

            if current in closed_set:
                continue

            closed_set.add(current)

            if current == goal:
                return path

            # Explore neighbors
            for neighbor, edge_data in self.graph_builder.graph[current].items():
                if neighbor in closed_set:
                    continue

                for edge_key, edge_attrs in edge_data.items():
                    edge = self.graph_builder.edges.get(edge_attrs.get('id'))
                    if not edge:
                        continue

                    # Check if edge allows any of the requested modes
                    if not any(mode in edge.allowed_modes for mode in allowed_modes):
                        continue

                    # Try each allowed mode
                    for mode in edge.allowed_modes:
                        if mode not in allowed_modes:
                            continue

                        # Calculate tentative g_score
                        edge_cost = cost_function(edge, mode, current_mode)
                        tentative_g = g_score.get(current, float('inf')) + edge_cost

                        if tentative_g < g_score.get(neighbor, float('inf')):
                            # This path to neighbor is better
                            g_score[neighbor] = tentative_g
                            f_score[neighbor] = tentative_g + heuristic_function(neighbor, goal)

                            new_path = path + [(current, neighbor, mode)]
                            heapq.heappush(open_set, (f_score[neighbor], neighbor, new_path, mode))

        return None  # No path found

    def _get_cost_function(self, preference: RoutePreference) -> Callable:
        """Get cost function based on route preference."""

        if preference == RoutePreference.FASTEST:
            return self._fastest_cost_function
        elif preference == RoutePreference.SAFEST:
            return self._safest_cost_function
        elif preference == RoutePreference.ENERGY_EFFICIENT:
            return self._energy_efficient_cost_function
        elif preference == RoutePreference.SCENIC:
            return self._scenic_cost_function
        elif preference == RoutePreference.HEALTHY:
            return self._healthy_cost_function
        elif preference == RoutePreference.CHEAPEST:
            return self._cheapest_cost_function
        else:
            return self._fastest_cost_function

    def _fastest_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for fastest route (time-based)."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)  # seconds

        # Apply penalties
        effective_time = base_time * edge.weather_penalty * edge.event_penalty

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            effective_time += switch_cost

        return effective_time

    def _safest_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for safest route (safety-weighted time)."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)

        # Safety penalty based on mode and road conditions
        safety_penalty = 1.0
        if mode == TransportMode.CAR and not edge.is_bike_lane:
            safety_penalty = 1.2  # Cars are less safe
        elif mode in [TransportMode.BIKING, TransportMode.SCOOTER] and not edge.is_bike_lane:
            safety_penalty = 1.5  # Bikes/scooters on roads without bike lanes

        effective_time = base_time * edge.weather_penalty * edge.event_penalty * safety_penalty

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            effective_time += switch_cost

        return effective_time

    def _energy_efficient_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for energy-efficient route."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)

        # Energy efficiency weights
        energy_weights = {
            TransportMode.WALKING: 0.1,
            TransportMode.BIKING: 0.2,
            TransportMode.SCOOTER: 0.3,
            TransportMode.BUS: 0.4,
            TransportMode.SKYTRAIN: 0.4,
            TransportMode.CAR: 1.0
        }

        energy_cost = edge.distance * energy_weights.get(mode, 0.5)
        effective_time = base_time + energy_cost

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            effective_time += switch_cost

        return effective_time

    def _scenic_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for scenic route."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)

        # Scenic bonus (negative cost) for slower, more scenic modes
        scenic_bonus = {
            TransportMode.WALKING: -0.2,
            TransportMode.BIKING: -0.1,
            TransportMode.SCOOTER: 0.0,
            TransportMode.BUS: 0.0,
            TransportMode.CAR: 0.1
        }

        effective_time = base_time * (1 + scenic_bonus.get(mode, 0))

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            effective_time += switch_cost

        return effective_time

    def _healthy_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for healthy route (encourages active transportation)."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)

        # Health bonus for active modes
        health_bonus = {
            TransportMode.WALKING: -0.3,
            TransportMode.BIKING: -0.2,
            TransportMode.SCOOTER: -0.1,
            TransportMode.BUS: 0.0,
            TransportMode.CAR: 0.2
        }

        effective_time = base_time * (1 + health_bonus.get(mode, 0))

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            effective_time += switch_cost

        return effective_time

    def _cheapest_cost_function(self, edge: Edge, mode: TransportMode, previous_mode: Optional[TransportMode]) -> float:
        """Cost function for cheapest route."""
        base_time = edge.distance / (self.mode_speeds[mode] * 1000 / 3600)

        # Cost per mode (relative)
        cost_weights = {
            TransportMode.WALKING: 0.0,
            TransportMode.BIKING: 0.1,
            TransportMode.SCOOTER: 0.5,
            TransportMode.BUS: 0.3,
            TransportMode.SKYTRAIN: 0.4,
            TransportMode.CAR: 1.0
        }

        cost = base_time + (edge.distance / 1000) * cost_weights.get(mode, 0.5)

        # Add mode switching cost
        if previous_mode and previous_mode != mode:
            switch_cost = self.mode_switch_costs.get((previous_mode, mode), 0)
            cost += switch_cost

        return cost

    def _get_heuristic_function(self, preference: RoutePreference) -> Callable:
        """Get heuristic function for A* algorithm."""
        return self._euclidean_heuristic

    def _euclidean_heuristic(self, node1: str, node2: str) -> float:
        """Euclidean distance heuristic."""
        if node1 not in self.graph_builder.nodes or node2 not in self.graph_builder.nodes:
            return 0

        point1 = self.graph_builder.nodes[node1].point
        point2 = self.graph_builder.nodes[node2].point

        distance = point1.distance_to(point2)

        # Convert to time using average walking speed
        return distance / (self.mode_speeds[TransportMode.WALKING] * 1000 / 3600)

    async def _path_to_route(
        self,
        path: List[Tuple[str, str, TransportMode]],
        request: RouteRequest,
        preference: RoutePreference,
        real_time_data: Dict
    ) -> Route:
        """Convert A* path to Route object."""

        steps = []
        total_distance = 0
        total_time = 0
        total_sustainability_points = 0

        for i, (from_node_id, to_node_id, mode) in enumerate(path):
            from_node = self.graph_builder.nodes[from_node_id]
            to_node = self.graph_builder.nodes[to_node_id]

            # Find edge
            edge = None
            for edge_id, e in self.graph_builder.edges.items():
                if e.from_node == from_node_id and e.to_node == to_node_id:
                    edge = e
                    break

            if not edge:
                continue

            # Calculate step details
            distance = edge.distance
            estimated_time = int(edge.distance / (self.mode_speeds[mode] * 1000 / 3600))

            # Calculate slope if available
            slope = None
            if from_node.elevation is not None and to_node.elevation is not None:
                elevation_diff = to_node.elevation - from_node.elevation
                slope = (elevation_diff / distance) * 100 if distance > 0 else 0

            # Determine effort level
            effort_level = "moderate"
            if slope:
                if slope > 5:
                    effort_level = "high"
                elif slope < -2:
                    effort_level = "low"

            # Generate instructions
            instructions = self._generate_instructions(
                from_node, to_node, mode, i, len(path), edge
            )

            # Calculate sustainability points
            sustainability_points = self._calculate_sustainability_points(mode, distance)

            step = RouteStep(
                mode=mode,
                distance=distance,
                estimated_time=estimated_time,
                slope=slope,
                effort_level=effort_level,
                instructions=instructions,
                start_point=from_node.point,
                end_point=to_node.point,
                sustainability_points=sustainability_points
            )

            steps.append(step)
            total_distance += distance
            total_time += estimated_time
            total_sustainability_points += sustainability_points

        # Calculate route quality metrics
        safety_score = self._calculate_route_safety_score(steps)
        energy_efficiency = self._calculate_energy_efficiency(steps)
        scenic_score = self._calculate_scenic_score(steps)

        return Route(
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

    def _generate_instructions(
        self,
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

    def _calculate_sustainability_points(self, mode: TransportMode, distance: float) -> int:
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

    def _calculate_route_safety_score(self, steps: List[RouteStep]) -> float:
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

    def _calculate_energy_efficiency(self, steps: List[RouteStep]) -> float:
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

    def _calculate_scenic_score(self, steps: List[RouteStep]) -> float:
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

    async def _find_alternative_routes(
        self,
        request: RouteRequest,
        origin_node: str,
        destination_node: str,
        existing_routes: List[Route],
        real_time_data: Dict
    ) -> List[Route]:
        """Find alternative routes that are significantly different from existing ones."""
        alternatives = []

        # Try different preferences
        for preference in RoutePreference:
            if preference not in [r.preference for r in existing_routes]:
                route = await self._find_route_for_preference(
                    request, origin_node, destination_node, preference, real_time_data
                )
                if route and self._is_significantly_different(route, existing_routes):
                    alternatives.append(route)

        return alternatives[:3]  # Limit to 3 alternatives

    def _is_significantly_different(self, route: Route, existing_routes: List[Route]) -> bool:
        """Check if a route is significantly different from existing routes."""
        if not existing_routes:
            return True

        # Check if route uses different modes or has significantly different distance
        for existing_route in existing_routes:
            # Compare total distance (should be at least 20% different)
            distance_ratio = abs(route.total_distance - existing_route.total_distance) / existing_route.total_distance
            if distance_ratio < 0.2:
                return False

            # Compare modes used
            route_modes = set(step.mode for step in route.steps)
            existing_modes = set(step.mode for step in existing_route.steps)
            if route_modes == existing_modes:
                return False

        return True

    async def _update_graph_with_real_time_data(self, real_time_data: Dict):
        """Update graph edges with real-time data."""
        try:
            # Update weather penalties
            weather = real_time_data.get("weather")
            if weather:
                weather_penalty = self._calculate_weather_penalty(weather)
                for edge in self.graph_builder.edges.values():
                    edge.weather_penalty = weather_penalty

            # Update traffic data
            traffic_data = real_time_data.get("traffic", [])
            for traffic in traffic_data:
                if traffic.edge_id in self.graph_builder.edges:
                    edge = self.graph_builder.edges[traffic.edge_id]
                    edge.current_traffic_speed = traffic.current_speed

            # Update event penalties (road closures, construction)
            road_closures = real_time_data.get("road_closures", [])
            construction = real_time_data.get("construction", [])

            # This would be implemented based on actual road closure data
            # For now, we'll use default values

        except Exception as e:
            logger.error(f"Error updating graph with real-time data: {e}")

    def _calculate_weather_penalty(self, weather: WeatherData) -> float:
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


    async def _convert_google_route_to_route(
        self,
        google_route: Dict[str, any],
        request: RouteRequest,
        transport_mode: TransportMode,
        real_time_data: Dict
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

                    # Get step instructions
                    instructions = step.get("html_instructions", "")
                    # Remove HTML tags
                    instructions = re.sub('<[^<]+?>', '', instructions)

                    # Calculate sustainability points
                    sustainability_points = self._calculate_sustainability_points(transport_mode, step_distance)

                    # Determine effort level based on distance and mode
                    effort_level = "moderate"
                    if transport_mode == TransportMode.WALKING:
                        if step_distance > 1000:
                            effort_level = "high"
                        elif step_distance < 200:
                            effort_level = "low"
                    elif transport_mode == TransportMode.BIKING:
                        if step_distance > 5000:
                            effort_level = "high"
                        elif step_distance < 500:
                            effort_level = "low"

                    # Get elevation data if available (skip for performance - can be enabled if needed)
                    slope = None
                    # Note: Elevation API calls are slow, skipping for better performance
                    # Uncomment below if elevation data is critical:
                    # if start_location and end_location:
                    #     elevations = await self.api_client.google_maps.get_elevation([start_point, end_point])
                    #     if len(elevations) == 2 and elevations[0] and elevations[1]:
                    #         elevation_diff = elevations[1] - elevations[0]
                    #         slope = (elevation_diff / step_distance * 100) if step_distance > 0 else 0
                    #         if slope > 5:
                    #             effort_level = "high"
                    #         elif slope < -2:
                    #             effort_level = "low"

                    # Check for transit details
                    transit_details = None
                    if transport_mode in [TransportMode.BUS, TransportMode.SKYTRAIN]:
                        transit_step = step.get("transit_details")
                        if transit_step:
                            transit_details = {
                                "line": transit_step.get("line", {}).get("name", ""),
                                "vehicle": transit_step.get("line", {}).get("vehicle", {}).get("name", ""),
                                "departure_stop": transit_step.get("departure_stop", {}).get("name", ""),
                                "arrival_stop": transit_step.get("arrival_stop", {}).get("name", ""),
                            }

                    route_step = RouteStep(
                        mode=transport_mode,
                        distance=step_distance,
                        estimated_time=step_duration,
                        slope=slope,
                        effort_level=effort_level,
                        instructions=instructions or f"Continue {step_distance/1000:.1f}km",
                        start_point=start_point,
                        end_point=end_point,
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
            safety_score = self._calculate_route_safety_score(steps)
            energy_efficiency = self._calculate_energy_efficiency(steps)
            scenic_score = self._calculate_scenic_score(steps)

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

    def _apply_preference_scoring(self, route: Route, preferences: List[RoutePreference]) -> Route:
        """Apply preference-based scoring to enhance route metrics."""
        if not preferences:
            return route

        # Adjust scores based on preferences
        for preference in preferences:
            if preference == RoutePreference.SAFEST:
                route.safety_score = min(1.0, route.safety_score * 1.1)
            elif preference == RoutePreference.ENERGY_EFFICIENT:
                route.energy_efficiency = min(1.0, route.energy_efficiency * 1.1)
            elif preference == RoutePreference.SCENIC:
                route.scenic_score = min(1.0, route.scenic_score * 1.1)
            elif preference == RoutePreference.HEALTHY:
                # Boost sustainability points for healthy routes
                route.total_sustainability_points = int(route.total_sustainability_points * 1.2)

        return route

    def _sort_routes_by_preferences(self, routes: List[Route], preferences: List[RoutePreference]) -> List[Route]:
        """Sort routes by preference priority."""
        if not preferences:
            return routes

        def route_score(route: Route) -> float:
            score = 0.0
            for pref in preferences:
                if pref == RoutePreference.FASTEST:
                    score += 1000.0 / max(route.total_time, 1)  # Higher score for faster routes
                elif pref == RoutePreference.SAFEST:
                    score += route.safety_score * 100
                elif pref == RoutePreference.ENERGY_EFFICIENT:
                    score += route.energy_efficiency * 100
                elif pref == RoutePreference.SCENIC:
                    score += route.scenic_score * 100
                elif pref == RoutePreference.HEALTHY:
                    score += route.total_sustainability_points
                elif pref == RoutePreference.CHEAPEST:
                    # Assume cheaper = less distance for walking/biking
                    score += 1000.0 / max(route.total_distance, 1)
            return score

        return sorted(routes, key=route_score, reverse=True)

    async def close(self):
        """Close API client connections."""
        await self.api_client.close()
