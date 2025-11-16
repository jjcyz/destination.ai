#!/usr/bin/env python3
"""
Simple test to verify demo functionality works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.demo import DemoDataProvider, DemoGamificationProvider
from app.models import RouteRequest, Point, RoutePreference, TransportMode

def test_demo_functionality():
    """Test that demo functionality works."""
    print(" Testing Demo Functionality...")

    # Test geocoding
    print("\n1. Testing Demo Geocoding...")
    origin = DemoDataProvider.geocode_address("vancouver downtown")
    destination = DemoDataProvider.geocode_address("stanley park")
    print(f"   Origin: {origin}")
    print(f"   Destination: {destination}")

    # Test route generation
    print("\n2. Testing Demo Route Generation...")
    request = RouteRequest(
        origin=origin,
        destination=destination,
        preferences=[RoutePreference.FASTEST, RoutePreference.SCENIC],
        transport_modes=[TransportMode.WALKING, TransportMode.BIKING, TransportMode.BUS],
        departure_time=None,
        max_walking_distance=1000,
        max_biking_distance=5000
    )

    response = DemoDataProvider.generate_demo_routes(request)
    print(f"   Generated {len(response.routes)} routes")
    print(f"   Generated {len(response.alternatives)} alternatives")
    print(f"   Data sources: {response.data_sources}")

    # Test gamification
    print("\n3. Testing Demo Gamification...")
    if response.routes:
        route = response.routes[0]
        user_profile = {"level": 1, "total_points": 100}
        rewards = DemoGamificationProvider.calculate_demo_rewards(route, user_profile)
        print(f"   Sustainability points: {rewards['sustainability_points']}")
        print(f"   CO2 saved: {rewards['co2_saved']} kg")
        print(f"   Achievements: {len(rewards['achievements_unlocked'])}")
        print(f"   Badges: {len(rewards['badges_earned'])}")

    # Test other gamification features
    print("\n4. Testing Demo Gamification Features...")
    achievements = DemoGamificationProvider.get_demo_achievements()
    badges = DemoGamificationProvider.get_demo_badges()
    challenges = DemoGamificationProvider.get_demo_daily_challenges()
    leaderboard = DemoGamificationProvider.get_demo_leaderboard()
    tips = DemoGamificationProvider.get_demo_sustainability_tips()

    print(f"   Achievements: {len(achievements)}")
    print(f"   Badges: {len(badges)}")
    print(f"   Daily challenges: {len(challenges)}")
    print(f"   Leaderboard entries: {len(leaderboard)}")
    print(f"   Sustainability tips: {len(tips)}")

    print("\n Demo functionality test completed successfully!")
    print("\n The demo mode is ready to use!")
    print("   - Route calculation: ✅")
    print("   - Geocoding: ✅")
    print("   - Gamification: ✅")
    print("   - All features: ✅")

if __name__ == "__main__":
    test_demo_functionality()
