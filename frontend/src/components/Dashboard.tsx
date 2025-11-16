import React, { useState, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import { BarChart3, TrendingUp, Leaf, Award, Target, Zap } from 'lucide-react'
import { gamificationAPI } from '../services/api'

const Dashboard: React.FC = () => {
  const { state: userState } = useUser()
  const [challenges, setChallenges] = useState<any[]>([])
  const [tips, setTips] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Load dashboard data
    const loadDashboardData = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const [challengesData, tipsData] = await Promise.all([
          gamificationAPI.getDailyChallenges(),
          gamificationAPI.getSustainabilityTips()
        ])

        setChallenges(challengesData.challenges || [])
        setTips(tipsData.tips?.map((tip: any) => tip.description || tip.title || tip) || [])
      } catch (error) {
        // Use mock data for demo when backend is not available
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.log('Backend not available, using demo data:', error instanceof Error ? error.message : 'Unknown error')
        }
        setChallenges([
          {
            id: 'daily_walk',
            name: 'Daily Walker',
            description: 'Walk at least 2km today',
            reward_points: 30,
            progress: 0,
            target: 2000
          },
          {
            id: 'eco_commute',
            name: 'Eco Commute',
            description: 'Complete a route without using a car',
            reward_points: 50,
            progress: 0,
            target: 1
          },
          {
            id: 'public_transit',
            name: 'Public Transit Pro',
            description: 'Use public transportation for your commute',
            reward_points: 40,
            progress: 0,
            target: 1
          }
        ])
        setTips([
          'Walking is the most sustainable mode of transportation with zero emissions!',
          'Biking burns calories while saving the planet - it\'s a win-win!',
          'Public transit reduces traffic congestion and your carbon footprint.',
          'Carpooling with colleagues can cut your emissions in half!',
          'Planning your route in advance helps avoid traffic and saves fuel.'
        ])
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const progressToNextLevel = (userState.profile.total_sustainability_points % 100)
  const pointsNeeded = 100 - progressToNextLevel

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }


  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Your Sustainability Dashboard
        </h1>
        <p className="text-gray-600">
          Track your progress and discover new ways to be eco-friendly
        </p>
      </div>

      {/* User Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Level</p>
              <p className="text-2xl font-bold text-gray-900">{userState.profile.level}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Sustainability Points</p>
              <p className="text-2xl font-bold text-gray-900">{userState.profile.total_sustainability_points}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">CO2 Saved</p>
              <p className="text-2xl font-bold text-gray-900">{userState.profile.total_distance_saved.toFixed(1)} kg</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Achievements</p>
              <p className="text-2xl font-bold text-gray-900">{userState.profile.achievements.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Level Progress */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Level Progress</h3>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Progress to Level {userState.profile.level + 1}</span>
            <span className="text-gray-900">{progressToNextLevel}/100 points</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${(progressToNextLevel / 100) * 100}%` }}
            />
          </div>
          <p className="text-sm text-gray-500">
            {pointsNeeded} more points needed to reach the next level
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Challenges */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2" />
            Daily Challenges
          </h3>
          <div className="space-y-4">
            {challenges.map((challenge) => (
              <div key={challenge.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{challenge.name || challenge.title}</h4>
                  <span className="text-sm text-green-600 font-medium">
                    +{challenge.reward_points} pts
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{challenge.description}</p>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Progress: {challenge.progress}/{challenge.target}</span>
                  <span>{Math.round((challenge.progress / challenge.target) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min((challenge.progress / challenge.target) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sustainability Tips */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Sustainability Tips
          </h3>
          <div className="space-y-3">
            {tips.map((tip, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 text-sm">💡</span>
                </div>
                <p className="text-sm text-gray-700">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-sm">🚴</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Completed bike route</p>
              <p className="text-xs text-gray-500">Downtown to Stanley Park • +25 points</p>
            </div>
            <span className="text-xs text-gray-400">2 hours ago</span>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-sm">🏆</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Achievement unlocked</p>
              <p className="text-xs text-gray-500">First Steps • +10 points</p>
            </div>
            <span className="text-xs text-gray-400">1 day ago</span>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 text-sm">🎖️</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Badge earned</p>
              <p className="text-xs text-gray-500">Eco Warrior • Rare</p>
            </div>
            <span className="text-xs text-gray-400">3 days ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
