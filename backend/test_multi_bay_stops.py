#!/usr/bin/env python3
"""
Test script for multi-bay stop handling.

Tests how the system handles stops with multiple bays like "UBC Exchange @ Bay 9".
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.gtfs_static import GTFSStaticParser


def test_multi_bay_stops():
    """Test multi-bay stop handling."""
    print("🚌 Testing Multi-Bay Stop Handling...")
    print("-" * 50)

    parser = GTFSStaticParser()

    if not parser.gtfs_path.exists():
        print(f"❌ GTFS directory not found: {parser.gtfs_path}")
        return False

    parser.load()
    print(f"✅ Loaded {len(parser.stops)} stops")
    print()

    # Test stops with multiple bays
    test_cases = [
        "UBC Exchange",
        "Commercial-Broadway Station",
        "Metrotown Station",
        "Waterfront Station",
    ]

    for stop_name in test_cases:
        print(f"📍 Testing: {stop_name}")

        # Get all matching stops
        all_stops = parser.get_all_stops_by_name(stop_name)

        if not all_stops:
            print(f"   ❌ No stops found")
            continue

        print(f"   Found {len(all_stops)} matching stop(s):")

        # Group by bay/type
        stations = [s for s in all_stops if s.location_type == 1]
        bays = [s for s in all_stops if s.location_type == 0 and '@ Bay' in s.stop_name]
        other = [s for s in all_stops if s not in stations and s not in bays]

        if stations:
            print(f"   🏢 Station stops ({len(stations)}):")
            for stop in stations[:3]:  # Show first 3
                print(f"      - {stop.stop_name} (ID: {stop.stop_id})")

        if bays:
            print(f"   🚏 Bay stops ({len(bays)}):")
            for stop in bays[:5]:  # Show first 5
                print(f"      - {stop.stop_name} (ID: {stop.stop_id})")
            if len(bays) > 5:
                print(f"      ... and {len(bays) - 5} more")

        if other:
            print(f"   📍 Other stops ({len(other)}):")
            for stop in other[:3]:
                print(f"      - {stop.stop_name} (ID: {stop.stop_id})")

        # Test selection
        selected = parser.get_stop_id_by_name(stop_name, prefer_station=True)
        if selected:
            selected_stop = parser.get_stop_by_id(selected)
            print(f"   ✅ Selected: {selected_stop.stop_name if selected_stop else selected} (ID: {selected})")
            if selected_stop:
                print(f"      Type: {'Station' if selected_stop.location_type == 1 else 'Stop/Bay'}")

        print()

    print("=" * 50)
    print("💡 Multi-Bay Stop Handling Strategy:")
    print()
    print("When Google Maps provides a stop name without bay info:")
    print("1. Find all matching stops (including all bays)")
    print("2. Prefer station stops (location_type=1) over bay stops")
    print("3. If multiple bays, select first match")
    print()
    print("Future improvements:")
    print("- Match by route (requires trips.txt)")
    print("- Select closest bay to route path")
    print("- Use stop_times.txt to find which bay serves which route")

    return True


def main():
    """Main function."""
    print("=" * 50)
    print("Multi-Bay Stop Handling Test")
    print("=" * 50)
    print()

    success = test_multi_bay_stops()

    print("=" * 50)
    if success:
        print("✅ Test completed!")
        sys.exit(0)
    else:
        print("❌ Test failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

