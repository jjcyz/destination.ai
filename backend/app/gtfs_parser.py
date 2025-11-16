"""
GTFS-RT (GTFS Realtime) parser for TransLink transit data.

Parses Protocol Buffer feeds to extract real-time transit information
including trip updates, vehicle positions, and service alerts.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

try:
    from google.transit import gtfs_realtime_pb2
except ImportError:
    # Fallback if gtfs-realtime-bindings is not installed
    gtfs_realtime_pb2 = None

from .models import TransitData, Point

logger = logging.getLogger(__name__)

# Global GTFS static parser instance (lazy loaded)
_gtfs_static = None


def get_gtfs_static():
    """Get or create GTFS static parser instance."""
    global _gtfs_static
    if _gtfs_static is None:
        try:
            from .gtfs_static import GTFSStaticParser
            _gtfs_static = GTFSStaticParser()
            _gtfs_static.load()
        except ImportError:
            logger.debug("GTFS static parser not available")
            return None
    return _gtfs_static


class GTFSRTParser:
    """Parser for GTFS-RT Protocol Buffer feeds."""

    @staticmethod
    def parse_trip_updates(feed_data: bytes) -> List[Dict]:
        """
        Parse GTFS-RT trip updates feed.

        Args:
            feed_data: Raw Protocol Buffer bytes from GTFS-RT feed

        Returns:
            List of trip update dictionaries with real-time information
        """
        if gtfs_realtime_pb2 is None:
            logger.error("gtfs-realtime-bindings not installed. Install with: pip install gtfs-realtime-bindings")
            return []

        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)

            trip_updates = []

            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip_update = entity.trip_update
                    trip = trip_update.trip

                    # Extract trip information
                    trip_info = {
                        'trip_id': trip.trip_id,
                        'route_id': trip.route_id,
                        'direction_id': trip.direction_id if trip.HasField('direction_id') else None,
                        'start_time': trip.start_time if trip.HasField('start_time') else None,
                        'start_date': trip.start_date if trip.HasField('start_date') else None,
                        'schedule_relationship': trip.schedule_relationship,
                        'stop_time_updates': []
                    }

                    # Extract stop time updates (arrival/departure times)
                    for stop_time_update in trip_update.stop_time_update:
                        stop_update = {
                            'stop_sequence': stop_time_update.stop_sequence if stop_time_update.HasField('stop_sequence') else None,
                            'stop_id': stop_time_update.stop_id,
                            'arrival': None,
                            'departure': None,
                            'schedule_relationship': stop_time_update.schedule_relationship if stop_time_update.HasField('schedule_relationship') else None,
                        }

                        # Extract arrival time
                        if stop_time_update.HasField('arrival'):
                            arrival = stop_time_update.arrival
                            stop_update['arrival'] = {
                                'delay': arrival.delay if arrival.HasField('delay') else 0,
                                'time': arrival.time if arrival.HasField('time') else None,
                                'uncertainty': arrival.uncertainty if arrival.HasField('uncertainty') else None,
                            }

                        # Extract departure time
                        if stop_time_update.HasField('departure'):
                            departure = stop_time_update.departure
                            stop_update['departure'] = {
                                'delay': departure.delay if departure.HasField('delay') else 0,
                                'time': departure.time if departure.HasField('time') else None,
                                'uncertainty': departure.uncertainty if departure.HasField('uncertainty') else None,
                            }

                        trip_info['stop_time_updates'].append(stop_update)

                    trip_updates.append(trip_info)

            logger.info(f"Parsed {len(trip_updates)} trip updates from GTFS-RT feed")
            return trip_updates

        except Exception as e:
            logger.error(f"Error parsing GTFS-RT trip updates: {e}")
            return []

    @staticmethod
    def parse_vehicle_positions(feed_data: bytes) -> List[Dict]:
        """
        Parse GTFS-RT vehicle positions feed.

        Args:
            feed_data: Raw Protocol Buffer bytes from GTFS-RT feed

        Returns:
            List of vehicle position dictionaries
        """
        if gtfs_realtime_pb2 is None:
            logger.error("gtfs-realtime-bindings not installed. Install with: pip install gtfs-realtime-bindings")
            return []

        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)

            vehicle_positions = []

            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    vehicle = entity.vehicle
                    trip = vehicle.trip
                    position = vehicle.position

                    vehicle_info = {
                        'vehicle_id': vehicle.vehicle.id if vehicle.HasField('vehicle') and vehicle.vehicle.HasField('id') else None,
                        'trip_id': trip.trip_id if trip.HasField('trip_id') else None,
                        'route_id': trip.route_id if trip.HasField('route_id') else None,
                        'direction_id': trip.direction_id if trip.HasField('direction_id') else None,
                        'position': {
                            'latitude': position.latitude if position.HasField('latitude') else None,
                            'longitude': position.longitude if position.HasField('longitude') else None,
                            'bearing': position.bearing if position.HasField('bearing') else None,
                            'speed': position.speed if position.HasField('speed') else None,
                        },
                        'current_stop_sequence': vehicle.current_stop_sequence if vehicle.HasField('current_stop_sequence') else None,
                        'current_status': vehicle.current_status if vehicle.HasField('current_status') else None,
                        'timestamp': vehicle.timestamp if vehicle.HasField('timestamp') else None,
                        'congestion_level': vehicle.congestion_level if vehicle.HasField('congestion_level') else None,
                        'occupancy_status': vehicle.occupancy_status if vehicle.HasField('occupancy_status') else None,
                    }

                    vehicle_positions.append(vehicle_info)

            logger.info(f"Parsed {len(vehicle_positions)} vehicle positions from GTFS-RT feed")
            return vehicle_positions

        except Exception as e:
            logger.error(f"Error parsing GTFS-RT vehicle positions: {e}")
            return []

    @staticmethod
    def parse_service_alerts(feed_data: bytes) -> List[Dict]:
        """
        Parse GTFS-RT service alerts feed.

        Args:
            feed_data: Raw Protocol Buffer bytes from GTFS-RT feed

        Returns:
            List of service alert dictionaries
        """
        if gtfs_realtime_pb2 is None:
            logger.error("gtfs-realtime-bindings not installed. Install with: pip install gtfs-realtime-bindings")
            return []

        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)

            service_alerts = []

            for entity in feed.entity:
                if entity.HasField('alert'):
                    alert = entity.alert

                    alert_info = {
                        'alert_id': entity.id,
                        'active_period': [],
                        'informed_entity': [],
                        'cause': alert.cause if alert.HasField('cause') else None,
                        'effect': alert.effect if alert.HasField('effect') else None,
                        'url': None,
                        'header_text': None,
                        'description_text': None,
                    }

                    # Extract active periods
                    for period in alert.active_period:
                        alert_info['active_period'].append({
                            'start': period.start if period.HasField('start') else None,
                            'end': period.end if period.HasField('end') else None,
                        })

                    # Extract informed entities (routes, stops affected)
                    for entity_info in alert.informed_entity:
                        informed = {}
                        if entity_info.HasField('agency_id'):
                            informed['agency_id'] = entity_info.agency_id
                        if entity_info.HasField('route_id'):
                            informed['route_id'] = entity_info.route_id
                        if entity_info.HasField('route_type'):
                            informed['route_type'] = entity_info.route_type
                        if entity_info.HasField('stop_id'):
                            informed['stop_id'] = entity_info.stop_id
                        alert_info['informed_entity'].append(informed)

                    # Extract URL
                    if alert.HasField('url'):
                        url_translation = alert.url
                        alert_info['url'] = url_translation.translation[0].text if url_translation.translation else None

                    # Extract header text
                    if alert.HasField('header_text'):
                        header_translation = alert.header_text
                        alert_info['header_text'] = header_translation.translation[0].text if header_translation.translation else None

                    # Extract description text
                    if alert.HasField('description_text'):
                        desc_translation = alert.description_text
                        alert_info['description_text'] = desc_translation.translation[0].text if desc_translation.translation else None

                    service_alerts.append(alert_info)

            logger.info(f"Parsed {len(service_alerts)} service alerts from GTFS-RT feed")
            return service_alerts

        except Exception as e:
            logger.error(f"Error parsing GTFS-RT service alerts: {e}")
            return []

    @staticmethod
    def get_stop_arrival_time(
        trip_updates: List[Dict],
        route_id: str,
        stop_identifier: str,
        current_time: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Get real-time arrival information for a specific stop and route.

        Args:
            trip_updates: Parsed trip updates from GTFS-RT feed
            route_id: GTFS route ID (e.g., "99")
            stop_identifier: GTFS stop ID or stop name
            current_time: Current time for filtering (defaults to now)

        Returns:
            Dictionary with arrival time and delay information, or None
        """
        if current_time is None:
            current_time = datetime.now()

        # Try to resolve stop name to stop ID using GTFS static feed
        stop_id = stop_identifier
        gtfs_static = get_gtfs_static()

        if gtfs_static:
            # If stop_identifier looks like a name (not a numeric ID), try to resolve it
            if not stop_identifier.isdigit() and not stop_identifier.startswith('stop_'):
                # Use route-based selection (uses trips.txt and stop_times.txt)
                resolved_id = gtfs_static.get_stop_id_by_name(
                    stop_identifier,
                    route_id=route_id,
                    prefer_station=True
                )
                if resolved_id:
                    stop_id = resolved_id
                    logger.debug(
                        f"Mapped stop name '{stop_identifier}' to stop ID '{stop_id}' "
                        f"(route: {route_id}, route-based selection)"
                    )
                else:
                    # Fallback: try to find all matching stops
                    all_matching = gtfs_static.get_all_stops_by_name(stop_identifier)
                    if all_matching:
                        stop_id = all_matching[0].stop_id
                        logger.debug(
                            f"Mapped stop name '{stop_identifier}' to stop ID '{stop_id}' "
                            f"(found {len(all_matching)} matches, using first)"
                        )

        # Get all matching stop IDs if we have multiple bays
        stop_ids_to_try = [stop_id]
        if gtfs_static:
            all_matching_stops = gtfs_static.get_all_stops_by_name(stop_identifier)
            if len(all_matching_stops) > 1:
                # Try all matching stops (for multi-bay stops)
                stop_ids_to_try = [s.stop_id for s in all_matching_stops]
                logger.debug(f"Trying {len(stop_ids_to_try)} stop IDs for '{stop_identifier}'")

        # Find matching trip updates for this route
        for trip_update in trip_updates:
            if trip_update.get('route_id') != route_id:
                continue

            # Check stop time updates
            for stop_update in trip_update.get('stop_time_updates', []):
                update_stop_id = stop_update.get('stop_id')

                # Match by stop ID (try all matching stops for multi-bay locations)
                if update_stop_id in stop_ids_to_try:
                    arrival = stop_update.get('arrival')
                    departure = stop_update.get('departure')

                    # Prefer arrival, fallback to departure
                    time_info = arrival if arrival else departure
                    if time_info:
                        delay_seconds = time_info.get('delay', 0)
                        scheduled_time = time_info.get('time')

                        if scheduled_time:
                            # Convert Unix timestamp to datetime
                            scheduled_dt = datetime.fromtimestamp(scheduled_time)
                            actual_dt = scheduled_dt + timedelta(seconds=delay_seconds)

                            return {
                                'scheduled_time': scheduled_dt,
                                'actual_time': actual_dt,
                                'delay_seconds': delay_seconds,
                                'delay_minutes': delay_seconds // 60,
                                'is_delayed': delay_seconds > 0,
                                'trip_id': trip_update.get('trip_id'),
                                'stop_id': update_stop_id,
                            }

        return None

    @staticmethod
    def get_route_delays(trip_updates: List[Dict], route_id: str) -> List[Dict]:
        """
        Get all delays for a specific route.

        Args:
            trip_updates: Parsed trip updates from GTFS-RT feed
            route_id: GTFS route ID

        Returns:
            List of delay information for stops on this route
        """
        delays = []

        for trip_update in trip_updates:
            if trip_update.get('route_id') != route_id:
                continue

            for stop_update in trip_update.get('stop_time_updates', []):
                arrival = stop_update.get('arrival')
                departure = stop_update.get('departure')

                time_info = arrival if arrival else departure
                if time_info and time_info.get('delay', 0) != 0:
                    delays.append({
                        'stop_id': stop_update.get('stop_id'),
                        'delay_seconds': time_info.get('delay', 0),
                        'delay_minutes': time_info.get('delay', 0) // 60,
                        'trip_id': trip_update.get('trip_id'),
                    })

        return delays

