"""
Graph builder for the Vancouver route recommendation system.
Creates and manages the graph of streets, paths, and transit routes.
"""

import networkx as nx
from typing import List, Dict, Set, Tuple, Optional
import logging
from datetime import datetime
import asyncio

# Optional imports with fallbacks
try:
    import osmnx as ox
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False
    logging.warning("OSMnx not available. Using fallback network generation.")

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logging.warning("GeoPandas not available. Using basic coordinate handling.")

from .models import (
    Node, Edge, Point, TransportMode, WeatherData, TrafficData,
    TransitData, BikeScooterData
)
from .api_clients import APIClientManager
from .config import settings

logger = logging.getLogger(__name__)


class VancouverGraphBuilder:
    """Builds and manages the routing graph for Vancouver."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.api_client = APIClientManager()

        # Vancouver bounding box
        self.bounds = settings.vancouver_bounds

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

    async def build_graph(self, center_point: Point, radius: int = 5000) -> nx.MultiDiGraph:
        """
        Build the routing graph for Vancouver.

        Args:
            center_point: Center point for the graph
            radius: Radius in meters to include

        Returns:
            NetworkX MultiDiGraph with nodes and edges
        """
        logger.info(f"Building graph for Vancouver centered at {center_point}")

        try:
            # Download street network from OpenStreetMap
            await self._build_street_network(center_point, radius)

            # Add transit stops and routes
            await self._add_transit_network(center_point, radius)

            # Add bike/scooter sharing stations
            await self._add_shared_mobility_stations(center_point, radius)

            # Add pedestrian paths and bike lanes
            await self._add_pedestrian_bike_network(center_point, radius)

            # Update edge costs with real-time data
            await self._update_edge_costs()

            logger.info(f"Graph built with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
            return self.graph

        except Exception as e:
            logger.error(f"Error building graph: {e}")
            raise

    async def _build_street_network(self, center_point: Point, radius: int):
        """Build the street network using OpenStreetMap data."""
        if not OSMNX_AVAILABLE:
            logger.warning("OSMnx not available, using fallback network")
            await self._create_fallback_network(center_point, radius)
            return

        try:
            # Configure OSMnx for Vancouver
            ox.config(use_cache=True, log_console=False)

            # Download street network
            graph = ox.graph_from_point(
                (center_point.lat, center_point.lng),
                dist=radius,
                network_type='drive',  # Includes all driveable roads
                simplify=True
            )

            # Convert to our graph format
            for node_id, data in graph.nodes(data=True):
                if 'x' in data and 'y' in data:
                    # Convert from UTM to lat/lng
                    if GEOPANDAS_AVAILABLE:
                        from shapely.geometry import Point as ShapelyPoint
                        point_geom = ShapelyPoint(data['x'], data['y'])
                        lat, lng = ox.projection.project_geometry(
                            point_geom,
                            from_crs=graph.graph['crs'],
                            to_crs='EPSG:4326'
                        ).centroid.coords[0]
                    else:
                        # Simple approximation for demo purposes
                        lat = center_point.lat + (data['y'] - center_point.lat) * 0.00001
                        lng = center_point.lng + (data['x'] - center_point.lng) * 0.00001

                    node = Node(
                        id=str(node_id),
                        point=Point(lat=lat, lng=lng),
                        node_type="intersection",
                        elevation=data.get('elevation', 0)
                    )

                    self.nodes[str(node_id)] = node
                    self.graph.add_node(str(node_id), **node.dict())

            # Add edges
            for u, v, key, data in graph.edges(data=True, keys=True):
                if str(u) in self.nodes and str(v) in self.nodes:
                    # Determine allowed modes based on road type
                    allowed_modes = self._get_allowed_modes(data)

                    # Calculate distance
                    from_node = self.nodes[str(u)]
                    to_node = self.nodes[str(v)]
                    distance = from_node.point.distance_to(to_node.point)

                    edge = Edge(
                        id=f"{u}_{v}_{key}",
                        from_node=str(u),
                        to_node=str(v),
                        distance=distance,
                        allowed_modes=allowed_modes,
                        is_bike_lane=self._has_bike_lane(data),
                        is_sidewalk=True,  # Assume sidewalks exist
                        has_transit_service=self._has_transit_service(data)
                    )

                    self.edges[edge.id] = edge
                    self.graph.add_edge(str(u), str(v), key=key, **edge.dict())

            logger.info(f"Added {len(self.nodes)} street nodes and {len(self.edges)} street edges")

        except Exception as e:
            logger.error(f"Error building street network: {e}")
            # Fallback: create a simple grid
            await self._create_fallback_network(center_point, radius)

    def _get_allowed_modes(self, road_data: Dict) -> List[TransportMode]:
        """Determine allowed transport modes for a road segment."""
        allowed_modes = [TransportMode.WALKING]  # Always allow walking

        highway = road_data.get('highway', '')
        access = road_data.get('access', '')

        # Car access
        if highway in ['primary', 'secondary', 'tertiary', 'residential', 'trunk', 'motorway']:
            if access != 'no':
                allowed_modes.append(TransportMode.CAR)

        # Bike access
        if highway in ['primary', 'secondary', 'tertiary', 'residential', 'cycleway', 'path']:
            if access != 'no':
                allowed_modes.append(TransportMode.BIKING)

        # Scooter access (similar to bike but more restrictive)
        if highway in ['tertiary', 'residential', 'cycleway', 'path']:
            if access != 'no':
                allowed_modes.append(TransportMode.SCOOTER)

        return allowed_modes

    def _has_bike_lane(self, road_data: Dict) -> bool:
        """Check if road has bike lane."""
        return (
            road_data.get('highway') == 'cycleway' or
            'cycleway' in road_data or
            'bicycle' in road_data.get('access', '')
        )

    def _has_transit_service(self, road_data: Dict) -> bool:
        """Check if road has transit service."""
        return (
            road_data.get('highway') in ['primary', 'secondary', 'tertiary'] or
            'bus' in road_data.get('public_transport', '')
        )

    async def _add_transit_network(self, center_point: Point, radius: int):
        """Add transit stops and routes to the graph."""
        try:
            # Get nearby transit stops
            transit_stops = await self.api_client.translink.get_nearby_stops(center_point, radius)

            for stop in transit_stops:
                # Create transit stop node
                node = Node(
                    id=f"transit_{stop.stop_id}",
                    point=Point(lat=stop.location.lat, lng=stop.location.lng),
                    node_type="transit_stop",
                    name=stop.stop_name,
                    accessibility_features=["wheelchair"] if stop.accessibility else []
                )

                self.nodes[node.id] = node
                self.graph.add_node(node.id, **node.dict())

                # Connect to nearest street nodes
                await self._connect_transit_to_streets(node)

            logger.info(f"Added {len(transit_stops)} transit stops")

        except Exception as e:
            logger.error(f"Error adding transit network: {e}")

    async def _add_shared_mobility_stations(self, center_point: Point, radius: int):
        """Add bike/scooter sharing stations to the graph."""
        try:
            # Get Lime vehicles
            lime_vehicles = await self.api_client.lime.get_available_vehicles(center_point, radius)

            for vehicle in lime_vehicles:
                if vehicle.available_bikes > 0 or vehicle.available_scooters > 0:
                    # Create shared mobility node
                    node = Node(
                        id=f"lime_{vehicle.station_id}",
                        point=vehicle.location,
                        node_type="shared_mobility",
                        name=f"Lime Station {vehicle.station_id}"
                    )

                    self.nodes[node.id] = node
                    self.graph.add_node(node.id, **node.dict())

                    # Connect to nearest street nodes
                    await self._connect_shared_mobility_to_streets(node)

            logger.info(f"Added {len(lime_vehicles)} shared mobility stations")

        except Exception as e:
            logger.error(f"Error adding shared mobility stations: {e}")

    async def _add_pedestrian_bike_network(self, center_point: Point, radius: int):
        """Add pedestrian paths and bike lanes to the graph."""
        if not OSMNX_AVAILABLE:
            logger.warning("OSMnx not available, skipping pedestrian network")
            return

        try:
            # Download pedestrian network
            ped_graph = ox.graph_from_point(
                (center_point.lat, center_point.lng),
                dist=radius,
                network_type='walk',
                simplify=True
            )

            # Add pedestrian-specific nodes and edges
            for node_id, data in ped_graph.nodes(data=True):
                if 'x' in data and 'y' in data and str(node_id) not in self.nodes:
                    if GEOPANDAS_AVAILABLE:
                        from shapely.geometry import Point as ShapelyPoint
                        point_geom = ShapelyPoint(data['x'], data['y'])
                        lat, lng = ox.projection.project_geometry(
                            point_geom,
                            from_crs=ped_graph.graph['crs'],
                            to_crs='EPSG:4326'
                        ).centroid.coords[0]
                    else:
                        # Simple approximation
                        lat = center_point.lat + (data['y'] - center_point.lat) * 0.00001
                        lng = center_point.lng + (data['x'] - center_point.lng) * 0.00001

                    node = Node(
                        id=f"ped_{node_id}",
                        point=Point(lat=lat, lng=lng),
                        node_type="pedestrian_path"
                    )

                    self.nodes[node.id] = node
                    self.graph.add_node(node.id, **node.dict())

            # Add pedestrian edges
            for u, v, key, data in ped_graph.edges(data=True, keys=True):
                if f"ped_{u}" in self.nodes and f"ped_{v}" in self.nodes:
                    from_node = self.nodes[f"ped_{u}"]
                    to_node = self.nodes[f"ped_{v}"]
                    distance = from_node.point.distance_to(to_node.point)

                    edge = Edge(
                        id=f"ped_{u}_{v}_{key}",
                        from_node=f"ped_{u}",
                        to_node=f"ped_{v}",
                        distance=distance,
                        allowed_modes=[TransportMode.WALKING, TransportMode.BIKING],
                        is_sidewalk=True
                    )

                    self.edges[edge.id] = edge
                    self.graph.add_edge(f"ped_{u}", f"ped_{v}", key=key, **edge.dict())

            logger.info("Added pedestrian and bike network")

        except Exception as e:
            logger.error(f"Error adding pedestrian/bike network: {e}")

    async def _connect_transit_to_streets(self, transit_node: Node):
        """Connect transit stops to nearest street nodes."""
        min_distance = float('inf')
        nearest_street_node = None

        for node_id, node in self.nodes.items():
            if node.node_type == "intersection":
                distance = transit_node.point.distance_to(node.point)
                if distance < min_distance and distance < 200:  # Within 200m
                    min_distance = distance
                    nearest_street_node = node_id

        if nearest_street_node:
            # Create walking connection
            distance = transit_node.point.distance_to(self.nodes[nearest_street_node].point)
            edge = Edge(
                id=f"transit_walk_{transit_node.id}_{nearest_street_node}",
                from_node=transit_node.id,
                to_node=nearest_street_node,
                distance=distance,
                allowed_modes=[TransportMode.WALKING]
            )

            self.edges[edge.id] = edge
            self.graph.add_edge(transit_node.id, nearest_street_node, **edge.dict())

            # Reverse edge
            reverse_edge = Edge(
                id=f"transit_walk_{nearest_street_node}_{transit_node.id}",
                from_node=nearest_street_node,
                to_node=transit_node.id,
                distance=distance,
                allowed_modes=[TransportMode.WALKING]
            )

            self.edges[reverse_edge.id] = reverse_edge
            self.graph.add_edge(nearest_street_node, transit_node.id, **reverse_edge.dict())

    async def _connect_shared_mobility_to_streets(self, mobility_node: Node):
        """Connect shared mobility stations to nearest street nodes."""
        min_distance = float('inf')
        nearest_street_node = None

        for node_id, node in self.nodes.items():
            if node.node_type == "intersection":
                distance = mobility_node.point.distance_to(node.point)
                if distance < min_distance and distance < 100:  # Within 100m
                    min_distance = distance
                    nearest_street_node = node_id

        if nearest_street_node:
            # Create walking connection
            distance = mobility_node.point.distance_to(self.nodes[nearest_street_node].point)
            edge = Edge(
                id=f"mobility_walk_{mobility_node.id}_{nearest_street_node}",
                from_node=mobility_node.id,
                to_node=nearest_street_node,
                distance=distance,
                allowed_modes=[TransportMode.WALKING]
            )

            self.edges[edge.id] = edge
            self.graph.add_edge(mobility_node.id, nearest_street_node, **edge.dict())

    async def _update_edge_costs(self):
        """Update edge costs with real-time data."""
        try:
            # Get real-time data
            # This would be called with actual origin/destination points
            # For now, we'll use default values

            for edge_id, edge in self.edges.items():
                # Update with default values
                edge.current_traffic_speed = self.mode_speeds.get(edge.allowed_modes[0], 20.0)
                edge.weather_penalty = 1.0
                edge.event_penalty = 1.0

                # Calculate energy costs
                for mode in edge.allowed_modes:
                    if mode == TransportMode.WALKING:
                        edge.energy_cost[mode] = edge.distance * 0.1  # Low energy cost
                    elif mode == TransportMode.BIKING:
                        edge.energy_cost[mode] = edge.distance * 0.05  # Very low energy cost
                    elif mode == TransportMode.CAR:
                        edge.energy_cost[mode] = edge.distance * 0.5  # High energy cost
                    else:
                        edge.energy_cost[mode] = edge.distance * 0.2  # Medium energy cost

            logger.info("Updated edge costs with real-time data")

        except Exception as e:
            logger.error(f"Error updating edge costs: {e}")

    async def _create_fallback_network(self, center_point: Point, radius: int):
        """Create a simple fallback network if OSM data fails."""
        logger.warning("Creating fallback network due to OSM data failure")

        # Create a simple grid network
        grid_size = 100  # meters
        lat_step = grid_size / 111000  # Approximate degrees per meter
        lng_step = grid_size / (111000 * abs(center_point.lat))

        nodes_created = 0
        for i in range(-radius//grid_size, radius//grid_size + 1):
            for j in range(-radius//grid_size, radius//grid_size + 1):
                lat = center_point.lat + i * lat_step
                lng = center_point.lng + j * lng_step

                # Check if within bounds
                if (self.bounds["south"] <= lat <= self.bounds["north"] and
                    self.bounds["west"] <= lng <= self.bounds["east"]):

                    node = Node(
                        id=f"grid_{i}_{j}",
                        point=Point(lat=lat, lng=lng),
                        node_type="intersection"
                    )

                    self.nodes[node.id] = node
                    self.graph.add_node(node.id, **node.dict())
                    nodes_created += 1

        # Connect grid nodes
        for node_id, node in self.nodes.items():
            if node_id.startswith("grid_"):
                i, j = map(int, node_id.split("_")[1:])

                # Connect to adjacent nodes
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor_id = f"grid_{i+di}_{j+dj}"
                    if neighbor_id in self.nodes:
                        neighbor = self.nodes[neighbor_id]
                        distance = node.point.distance_to(neighbor.point)

                        edge = Edge(
                            id=f"{node_id}_{neighbor_id}",
                            from_node=node_id,
                            to_node=neighbor_id,
                            distance=distance,
                            allowed_modes=[TransportMode.WALKING, TransportMode.BIKING, TransportMode.CAR]
                        )

                        self.edges[edge.id] = edge
                        self.graph.add_edge(node_id, neighbor_id, **edge.dict())

        logger.info(f"Created fallback network with {nodes_created} nodes")

    def get_nearest_node(self, point: Point, node_type: Optional[str] = None) -> Optional[str]:
        """Find the nearest node to a given point."""
        min_distance = float('inf')
        nearest_node = None

        for node_id, node in self.nodes.items():
            if node_type is None or node.node_type == node_type:
                distance = point.distance_to(node.point)
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node_id

        return nearest_node

    def get_nodes_in_radius(self, point: Point, radius: float) -> List[str]:
        """Get all nodes within a given radius of a point."""
        nodes_in_radius = []

        for node_id, node in self.nodes.items():
            distance = point.distance_to(node.point)
            if distance <= radius:
                nodes_in_radius.append(node_id)

        return nodes_in_radius

    async def close(self):
        """Close API client connections."""
        await self.api_client.close()
