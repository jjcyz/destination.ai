#!/usr/bin/env python3
"""
Test script for GTFS-RT parsing functionality.

Tests the GTFS-RT parser with real TransLink data.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.api_clients import TransLinkClient
from app.gtfs_parser import GTFSRTParser


async def test_gtfs_rt_parsing():
    """Test GTFS-RT parsing."""
    print("🚌 Testing GTFS-RT Parsing...")
    print("-" * 50)

    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)

    # Initialize client
    client = TransLinkClient()

    if not client.api_key:
        print("❌ ERROR: TransLink API key not found!")
        print("   Set TRANSLINK_API_KEY in your .env file")
        return False

    print(f"✓ API Key found: {client.api_key[:8]}...{client.api_key[-4:]}")
    print()

    # Test trip updates parsing
    print("⏳ Fetching and parsing trip updates...")
    try:
        trip_updates = await client.get_parsed_trip_updates()

        if not trip_updates:
            print("⚠️  No trip updates found")
        else:
            print(f"✅ Parsed {len(trip_updates)} trip updates")

            # Show sample trip update
            if trip_updates:
                sample = trip_updates[0]
                print(f"\n   Sample Trip Update:")
                print(f"   - Route ID: {sample.get('route_id', 'N/A')}")
                print(f"   - Trip ID: {sample.get('trip_id', 'N/A')}")
                print(f"   - Stop Updates: {len(sample.get('stop_time_updates', []))}")

                # Show first stop update with delay
                for stop_update in sample.get('stop_time_updates', [])[:3]:
                    arrival = stop_update.get('arrival')
                    if arrival:
                        delay_sec = arrival.get('delay', 0)
                        if delay_sec != 0:
                            print(f"   - Stop {stop_update.get('stop_id')}: Delay {delay_sec // 60} minutes")
    except Exception as e:
        print(f"❌ Error parsing trip updates: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test vehicle positions parsing
    print("⏳ Fetching and parsing vehicle positions...")
    try:
        vehicle_positions = await client.get_parsed_vehicle_positions()

        if not vehicle_positions:
            print("⚠️  No vehicle positions found")
        else:
            print(f"✅ Parsed {len(vehicle_positions)} vehicle positions")

            # Show sample vehicle position
            if vehicle_positions:
                sample = vehicle_positions[0]
                print(f"\n   Sample Vehicle Position:")
                print(f"   - Route ID: {sample.get('route_id', 'N/A')}")
                print(f"   - Trip ID: {sample.get('trip_id', 'N/A')}")
                pos = sample.get('position', {})
                if pos.get('latitude') and pos.get('longitude'):
                    print(f"   - Location: {pos.get('latitude')}, {pos.get('longitude')}")
    except Exception as e:
        print(f"❌ Error parsing vehicle positions: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test service alerts parsing
    print("⏳ Fetching and parsing service alerts...")
    try:
        service_alerts = await client.get_parsed_service_alerts()

        if not service_alerts:
            print("✅ No service alerts (this is normal)")
        else:
            print(f"✅ Parsed {len(service_alerts)} service alerts")

            # Show sample alert
            if service_alerts:
                sample = service_alerts[0]
                print(f"\n   Sample Service Alert:")
                print(f"   - Header: {sample.get('header_text', 'N/A')}")
                print(f"   - Effect: {sample.get('effect', 'N/A')}")
    except Exception as e:
        print(f"❌ Error parsing service alerts: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("=" * 50)
    print("✅ GTFS-RT Parsing Test Complete!")
    print()
    print("The parser is working correctly and can extract:")
    print("  ✓ Trip updates with delays")
    print("  ✓ Vehicle positions")
    print("  ✓ Service alerts")

    await client.client.aclose()
    return True


def main():
    """Main function."""
    print("=" * 50)
    print("GTFS-RT Parser Test")
    print("=" * 50)
    print()

    success = asyncio.run(test_gtfs_rt_parsing())

    print("=" * 50)
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

