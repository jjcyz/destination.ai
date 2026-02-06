import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import type {
  RouteRequest,
  RouteResponse,
  Point,
  Route,
  UserProfile,
  GamificationRewards,
  Achievement,
  Badge,
  DailyChallenge,
  LeaderboardEntry,
  ApiConfig,
  HealthCheckResponse,
} from '../types'
import { API_CONFIG } from '../config'

// Retry configuration
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second
const RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Retry helper function with exponential backoff
const retryRequest = async (
  error: AxiosError,
  retryCount = 0
): Promise<any> => {
  const config = error.config as AxiosRequestConfig & { _retryCount?: number }

  if (!config || retryCount >= MAX_RETRIES) {
    return Promise.reject(error)
  }

  const statusCode = error.response?.status
  if (statusCode && !RETRY_STATUS_CODES.includes(statusCode)) {
    return Promise.reject(error)
  }

  // Exponential backoff: 1s, 2s, 4s
  const delay = RETRY_DELAY * Math.pow(2, retryCount)

  if (import.meta.env.DEV) {
    console.log(`Retrying request (attempt ${retryCount + 1}/${MAX_RETRIES}) after ${delay}ms...`)
  }

  await new Promise(resolve => setTimeout(resolve, delay))

  config._retryCount = retryCount + 1
  return api.request(config)
}

// Request interceptor for logging (development only)
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
    console.error('API Request Error:', error)
    }
    return Promise.reject(error)
  }
)

// Response interceptor for error handling with retry
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
    console.log(`API Response: ${response.status} ${response.config.url}`)
    }
    return response
  },
  async (error: AxiosError) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
    console.error('API Response Error:', error.message)
    }

    const config = error.config as AxiosRequestConfig & { _retryCount?: number }
    const retryCount = config?._retryCount || 0

    // Attempt retry for retryable errors
    if (error.response?.status && RETRY_STATUS_CODES.includes(error.response.status)) {
      return retryRequest(error, retryCount)
    }

    return Promise.reject(error)
  }
)

/**
 * Extract error message from API error
 */
function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>
    return axiosError.response?.data?.detail || error.message || 'An unknown error occurred'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}

export const routeAPI = {
  /**
   * Calculate routes between origin and destination
   * Uses longer timeout for route calculation which can take time
   */
  async calculateRoute(request: RouteRequest): Promise<RouteResponse> {
    try {
      // Route calculation should complete quickly (within 5 seconds)
      // Allow 10 seconds total to account for network latency
      const response = await api.post<RouteResponse>('/route', request, {
        timeout: 10000, // 10 seconds - route calculation should take ~5 seconds
      })
      return response.data
    } catch (error) {
      const errorMessage = getErrorMessage(error)

      // Provide more helpful error messages
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          throw new Error(
            'Route calculation timed out. The request took longer than expected. ' +
            'This may indicate slow API responses or network issues. Please try again.'
          )
        }
        if (error.response?.status === 503) {
          throw new Error('Backend service is unavailable. Please check if the server is running.')
        }
      }

      throw new Error(errorMessage)
    }
  },

  /**
   * Geocode an address to coordinates
   */
  async geocodeAddress(address: string): Promise<Point> {
    try {
      const response = await api.get<Point>('/route/geocode', {
        params: { address },
      })
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Calculate gamification rewards for a completed route
   */
  async calculateRewards(route: Route, userProfile: UserProfile): Promise<GamificationRewards> {
    try {
      const response = await api.post<GamificationRewards>('/gamification/rewards', {
        route,
        user_profile: userProfile,
      })
      return response.data
    } catch (error) {
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
      console.warn('Failed to calculate rewards:', error)
      }
      // Return mock rewards for demo
      return {
        sustainability_points: route.total_sustainability_points || 0,
        co2_saved: 0.5,
        achievements_unlocked: [],
        badges_earned: [],
        level_up: false,
        streak_bonus: 0,
      }
    }
  },
}

export const gamificationAPI = {
  /**
   * Get all available achievements
   */
  async getAchievements(): Promise<{ achievements: Achievement[] }> {
    try {
      const response = await api.get<{ achievements: Achievement[] }>('/gamification/achievements')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Get all available badges
   */
  async getBadges(): Promise<{ badges: Badge[] }> {
    try {
      const response = await api.get<{ badges: Badge[] }>('/gamification/badges')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Get daily challenges
   */
  async getDailyChallenges(): Promise<{ challenges: DailyChallenge[] }> {
    try {
      const response = await api.get<{ challenges: DailyChallenge[] }>('/gamification/challenges')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Get leaderboard data
   */
  async getLeaderboard(limit: number = 10): Promise<{ leaderboard: LeaderboardEntry[] }> {
    try {
      const response = await api.get<{ leaderboard: LeaderboardEntry[] }>('/gamification/leaderboard', {
        params: { limit },
      })
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Get sustainability tips
   */
  async getSustainabilityTips(): Promise<{ tips: string[] }> {
    try {
      const response = await api.get<{ tips: string[] }>('/gamification/tips')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}

export const configAPI = {
  /**
   * Get API configuration and instructions
   */
  async getConfig(): Promise<ApiConfig> {
    try {
      const response = await api.get<ApiConfig>('/config')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await api.get<HealthCheckResponse>('/health')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}

export default api
