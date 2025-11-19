"""
Routing engine using Google Maps Directions API.
Handles multi-modal routing with real-time data integration.

This is the refactored version that uses modular components from the routing package.
"""

import time
from typing import List, Dict, Optional
from datetime import datetime
import logging
import asyncio

from .models import (
    RouteRequest, RouteResponse, TransportMode
)
from .graph_builder import VancouverGraphBuilder
from .api_clients import APIClientManager
from .routing import (
    convert_google_route_to_route,
    apply_preference_scoring,
    sort_routes_by_preferences,
    update_graph_with_real_time_data,
)

logger = logging.getLogger(__name__)


class RoutingEngine:
    """Routing engine using Google Maps Directions API with multi-modal support."""

    def __init__(self, graph_builder: VancouverGraphBuilder):
        self.graph_builder = graph_builder
        self.api_client = APIClientManager()

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
            real_time_data = await self._fetch_realtime_data(request)

            # Update graph with real-time data (weather penalties, traffic, etc.)
            await update_graph_with_real_time_data(self.graph_builder, real_time_data)

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
                try:
                    # Skip if we already processed transit modes
                    if transport_mode in transit_modes and "transit" in processed_modes:
                        logger.debug(f"Skipping {transport_mode} - transit already processed")
                        continue

                    google_mode = mode_mapping.get(transport_mode, "driving")
                    if google_mode in processed_modes:
                        logger.debug(f"Skipping {transport_mode} - {google_mode} already processed")
                        continue

                    processed_modes.add(google_mode)
                    logger.info(f"Processing transport mode: {transport_mode} -> Google Maps mode: {google_mode}")

                    # Build avoid list based on preferences
                    avoid_list = []
                    if request.avoid_highways:
                        avoid_list.append("highways")

                    # Get directions from Google Maps (with timeout)
                    api_start_time = time.time()
                    try:
                        directions_data = await asyncio.wait_for(
                            self.api_client.google_maps.get_directions(
                                origin=request.origin,
                                destination=request.destination,
                                mode=google_mode,
                                alternatives=True,
                                avoid=avoid_list if avoid_list else None,
                                departure_time="now" if request.departure_time else None
                            ),
                            timeout=5.0  # 5 second timeout for Google Maps API
                        )
                        elapsed = time.time() - api_start_time
                        logger.info(f"Google Maps API call for {google_mode} completed in {elapsed:.2f}s")
                    except asyncio.TimeoutError:
                        logger.error(f"Google Maps API call for {google_mode} timed out after 5 seconds")
                        continue
                    except Exception as e:
                        logger.error(f"Google Maps API call for {google_mode} failed: {type(e).__name__}: {e}")
                        continue

                    if not directions_data or not directions_data.get("routes"):
                        logger.warning(f"No routes found for mode {transport_mode} (Google Maps mode: {google_mode})")
                        continue

                    logger.info(f"Found {len(directions_data.get('routes', []))} routes for {transport_mode}")

                    # Process each route from Google Maps
                    for route_idx, google_route in enumerate(directions_data.get("routes", [])):
                        try:
                            # Determine actual transport mode from route data
                            actual_mode = self._determine_actual_mode(google_route, transport_mode, google_mode)

                            # Convert Google Maps route to our Route model
                            route = await convert_google_route_to_route(
                                google_route,
                                request,
                                actual_mode,
                                real_time_data,
                                self.api_client
                            )

                            if route:
                                # Apply preference-based scoring
                                route = apply_preference_scoring(route, request.preferences)

                                if route_idx == 0:
                                    routes.append(route)
                                    logger.info(f"Added route for {actual_mode} (primary)")
                                else:
                                    alternatives.append(route)
                                    logger.debug(f"Added alternative route for {actual_mode}")
                            else:
                                logger.warning(f"Route conversion returned None for {transport_mode} route {route_idx}")
                        except Exception as e:
                            logger.error(f"Error processing route {route_idx} for {transport_mode}: {e}", exc_info=True)
                            continue
                except Exception as e:
                    logger.error(f"Error processing transport mode {transport_mode}: {e}", exc_info=True)
                    continue

            # If no routes found, try with first requested mode (not always car)
            if not routes and request.transport_modes:
                first_mode = request.transport_modes[0]
                google_mode = mode_mapping.get(first_mode, "driving")
                logger.warning(f"No routes found with requested modes, trying fallback: {first_mode} ({google_mode})")

                try:
                    directions_data = await self.api_client.google_maps.get_directions(
                        origin=request.origin,
                        destination=request.destination,
                        mode=google_mode,
                        alternatives=True
                    )

                    if directions_data and directions_data.get("routes"):
                        route = await convert_google_route_to_route(
                            directions_data["routes"][0],
                            request,
                            first_mode,
                            real_time_data,
                            self.api_client
                        )
                        if route:
                            route = apply_preference_scoring(route, request.preferences)
                            routes.append(route)
                            logger.info(f"Added fallback route for {first_mode}")
                except Exception as e:
                    logger.error(f"Error in fallback route calculation: {e}", exc_info=True)

            # Sort routes by preference priority
            routes = sort_routes_by_preferences(routes, request.preferences)

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

    async def _fetch_realtime_data(self, request: RouteRequest) -> Dict:
        """Fetch real-time data if needed based on request complexity."""
        # Only fetch if we have multiple transport modes or preferences that benefit from it
        # Skip for simple single-mode requests to reduce API costs
        should_fetch_realtime = (
            len(request.transport_modes) > 1 or
            len(request.preferences) > 1 or
            'energy_efficient' in request.preferences or
            'safest' in request.preferences
        )

        if should_fetch_realtime:
            # Timeout after 3 seconds to ensure route calculation completes quickly
            try:
                real_time_data = await asyncio.wait_for(
                    self.api_client.get_all_data(request.origin, request.destination),
                    timeout=3.0
                )
            except asyncio.TimeoutError:
                logger.warning("Real-time data fetch timed out, using empty data")
                real_time_data = {
                    "weather": None,
                    "traffic": [],
                    "transit_origin": [],
                    "transit_destination": [],
                    "lime_origin": [],
                    "lime_destination": [],
                    "road_closures": [],
                    "construction": []
                }
        else:
            # Skip real-time data for simple requests to save API costs
            logger.debug("Skipping real-time data fetch for simple route request")
            real_time_data = {
                "weather": None,
                "traffic": [],
                "transit_origin": [],
                "transit_destination": [],
                "lime_origin": [],
                "lime_destination": [],
                "road_closures": [],
                "construction": []
            }

        # Get TransLink GTFS-RT real-time data (with timeout)
        translink_trip_updates = []
        translink_service_alerts = []
        if self.api_client.translink.api_key:
            try:
                # Timeout after 2 seconds for GTFS-RT data
                results = await asyncio.wait_for(
                    asyncio.gather(
                        self.api_client.translink.get_parsed_trip_updates(),
                        self.api_client.translink.get_parsed_service_alerts(),
                        return_exceptions=True
                    ),
                    timeout=2.0
                )
                # Handle exceptions from gather
                if not isinstance(results[0], Exception):
                    translink_trip_updates = results[0]
                else:
                    logger.warning(f"Could not fetch TransLink trip updates: {results[0]}")
                if not isinstance(results[1], Exception):
                    translink_service_alerts = results[1]
                else:
                    logger.warning(f"Could not fetch TransLink service alerts: {results[1]}")
                real_time_data['translink_trip_updates'] = translink_trip_updates
                real_time_data['translink_service_alerts'] = translink_service_alerts
            except asyncio.TimeoutError:
                logger.warning("TransLink GTFS-RT data fetch timed out")
            except Exception as e:
                logger.warning(f"Could not fetch TransLink GTFS-RT data: {e}")

        return real_time_data

    def _determine_actual_mode(self, google_route: Dict, transport_mode: TransportMode, google_mode: str) -> TransportMode:
        """Determine actual transport mode from Google Maps route data."""
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
        return actual_mode

    async def close(self):
        """Close API client connections."""
        await self.api_client.close()

