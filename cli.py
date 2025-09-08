#!/usr/bin/env python3
"""
Command Line Interface for the Vancouver Route Recommendation System.
Provides interactive testing and demonstration capabilities.
"""

import asyncio
import argparse
import json
import sys
from typing import Optional, List
from datetime import datetime

# Add the app directory to the Python path
sys.path.append('.')

from app.models import (
    RouteRequest, Point, RoutePreference, TransportMode, UserProfile
)
from app.routing_engine import RoutingEngine
from app.graph_builder import VancouverGraphBuilder
from app.gamification import GamificationEngine
from app.config import settings, validate_api_keys


class RouteCLI:
    """Command Line Interface for route recommendations."""

    def __init__(self):
        self.graph_builder = None
        self.routing_engine = None
        self.gamification_engine = GamificationEngine()
        self.user_profile = UserProfile(
            user_id="cli_user",
            preferred_modes=[TransportMode.WALKING, TransportMode.BIKING, TransportMode.BUS],
            fitness_level="moderate",
            sustainability_goals=True
        )

    async def initialize(self):
        """Initialize the routing system."""
        print("🚀 Initializing Vancouver Route Recommendation System...")

        # Check API keys
        api_status = validate_api_keys()
        if not api_status["all_required"]:
            print("⚠️  Warning: Some API keys are missing. Using mock data.")
            print("   Check env.example for API key setup instructions.")

        # Initialize components
        self.graph_builder = VancouverGraphBuilder()
        self.routing_engine = RoutingEngine(self.graph_builder)

        print("✅ System initialized successfully!")

    async def cleanup(self):
        """Clean up resources."""
        if self.routing_engine:
            await self.routing_engine.close()
        if self.graph_builder:
            await self.graph_builder.close()

    async def find_route(self, origin: str, destination: str, preferences: List[str] = None):
        """Find routes between two locations."""
        if not preferences:
            preferences = ["fastest"]

        print(f"\n🗺️  Finding routes from {origin} to {destination}")
        print(f"   Preferences: {', '.join(preferences)}")

        try:
            # Geocode addresses (simplified - in real implementation would use API)
            origin_point = self._parse_coordinates_or_geocode(origin)
            destination_point = self._parse_coordinates_or_geocode(destination)

            if not origin_point or not destination_point:
                print("❌ Could not resolve origin or destination coordinates")
                return

            # Create route request
            route_preferences = [RoutePreference(pref) for pref in preferences if pref in [p.value for p in RoutePreference]]
            if not route_preferences:
                route_preferences = [RoutePreference.FASTEST]

            request = RouteRequest(
                origin=origin_point,
                destination=destination_point,
                preferences=route_preferences,
                transport_modes=[
                    TransportMode.WALKING,
                    TransportMode.BIKING,
                    TransportMode.CAR,
                    TransportMode.BUS
                ]
            )

            # Find routes
            print("🔍 Calculating routes...")
            response = await self.routing_engine.find_routes(request)

            # Display results
            self._display_routes(response)

            # Calculate gamification rewards
            if response.routes:
                self._display_gamification_rewards(response.routes[0])

        except Exception as e:
            print(f"❌ Error finding routes: {e}")

    def _parse_coordinates_or_geocode(self, location: str) -> Optional[Point]:
        """Parse coordinates or return mock coordinates for demo."""
        # Check if it's coordinates
        if ',' in location:
            try:
                lat, lng = map(float, location.split(','))
                return Point(lat=lat, lng=lng)
            except ValueError:
                pass

        # Mock geocoding for demo
        mock_locations = {
            "vancouver downtown": Point(lat=49.2827, lng=-123.1207),
            "vancouver airport": Point(lat=49.1967, lng=-123.1815),
            "stanley park": Point(lat=49.3043, lng=-123.1443),
            "ubc": Point(lat=49.2606, lng=-123.2460),
            "burnaby": Point(lat=49.2488, lng=-122.9805),
            "richmond": Point(lat=49.1666, lng=-123.1336)
        }

        location_lower = location.lower()
        for key, point in mock_locations.items():
            if key in location_lower:
                return point

        # Default to downtown Vancouver
        return Point(lat=49.2827, lng=-123.1207)

    def _display_routes(self, response):
        """Display route results."""
        print(f"\n📊 Found {len(response.routes)} route(s) in {response.processing_time:.2f}s")
        print(f"   Data sources: {', '.join(response.data_sources)}")

        for i, route in enumerate(response.routes, 1):
            print(f"\n🛣️  Route {i}: {route.preference.value.title()}")
            print(f"   Total distance: {route.total_distance/1000:.2f} km")
            print(f"   Total time: {route.total_time//60} min {route.total_time%60} sec")
            print(f"   Sustainability points: {route.total_sustainability_points}")
            print(f"   Safety score: {route.safety_score:.2f}")
            print(f"   Energy efficiency: {route.energy_efficiency:.2f}")

            print("   Steps:")
            for j, step in enumerate(route.steps, 1):
                print(f"     {j}. {step.instructions}")
                print(f"        {step.distance/1000:.2f} km, {step.estimated_time//60} min, {step.mode.value}")
                if step.slope:
                    print(f"        Slope: {step.slope:.1f}%, Effort: {step.effort_level}")

        if response.alternatives:
            print(f"\n🔄 {len(response.alternatives)} alternative route(s) available")

    def _display_gamification_rewards(self, route):
        """Display gamification rewards."""
        print(f"\n🎮 Gamification Rewards:")

        rewards = self.gamification_engine.calculate_route_rewards(route, self.user_profile)

        print(f"   Sustainability points: {rewards['sustainability_points']}")
        print(f"   CO2 saved: {rewards['co2_saved']:.2f} kg")

        if rewards['achievements_unlocked']:
            print(f"   🏆 Achievements unlocked: {len(rewards['achievements_unlocked'])}")
            for achievement in rewards['achievements_unlocked']:
                print(f"      - {achievement.icon} {achievement.name}")

        if rewards['badges_earned']:
            print(f"   🎖️ Badges earned: {len(rewards['badges_earned'])}")
            for badge in rewards['badges_earned']:
                print(f"      - {badge.icon} {badge.name} ({badge.rarity})")

        if rewards['level_up']:
            print(f"   🎉 Level up! New level: {self.user_profile.level + 1}")

        if rewards['streak_bonus'] > 0:
            print(f"   🔥 Streak bonus: +{rewards['streak_bonus']} points")

        # Update user profile
        self.user_profile = self.gamification_engine.update_user_stats(self.user_profile, rewards)

    async def interactive_mode(self):
        """Run interactive mode."""
        print("\n🎯 Interactive Route Planning Mode")
        print("   Type 'help' for commands, 'quit' to exit")

        while True:
            try:
                command = input("\n> ").strip().lower()

                if command == 'quit' or command == 'exit':
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'status':
                    self._show_status()
                elif command == 'achievements':
                    self._show_achievements()
                elif command == 'challenges':
                    self._show_challenges()
                elif command == 'tips':
                    self._show_tips()
                elif command.startswith('route '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 3:
                        origin = parts[1]
                        destination = parts[2]
                        await self.find_route(origin, destination)
                    else:
                        print("Usage: route <origin> <destination> [preferences]")
                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _show_help(self):
        """Show help information."""
        print("\n📖 Available Commands:")
        print("   route <origin> <destination> [preferences] - Find routes")
        print("   status - Show system status")
        print("   achievements - Show available achievements")
        print("   challenges - Show daily challenges")
        print("   tips - Show sustainability tips")
        print("   help - Show this help")
        print("   quit - Exit the program")
        print("\n📍 Example locations:")
        print("   vancouver downtown, vancouver airport, stanley park, ubc, burnaby, richmond")
        print("   Or use coordinates: 49.2827,-123.1207")
        print("\n🎯 Example preferences:")
        print("   fastest, safest, energy_efficient, scenic, healthy, cheapest")

    def _show_status(self):
        """Show system status."""
        print(f"\n📊 System Status:")
        print(f"   User level: {self.user_profile.level}")
        print(f"   Sustainability points: {self.user_profile.total_sustainability_points}")
        print(f"   CO2 saved: {self.user_profile.total_distance_saved:.2f} kg")
        print(f"   Achievements: {len(self.user_profile.achievements)}/{len(self.gamification_engine.achievements)}")
        print(f"   Badges: {len(self.user_profile.badges)}/{len(self.gamification_engine.badges)}")

        api_status = validate_api_keys()
        print(f"   API keys: {'✅ All configured' if api_status['all_required'] else '⚠️ Some missing'}")

    def _show_achievements(self):
        """Show available achievements."""
        print(f"\n🏆 Available Achievements:")
        for achievement in self.gamification_engine.achievements:
            status = "✅" if achievement.id in self.user_profile.achievements else "⏳"
            print(f"   {status} {achievement.icon} {achievement.name}")
            print(f"      {achievement.description} (+{achievement.points_reward} points)")

    def _show_challenges(self):
        """Show daily challenges."""
        print(f"\n🎯 Daily Challenges:")
        challenges = self.gamification_engine.get_daily_challenges()
        for challenge in challenges:
            print(f"   {challenge['title']}: {challenge['description']}")
            print(f"      Reward: +{challenge['reward_points']} points")

    def _show_tips(self):
        """Show sustainability tips."""
        print(f"\n💡 Sustainability Tips:")
        tips = self.gamification_engine.get_sustainability_tips()
        for i, tip in enumerate(tips, 1):
            print(f"   {i}. {tip}")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Vancouver Route Recommendation System CLI")
    parser.add_argument("--origin", "-o", help="Origin location")
    parser.add_argument("--destination", "-d", help="Destination location")
    parser.add_argument("--preferences", "-p", nargs="+", help="Route preferences")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    cli = RouteCLI()

    try:
        await cli.initialize()

        if args.interactive or (not args.origin and not args.destination):
            await cli.interactive_mode()
        elif args.origin and args.destination:
            await cli.find_route(args.origin, args.destination, args.preferences)
        else:
            print("❌ Please provide both origin and destination, or use --interactive mode")
            parser.print_help()

    finally:
        await cli.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
