import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { Trophy, Award, Target, Star, Crown, Gem } from 'lucide-react'
import { gamificationAPI } from '../services/api'
import TopNavigation from './TopNavigation'

const Gamification: React.FC = () => {
  const { state: userState } = useUser()
  const [achievements, setAchievements] = useState<any[]>([])
  const [badges, setBadges] = useState<any[]>([])
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState<'achievements' | 'badges' | 'leaderboard'>('achievements')

  useEffect(() => {
    const loadGamificationData = async () => {
      try {
        const [achievementsData, badgesData, leaderboardData] = await Promise.all([
          gamificationAPI.getAchievements(),
          gamificationAPI.getBadges(),
          gamificationAPI.getLeaderboard()
        ])

        setAchievements(achievementsData.achievements || [])
        setBadges(badgesData.badges || [])
        setLeaderboard(leaderboardData.leaderboard || [])
      } catch (error) {
        // Use mock data for demo
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.error('Failed to load gamification data:', error)
        }
        setAchievements([
          {
            id: 'first_steps',
            name: 'First Steps',
            description: 'Complete your first sustainable route',
            icon: '👣',
            points_reward: 10
          },
          {
            id: 'eco_commuter',
            name: 'Eco Commuter',
            description: 'Complete 10 routes without using a car',
            icon: '🌱',
            points_reward: 100
          }
        ])
        setBadges([
          {
            id: 'eco_warrior',
            name: 'Eco Warrior',
            description: 'Complete a high-sustainability route without a car',
            icon: '🛡️',
            rarity: 'rare'
          },
          {
            id: 'speed_demon',
            name: 'Speed Demon',
            description: 'Complete a route in under 30 minutes',
            icon: '⚡',
            rarity: 'common'
          }
        ])
        setLeaderboard([
          {
            user_id: 'user1',
            username: 'EcoExplorer',
            sustainability_points: 1250,
            level: 13,
            co2_saved: 45.2
          },
          {
            user_id: 'user2',
            username: 'BikeMaster',
            sustainability_points: 980,
            level: 10,
            co2_saved: 32.1
          }
        ])
      }
    }

    loadGamificationData()
  }, [])

  const getRarityColor = (rarity: string) => {
    const colors: { [key: string]: string } = {
      common: 'bg-gray-100 text-gray-800',
      rare: 'bg-blue-100 text-blue-800',
      epic: 'bg-purple-100 text-purple-800',
      legendary: 'bg-yellow-100 text-yellow-800'
    }
    return colors[rarity] || colors.common
  }

  const getRarityIcon = (rarity: string) => {
    const icons: { [key: string]: any } = {
      common: Star,
      rare: Award,
      epic: Crown,
      legendary: Gem
    }
    return icons[rarity] || Star
  }

  return (
    <div className="min-h-screen">
      <TopNavigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 pt-6 space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          My Profile
        </h1>
        <p className="text-gray-600">
          Track your achievements, earn badges, and compete with others
        </p>
      </div>

      {/* User Progress Summary */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">{userState.profile.level}</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Level {userState.profile.level}</h3>
              <p className="text-gray-600">{userState.profile.total_sustainability_points} sustainability points</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">{userState.profile.achievements.length}</div>
            <div className="text-sm text-gray-500">Achievements</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('achievements')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
            activeTab === 'achievements'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Trophy className="w-4 h-4 inline mr-2" />
          Achievements
        </button>
        <button
          onClick={() => setActiveTab('badges')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
            activeTab === 'badges'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Award className="w-4 h-4 inline mr-2" />
          Badges
        </button>
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
            activeTab === 'leaderboard'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Target className="w-4 h-4 inline mr-2" />
          Leaderboard
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'achievements' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Achievements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {achievements.map((achievement) => {
              const isUnlocked = userState.profile.achievements.includes(achievement.id)

              return (
                <div
                  key={achievement.id}
                  className={`card ${
                    isUnlocked ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`text-2xl ${isUnlocked ? '' : 'grayscale opacity-50'}`}>
                      {achievement.icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className={`font-semibold ${isUnlocked ? 'text-green-900' : 'text-gray-700'}`}>
                          {achievement.name}
                        </h3>
                        {isUnlocked && (
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                            Unlocked
                          </span>
                        )}
                      </div>
                      <p className={`text-sm mt-1 ${isUnlocked ? 'text-green-700' : 'text-gray-600'}`}>
                        {achievement.description}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">
                          +{achievement.points_reward} points
                        </span>
                        {isUnlocked && (
                          <span className="text-xs text-green-600 font-medium">
                            ✓ Completed
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {activeTab === 'badges' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Badges</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {badges.map((badge) => {
              const isEarned = userState.profile.badges.includes(badge.id)
              const RarityIcon = getRarityIcon(badge.rarity)

              return (
                <div
                  key={badge.id}
                  className={`card ${
                    isEarned ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="text-center">
                    <div className={`text-3xl mb-3 ${isEarned ? '' : 'grayscale opacity-50'}`}>
                      {badge.icon}
                    </div>
                    <h3 className={`font-semibold mb-2 ${isEarned ? 'text-yellow-900' : 'text-gray-700'}`}>
                      {badge.name}
                    </h3>
                    <p className={`text-sm mb-3 ${isEarned ? 'text-yellow-700' : 'text-gray-600'}`}>
                      {badge.description}
                    </p>
                    <div className="flex items-center justify-center space-x-2">
                      <RarityIcon className="w-4 h-4" />
                      <span className={`text-xs px-2 py-1 rounded-full ${getRarityColor(badge.rarity)}`}>
                        {badge.rarity}
                      </span>
                    </div>
                    {isEarned && (
                      <div className="mt-3 text-xs text-yellow-600 font-medium">
                        ✓ Earned
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Leaderboard</h2>
          <div className="card">
            <div className="space-y-3">
              {leaderboard.map((user, index) => (
                <div
                  key={user.user_id}
                  className={`flex items-center space-x-4 p-3 rounded-lg ${
                    index === 0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex-shrink-0">
                    {index === 0 ? (
                      <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                        <Crown className="w-5 h-5 text-white" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">{index + 1}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">{user.username}</h3>
                      <span className="text-sm text-gray-500">Level {user.level}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{user.sustainability_points} points</span>
                      <span>{user.co2_saved} kg CO2 saved</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}

export default Gamification
