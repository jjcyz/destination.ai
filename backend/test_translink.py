#!/usr/bin/env python3
"""
Test script for TransLink GTFS-RT V3 API key.

This script tests if your TransLink API key is valid and working.
TransLink is Vancouver's public transit system.

Note: The old RTTI API was retired on December 3, 2024.
This script now tests the new GTFS-RT V3 API.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.api_clients import TransLinkClient


async def test_translink_api():
    """Test TransLink GTFS-RT V3 API."""
    print("🚌 Testing TransLink GTFS-RT V3 API Key...")
    print("-" * 50)

    # Initialize client
    client = TransLinkClient()

    # Check if API key is set
    if not client.api_key or client.api_key == "your_translink_api_key_here":
        print("❌ ERROR: TransLink API key not found!")
        print("\nPlease set TRANSLINK_API_KEY in your .env file:")
        print("  1. Copy env.example to .env if you haven't already")
        print("  2. Add your API key: TRANSLINK_API_KEY=your_key_here")
        print("  3. Get your API key from: https://developer.translink.ca/")
        return False

    print(f"✓ API Key found: {client.api_key[:8]}...{client.api_key[-4:]}")
    print(f"✓ Base URL: {client.base_url}")
    print()

    # Test GTFS-RT endpoints
    endpoints = [
        ("Trip Updates", "gtfsrealtime"),
        ("Position Updates", "gtfsposition"),
        ("Service Alerts", "gtfsalerts"),
    ]

    success_count = 0
    total_tests = len(endpoints)

    for endpoint_name, endpoint_path in endpoints:
        print(f"⏳ Testing {endpoint_name} endpoint...")

        try:
            url = f"{client.base_url}/{endpoint_path}"
            params = {"apikey": client.api_key}

            print(f"   URL: {url}")

            response = await client.client.get(url, params=params, timeout=30.0)

            # Check response status
            if response.status_code == 401:
                print(f"❌ ERROR: 401 Unauthorized for {endpoint_name}")
                print()
                print("💡 This means your API key is invalid or not activated.")
                print("   Check your API key at: https://developer.translink.ca/")
                await client.client.aclose()
                return False

            if response.status_code == 403:
                print(f"❌ ERROR: 403 Forbidden for {endpoint_name}")
                print()
                print("💡 This usually means:")
                print("   - Your API key doesn't have permission for this endpoint")
                print("   - Your account may be restricted")
                await client.client.aclose()
                return False

            if response.status_code == 429:
                print(f"❌ ERROR: 429 Too Many Requests for {endpoint_name}")
                print()
                print("💡 You've exceeded your API call limit.")
                print("   Wait a minute and try again.")
                await client.client.aclose()
                return False

            if response.status_code != 200:
                print(f"❌ ERROR: HTTP {response.status_code} for {endpoint_name}")
                try:
                    error_data = response.json()
                    print(f"   Response: {error_data}")
                except:
                    print(f"   Response: {response.text[:200]}")
                await client.client.aclose()
                return False

            # Check content type (should be Protocol Buffer)
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)

            print(f"✅ {endpoint_name} endpoint is working!")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {content_type}")
            print(f"   Content Length: {content_length} bytes")

            if content_type == 'application/x-protobuf' or content_type.startswith('application/x-google-protobuf'):
                print("   ✓ Protocol Buffer format detected (correct)")
            elif content_length > 0:
                print("   ⚠️  Note: GTFS-RT feeds are in Protocol Buffer format")
                print("      You'll need a GTFS-RT parser to decode the data")

            print()
            success_count += 1

        except Exception as e:
            print(f"❌ ERROR: Failed to fetch {endpoint_name}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            print()

            error_str = str(e).lower()
            if "nodename" in error_str or "servname" in error_str or "dns" in error_str:
                print("💡 DNS Resolution Error:")
                print("   - Cannot resolve the API domain")
                print("   - Check your internet connection")
                print(f"   - Verify the URL: {client.base_url}")
            elif "timeout" in error_str:
                print("💡 Connection Timeout:")
                print("   - The API server is not responding")
                print("   - Check your internet connection")

            await client.client.aclose()
            return False

    await client.client.aclose()

    if success_count == total_tests:
        print("=" * 50)
        print("✅ SUCCESS! All GTFS-RT endpoints are working!")
        print()
        print("Your API key is valid and can access:")
        print("  ✓ Trip Updates feed")
        print("  ✓ Position Updates feed")
        print("  ✓ Service Alerts feed")
        print()
        print("Note: These feeds return data in Protocol Buffer format.")
        print("You'll need a GTFS-RT parser library to decode the data.")
        print("See: https://github.com/google/transit")
        return True
    else:
        print(f"⚠️  Only {success_count}/{total_tests} endpoints succeeded")
        return False


def main():
    """Main function."""
    print("=" * 50)
    print("TransLink GTFS-RT V3 API Key Test")
    print("=" * 50)
    print()
    print("Note: The old RTTI API was retired on December 3, 2024.")
    print("This script tests the new GTFS-RT V3 API endpoints.")
    print()

    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from: {env_path}")
    else:
        print(f"⚠️  No .env file found at: {env_path}")
        print("   Using environment variables from system")
    print()

    # Run async test
    success = asyncio.run(test_translink_api())

    print("=" * 50)
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
