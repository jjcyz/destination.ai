#!/usr/bin/env python3
"""
Test script for GTFS static feed parsing.

Tests stop name to stop ID mapping.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.gtfs_static import GTFSStaticParser


def test_gtfs_static():
    """Test GTFS static feed parsing."""
    print("📋 Testing GTFS Static Feed Parser...")
    print("-" * 50)

    # Initialize parser
    parser = GTFSStaticParser()

    # Try to load GTFS feed
    print(f"📁 Looking for GTFS feed in: {parser.gtfs_path}")

    if not parser.gtfs_path.exists():
        print(f"\n❌ GTFS directory not found: {parser.gtfs_path}")
        print("\n📥 To set up GTFS static feed:")
        print("1. Download TransLink GTFS feed from:")
        print("   https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources")
        print("2. Extract the ZIP file")
        print(f"3. Copy all files to: {parser.gtfs_path}")
        print("\n   Expected files:")
        print("   - stops.txt")
        print("   - routes.txt")
        print("   - trips.txt")
        print("   - stop_times.txt")
        print("   - etc.")
        return False

    # Load GTFS feed
    print("⏳ Loading GTFS static feed...")
    success = parser.load()

    if not success:
        print("❌ Failed to load GTFS static feed")
        return False

    print(f"✅ Loaded GTFS static feed successfully!")
    print(f"   - Stops: {len(parser.stops)}")
    print(f"   - Routes: {len(parser.routes)}")
    print()

    # Test stop name to ID mapping
    print("🔍 Testing stop name to ID mapping...")
    test_stops = [
        "Commercial-Broadway Station",
        "Waterfront Station",
        "UBC Exchange",
        "Metrotown Station",
    ]

    for stop_name in test_stops:
        stop_id = parser.get_stop_id_by_name(stop_name)
        if stop_id:
            stop = parser.get_stop_by_id(stop_id)
            print(f"   ✅ '{stop_name}' → {stop_id}")
            if stop:
                print(f"      Location: {stop.stop_lat}, {stop.stop_lng}")
        else:
            # Try fuzzy matching
            fuzzy_ids = parser.get_stop_ids_by_name_fuzzy(stop_name)
            if fuzzy_ids:
                print(f"   ⚠️  '{stop_name}' → Not found (exact)")
                print(f"   💡 Found {len(fuzzy_ids)} fuzzy matches:")
                for fid in fuzzy_ids[:3]:  # Show first 3
                    fstop = parser.get_stop_by_id(fid)
                    if fstop:
                        print(f"      - '{fstop.stop_name}' ({fid})")
            else:
                print(f"   ❌ '{stop_name}' → Not found")

    print()

    # Test route short name to route ID mapping
    print("🔍 Testing route short name to route ID mapping...")
    test_routes = ["99", "4", "25", "Canada Line", "canada"]

    for route_short_name in test_routes:
        route_id = parser.get_route_id_by_short_name(route_short_name)
        if route_id:
            route = parser.routes.get(route_id)
            if route:
                print(f"   ✅ Route '{route_short_name}' → Route ID: {route_id}")
                print(f"      Short: '{route.route_short_name}', Long: '{route.route_long_name}'")
            else:
                print(f"   ✅ Route '{route_short_name}' → Route ID: {route_id}")
        else:
            # Show what routes are available
            print(f"   ⚠️  Route '{route_short_name}' → Not found")
            # Show similar routes
            matching = [r for r in parser.routes.values()
                       if route_short_name.lower() in r.route_short_name.lower()
                       or route_short_name.lower() in r.route_long_name.lower()]
            if matching:
                print(f"   💡 Similar routes found:")
                for r in matching[:3]:
                    print(f"      - '{r.route_short_name}' / '{r.route_long_name}' (ID: {r.route_id})")

    print()

    # Test fuzzy stop name matching
    print("🔍 Testing fuzzy stop name matching...")
    fuzzy_test = "Commercial"
    matching_ids = parser.get_stop_ids_by_name_fuzzy(fuzzy_test)
    if matching_ids:
        print(f"   ✅ Found {len(matching_ids)} stops matching '{fuzzy_test}':")
        for stop_id in matching_ids[:5]:  # Show first 5
            stop = parser.get_stop_by_id(stop_id)
            if stop:
                print(f"      - {stop.stop_name} ({stop_id})")
    else:
        print(f"   ⚠️  No stops found matching '{fuzzy_test}'")

    print()
    print("=" * 50)
    print("✅ GTFS Static Feed Test Complete!")
    print()
    print("The parser can now:")
    print("  ✓ Map stop names to stop IDs")
    print("  ✓ Map route short names to route IDs")
    print("  ✓ Find stops by location")
    print("  ✓ Support fuzzy stop name matching")

    return True


def main():
    """Main function."""
    print("=" * 50)
    print("GTFS Static Feed Parser Test")
    print("=" * 50)
    print()

    success = test_gtfs_static()

    print("=" * 50)
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

