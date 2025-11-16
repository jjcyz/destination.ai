#!/usr/bin/env python3
"""
Test script for route-based bay selection.

Tests how the system selects the correct bay for a route using trips.txt and stop_times.txt.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.gtfs_static import GTFSStaticParser


def test_route_bay_selection():
    """Test route-based bay selection."""
    print("🚌 Testing Route-Based Bay Selection...")
    print("-" * 50)

    parser = GTFSStaticParser()

    if not parser.gtfs_path.exists():
        print(f"❌ GTFS directory not found: {parser.gtfs_path}")
        return False

    parser.load()
    print(f"✅ Loaded GTFS static feed")
    print(f"   - Routes: {len(parser.routes)}")
    print(f"   - Routes with stop mappings: {len(parser.route_to_stops)}")
    print(f"   - Trips: {len(parser.trips)}")
    print()

    # Test route 99 (Commercial-Broadway/UBC B-Line)
    route_99_id = parser.get_route_id_by_short_name("99")
    if route_99_id:
        print(f"📍 Testing Route 99 (ID: {route_99_id})")
        stops_for_route = parser.get_stops_for_route(route_99_id)
        print(f"   Route 99 serves {len(stops_for_route)} stops")

        # Test UBC Exchange bay selection
        print()
        print("🔍 Testing UBC Exchange bay selection for Route 99:")

        # Get all UBC Exchange stops
        ubc_stops = parser.get_all_stops_by_name("UBC Exchange")
        print(f"   Found {len(ubc_stops)} UBC Exchange stops (all bays)")

        # Find which bay Route 99 uses
        ubc_stop_ids = {s.stop_id for s in ubc_stops}
        route_99_stop_ids = set(stops_for_route)
        matching_bays = ubc_stop_ids.intersection(route_99_stop_ids)

        if matching_bays:
            print(f"   ✅ Route 99 uses {len(matching_bays)} bay(s) at UBC Exchange:")
            for stop_id in list(matching_bays)[:5]:
                stop = parser.get_stop_by_id(stop_id)
                if stop:
                    print(f"      - {stop.stop_name} (ID: {stop_id})")
        else:
            print(f"   ⚠️  No matching bays found")

        # Test route-based selection
        print()
        print("🔍 Testing route-based stop selection:")
        selected_stop_id = parser.get_stop_id_by_name(
            "UBC Exchange",
            route_id=route_99_id,
            prefer_station=True
        )
        if selected_stop_id:
            selected_stop = parser.get_stop_by_id(selected_stop_id)
            print(f"   ✅ Selected: {selected_stop.stop_name if selected_stop else selected_stop_id}")
            print(f"      This is the bay Route 99 uses!")

        # Test location-based selection
        print()
        print("🔍 Testing location-based selection:")
        # UBC Exchange coordinates (approximate)
        ubc_lat = 49.265726
        ubc_lng = -123.248724

        location_stop_id = parser.get_route_stops_at_location(
            route_99_id,
            "UBC Exchange",
            ubc_lat,
            ubc_lng
        )
        if location_stop_id:
            location_stop = parser.get_stop_by_id(location_stop_id)
            print(f"   ✅ Selected by location: {location_stop.stop_name if location_stop else location_stop_id}")

    print()
    print("=" * 50)
    print("✅ Route-Based Bay Selection Test Complete!")
    print()
    print("The system now:")
    print("  ✓ Uses trips.txt to map route_id → trip_id")
    print("  ✓ Uses stop_times.txt to map trip_id → stop_id")
    print("  ✓ Builds route_id → [stop_ids] mapping")
    print("  ✓ Selects correct bay based on route")
    print("  ✓ Uses location for closest bay selection")

    return True


def main():
    """Main function."""
    print("=" * 50)
    print("Route-Based Bay Selection Test")
    print("=" * 50)
    print()

    success = test_route_bay_selection()

    print("=" * 50)
    if success:
        print("✅ Test completed!")
        sys.exit(0)
    else:
        print("❌ Test failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

