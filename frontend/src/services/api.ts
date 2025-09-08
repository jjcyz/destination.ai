import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const routeAPI = {
  // Calculate routes
  async calculateRoute(request: any) {
    try {
      const response = await api.post('/route', request)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to calculate routes')
    }
  },

  // Geocode address
  async geocodeAddress(address: string) {
    try {
      const response = await api.get('/route/geocode', {
        params: { address }
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to geocode address')
    }
  },

  // Calculate gamification rewards
  async calculateRewards(route: any, userProfile: any) {
    try {
      const response = await api.post('/gamification/rewards', {
        route,
        user_profile: userProfile
      })
      return response.data
    } catch (error: any) {
      console.warn('Failed to calculate rewards:', error)
      // Return mock rewards for demo
      return {
        sustainability_points: route.total_sustainability_points || 0,
        co2_saved: 0.5,
        achievements_unlocked: [],
        badges_earned: [],
        level_up: false,
        streak_bonus: 0
      }
    }
  }
}

export const gamificationAPI = {
  // Get achievements
  async getAchievements() {
    try {
      const response = await api.get('/gamification/achievements')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch achievements')
    }
  },

  // Get badges
  async getBadges() {
    try {
      const response = await api.get('/gamification/badges')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch badges')
    }
  },

  // Get daily challenges
  async getDailyChallenges() {
    try {
      const response = await api.get('/gamification/challenges')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch challenges')
    }
  },

  // Get leaderboard
  async getLeaderboard(limit: number = 10) {
    try {
      const response = await api.get('/gamification/leaderboard', {
        params: { limit }
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch leaderboard')
    }
  },

  // Get sustainability tips
  async getSustainabilityTips() {
    try {
      const response = await api.get('/gamification/tips')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch tips')
    }
  }
}

export const configAPI = {
  // Get API configuration
  async getConfig() {
    try {
      const response = await api.get('/config')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch config')
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Health check failed')
    }
  }
}

export default api
