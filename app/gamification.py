"""
Gamification system for encouraging sustainable transportation choices.
Tracks user progress, awards points, and provides achievements.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

from .models import (
    Route, RouteStep, TransportMode, UserProfile, GamificationStats,
    RoutePreference, Point
)

logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    """Represents a gamification achievement."""
    id: str
    name: str
    description: str
    icon: str
    points_reward: int
    condition: str  # JSON string describing the condition
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None


@dataclass
class Badge:
    """Represents a gamification badge."""
    id: str
    name: str
    description: str
    icon: str
    rarity: str  # common, rare, epic, legendary
    condition: str
    earned: bool = False
    earned_at: Optional[datetime] = None


class GamificationEngine:
    """Engine for managing gamification features."""

    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.badges = self._initialize_badges()

        # Sustainability point multipliers
        self.sustainability_multipliers = {
            TransportMode.WALKING: 1.5,
            TransportMode.BIKING: 1.2,
            TransportMode.SCOOTER: 1.0,
            TransportMode.BUS: 1.1,
            TransportMode.SKYTRAIN: 1.1,
            TransportMode.CAR: 0.1
        }

        # CO2 savings per km (kg CO2/km)
        self.co2_savings = {
            TransportMode.WALKING: 0.0,  # No emissions
            TransportMode.BIKING: 0.0,   # No emissions
            TransportMode.SCOOTER: 0.02, # Electric, minimal emissions
            TransportMode.BUS: 0.05,     # Shared emissions
            TransportMode.SKYTRAIN: 0.03, # Electric, shared
            TransportMode.CAR: 0.12      # High emissions
        }

    def calculate_route_rewards(self, route: Route, user_profile: UserProfile) -> Dict[str, any]:
        """
        Calculate rewards for completing a route.

        Args:
            route: The completed route
            user_profile: User's profile and preferences

        Returns:
            Dictionary with rewards and statistics
        """
        rewards = {
            "sustainability_points": 0,
            "co2_saved": 0.0,
            "achievements_unlocked": [],
            "badges_earned": [],
            "level_up": False,
            "streak_bonus": 0
        }

        # Calculate sustainability points
        base_points = route.total_sustainability_points
        multiplier = self._get_sustainability_multiplier(route, user_profile)
        rewards["sustainability_points"] = int(base_points * multiplier)

        # Calculate CO2 savings
        rewards["co2_saved"] = self._calculate_co2_savings(route)

        # Check for achievements
        rewards["achievements_unlocked"] = self._check_achievements(route, user_profile)

        # Check for badges
        rewards["badges_earned"] = self._check_badges(route, user_profile)

        # Check for level up
        rewards["level_up"] = self._check_level_up(user_profile, rewards["sustainability_points"])

        # Calculate streak bonus
        rewards["streak_bonus"] = self._calculate_streak_bonus(user_profile)

        return rewards

    def _get_sustainability_multiplier(self, route: Route, user_profile: UserProfile) -> float:
        """Calculate sustainability multiplier based on route and user preferences."""
        base_multiplier = 1.0

        # Bonus for sustainable preferences
        if user_profile.sustainability_goals:
            base_multiplier *= 1.2

        # Bonus for using multiple sustainable modes
        sustainable_modes = [TransportMode.WALKING, TransportMode.BIKING, TransportMode.BUS, TransportMode.SKYTRAIN]
        used_sustainable_modes = set(step.mode for step in route.steps if step.mode in sustainable_modes)
        if len(used_sustainable_modes) > 1:
            base_multiplier *= 1.1

        # Bonus for avoiding cars
        if TransportMode.CAR not in [step.mode for step in route.steps]:
            base_multiplier *= 1.3

        return base_multiplier

    def _calculate_co2_savings(self, route: Route) -> float:
        """Calculate CO2 savings compared to driving."""
        total_savings = 0.0

        for step in route.steps:
            # Calculate what CO2 would have been emitted by car
            car_co2 = step.distance / 1000 * self.co2_savings[TransportMode.CAR]

            # Calculate actual CO2 emissions for the mode used
            actual_co2 = step.distance / 1000 * self.co2_savings[step.mode]

            # Savings is the difference
            savings = car_co2 - actual_co2
            total_savings += max(0, savings)  # Only count positive savings

        return round(total_savings, 3)

    def _check_achievements(self, route: Route, user_profile: UserProfile) -> List[Achievement]:
        """Check if any achievements should be unlocked."""
        unlocked = []

        for achievement in self.achievements:
            if not achievement.unlocked and self._evaluate_achievement_condition(achievement, route, user_profile):
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
                unlocked.append(achievement)

        return unlocked

    def _check_badges(self, route: Route, user_profile: UserProfile) -> List[Badge]:
        """Check if any badges should be earned."""
        earned = []

        for badge in self.badges:
            if not badge.earned and self._evaluate_badge_condition(badge, route, user_profile):
                badge.earned = True
                badge.earned_at = datetime.now()
                earned.append(badge)

        return earned

    def _evaluate_achievement_condition(self, achievement: Achievement, route: Route, user_profile: UserProfile) -> bool:
        """Evaluate if an achievement condition is met."""
        try:
            condition = json.loads(achievement.condition)
            condition_type = condition.get("type")

            if condition_type == "distance_walked":
                return route.total_distance >= condition.get("threshold", 0)
            elif condition_type == "sustainability_points":
                return route.total_sustainability_points >= condition.get("threshold", 0)
            elif condition_type == "modes_used":
                required_modes = set(condition.get("modes", []))
                used_modes = set(step.mode for step in route.steps)
                return required_modes.issubset(used_modes)
            elif condition_type == "no_car_route":
                return TransportMode.CAR not in [step.mode for step in route.steps]
            elif condition_type == "long_distance_bike":
                bike_distance = sum(step.distance for step in route.steps if step.mode == TransportMode.BIKING)
                return bike_distance >= condition.get("threshold", 0)

            return False

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error evaluating achievement condition: {e}")
            return False

    def _evaluate_badge_condition(self, badge: Badge, route: Route, user_profile: UserProfile) -> bool:
        """Evaluate if a badge condition is met."""
        try:
            condition = json.loads(badge.condition)
            condition_type = condition.get("type")

            if condition_type == "eco_warrior":
                return (route.total_sustainability_points >= 100 and
                        TransportMode.CAR not in [step.mode for step in route.steps])
            elif condition_type == "speed_demon":
                return route.total_time <= condition.get("max_time", 1800)  # 30 minutes
            elif condition_type == "explorer":
                unique_modes = len(set(step.mode for step in route.steps))
                return unique_modes >= condition.get("min_modes", 3)

            return False

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error evaluating badge condition: {e}")
            return False

    def _check_level_up(self, user_profile: UserProfile, points_earned: int) -> bool:
        """Check if user should level up."""
        # Simple leveling system: 100 points per level
        current_level = user_profile.level
        total_points = user_profile.total_sustainability_points + points_earned
        new_level = (total_points // 100) + 1

        return new_level > current_level

    def _calculate_streak_bonus(self, user_profile: UserProfile) -> int:
        """Calculate streak bonus points."""
        if user_profile.streak_days >= 7:
            return 50  # Weekly streak bonus
        elif user_profile.streak_days >= 3:
            return 20  # 3-day streak bonus
        else:
            return 0

    def update_user_stats(self, user_profile: UserProfile, rewards: Dict[str, any]) -> UserProfile:
        """Update user statistics with new rewards."""
        # Update sustainability points
        user_profile.total_sustainability_points += rewards["sustainability_points"]

        # Update CO2 savings
        user_profile.total_distance_saved += rewards["co2_saved"]

        # Update level
        user_profile.level = (user_profile.total_sustainability_points // 100) + 1

        # Update achievements
        for achievement in rewards["achievements_unlocked"]:
            if achievement.id not in user_profile.achievements:
                user_profile.achievements.append(achievement.id)

        # Update badges
        for badge in rewards["badges_earned"]:
            if badge.id not in user_profile.badges:
                user_profile.badges.append(badge.id)

        return user_profile

    def get_leaderboard_data(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get leaderboard data (would be implemented with database)."""
        # This would typically query a database
        # For now, return mock data
        return [
            {
                "user_id": "user1",
                "username": "EcoExplorer",
                "sustainability_points": 1250,
                "level": 13,
                "co2_saved": 45.2,
                "badges": ["eco_warrior", "explorer"]
            },
            {
                "user_id": "user2",
                "username": "BikeMaster",
                "sustainability_points": 980,
                "level": 10,
                "co2_saved": 32.1,
                "badges": ["speed_demon"]
            }
        ]

    def get_daily_challenges(self) -> List[Dict[str, any]]:
        """Get daily challenges for users."""
        return [
            {
                "id": "daily_walk",
                "title": "Daily Walker",
                "description": "Walk at least 2km today",
                "reward_points": 30,
                "progress": 0,
                "target": 2000,
                "type": "distance",
                "mode": "walking"
            },
            {
                "id": "eco_commute",
                "title": "Eco Commute",
                "description": "Complete a route without using a car",
                "reward_points": 50,
                "progress": 0,
                "target": 1,
                "type": "routes",
                "mode": "any"
            },
            {
                "id": "multi_modal",
                "title": "Multi-Modal Master",
                "description": "Use at least 3 different transport modes in one route",
                "reward_points": 40,
                "progress": 0,
                "target": 1,
                "type": "routes",
                "mode": "mixed"
            }
        ]

    def get_sustainability_tips(self) -> List[str]:
        """Get sustainability tips for users."""
        return [
            "Walking is the most sustainable mode of transportation with zero emissions!",
            "Biking burns calories while saving the planet - it's a win-win!",
            "Public transit reduces traffic congestion and your carbon footprint.",
            "Consider combining walking with public transit for longer distances.",
            "Scooters are great for short trips and produce minimal emissions.",
            "Avoid driving during peak hours to reduce traffic congestion.",
            "Plan your routes to minimize backtracking and save time.",
            "Use bike lanes when available for safer and more efficient cycling."
        ]

    def _initialize_achievements(self) -> List[Achievement]:
        """Initialize available achievements."""
        return [
            Achievement(
                id="first_steps",
                name="First Steps",
                description="Complete your first sustainable route",
                icon="👣",
                points_reward=10,
                condition='{"type": "sustainability_points", "threshold": 1}'
            ),
            Achievement(
                id="eco_commuter",
                name="Eco Commuter",
                description="Complete 10 routes without using a car",
                icon="🌱",
                points_reward=100,
                condition='{"type": "no_car_route", "threshold": 10}'
            ),
            Achievement(
                id="bike_champion",
                name="Bike Champion",
                description="Bike a total of 50km",
                icon="🚴",
                points_reward=200,
                condition='{"type": "distance_biked", "threshold": 50000}'
            ),
            Achievement(
                id="multi_modal_master",
                name="Multi-Modal Master",
                description="Use 5 different transport modes",
                icon="🚌",
                points_reward=150,
                condition='{"type": "modes_used", "modes": ["walking", "biking", "bus", "skytrain", "scooter"]}'
            ),
            Achievement(
                id="sustainability_hero",
                name="Sustainability Hero",
                description="Earn 1000 sustainability points",
                icon="🏆",
                points_reward=500,
                condition='{"type": "sustainability_points", "threshold": 1000}'
            )
        ]

    def _initialize_badges(self) -> List[Badge]:
        """Initialize available badges."""
        return [
            Badge(
                id="eco_warrior",
                name="Eco Warrior",
                description="Complete a high-sustainability route without a car",
                icon="🛡️",
                rarity="rare",
                condition='{"type": "eco_warrior"}'
            ),
            Badge(
                id="speed_demon",
                name="Speed Demon",
                description="Complete a route in under 30 minutes",
                icon="⚡",
                rarity="common",
                condition='{"type": "speed_demon", "max_time": 1800}'
            ),
            Badge(
                id="explorer",
                name="Explorer",
                description="Use 3 or more transport modes in a single route",
                icon="🗺️",
                rarity="epic",
                condition='{"type": "explorer", "min_modes": 3}'
            ),
            Badge(
                id="carbon_crusher",
                name="Carbon Crusher",
                description="Save 10kg of CO2 emissions",
                icon="💨",
                rarity="legendary",
                condition='{"type": "co2_saved", "threshold": 10}'
            )
        ]

    def generate_route_recommendation_message(self, route: Route, rewards: Dict[str, any]) -> str:
        """Generate an encouraging message for route completion."""
        messages = []

        # Base message
        if route.total_sustainability_points > 50:
            messages.append("🌱 Excellent choice! You're making a real difference for the environment.")
        elif route.total_sustainability_points > 20:
            messages.append("👍 Great job choosing sustainable transportation!")
        else:
            messages.append("🚀 Nice route! Consider trying more sustainable options next time.")

        # CO2 savings message
        if rewards["co2_saved"] > 0:
            messages.append(f"💨 You saved {rewards['co2_saved']:.2f}kg of CO2 emissions!")

        # Achievement messages
        if rewards["achievements_unlocked"]:
            messages.append(f"🏆 You unlocked {len(rewards['achievements_unlocked'])} new achievement(s)!")

        # Badge messages
        if rewards["badges_earned"]:
            messages.append(f"🎖️ You earned {len(rewards['badges_earned'])} new badge(s)!")

        # Level up message
        if rewards["level_up"]:
            messages.append("🎉 Level up! You're becoming a sustainability champion!")

        return " ".join(messages)

    def get_user_progress_summary(self, user_profile: UserProfile) -> Dict[str, any]:
        """Get a summary of user's progress and statistics."""
        return {
            "level": user_profile.level,
            "sustainability_points": user_profile.total_sustainability_points,
            "points_to_next_level": 100 - (user_profile.total_sustainability_points % 100),
            "co2_saved": user_profile.total_distance_saved,
            "streak_days": user_profile.streak_days,
            "achievements_count": len(user_profile.achievements),
            "badges_count": len(user_profile.badges),
            "total_achievements": len(self.achievements),
            "total_badges": len(self.badges),
            "achievement_progress": len(user_profile.achievements) / len(self.achievements) * 100,
            "badge_progress": len(user_profile.badges) / len(self.badges) * 100
        }
