import { useState, useEffect, useCallback } from 'react'

interface RateLimitState {
  isLimited: boolean
  remainingTime: number
  requestCount: number
}

interface RateLimiterOptions {
  maxRequests: number
  timeWindowMs: number
  storageKey?: string
}

/**
 * Client-side rate limiting hook to prevent abuse
 */
export const useRateLimit = (options: RateLimiterOptions) => {
  const {
    maxRequests,
    timeWindowMs,
    storageKey = 'rate_limit_data'
  } = options

  const [state, setState] = useState<RateLimitState>({
    isLimited: false,
    remainingTime: 0,
    requestCount: 0
  })

  // Check rate limit status
  const checkRateLimit = useCallback((): boolean => {
    try {
      const now = Date.now()
      const stored = localStorage.getItem(storageKey)

      if (!stored) {
        return false // No previous requests
      }

      const data = JSON.parse(stored)
      const { requests, windowStart } = data

      // Check if we're still in the same time window
      if (now - windowStart < timeWindowMs) {
        if (requests.length >= maxRequests) {
          const oldestRequest = requests[0]
          const timeUntilReset = timeWindowMs - (now - oldestRequest)

          setState({
            isLimited: true,
            remainingTime: Math.ceil(timeUntilReset / 1000),
            requestCount: requests.length
          })

          return true
        }
      }

      setState({
        isLimited: false,
        remainingTime: 0,
        requestCount: requests.length
      })

      return false
    } catch (error) {
      console.warn('Rate limit check failed:', error)
      return false
    }
  }, [maxRequests, timeWindowMs, storageKey])

  // Record a new request
  const recordRequest = useCallback((): boolean => {
    try {
      const now = Date.now()
      const stored = localStorage.getItem(storageKey)

      let data = stored
        ? JSON.parse(stored)
        : { requests: [], windowStart: now }

      // Remove requests outside the time window
      data.requests = data.requests.filter((timestamp: number) => {
        return now - timestamp < timeWindowMs
      })

      // Reset window if needed
      if (data.requests.length === 0) {
        data.windowStart = now
      }

      // Check if we can add another request
      if (data.requests.length >= maxRequests) {
        checkRateLimit()
        return false
      }

      // Add new request
      data.requests.push(now)
      localStorage.setItem(storageKey, JSON.stringify(data))

      setState({
        isLimited: false,
        remainingTime: 0,
        requestCount: data.requests.length
      })

      return true
    } catch (error) {
      console.warn('Failed to record request:', error)
      return true // Allow request on error
    }
  }, [maxRequests, timeWindowMs, storageKey, checkRateLimit])

  // Update remaining time countdown
  useEffect(() => {
    if (!state.isLimited) return

    const interval = setInterval(() => {
      setState(prev => {
        if (prev.remainingTime <= 1) {
          return {
            isLimited: false,
            remainingTime: 0,
            requestCount: 0
          }
        }
        return {
          ...prev,
          remainingTime: prev.remainingTime - 1
        }
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [state.isLimited])

  return {
    ...state,
    checkRateLimit,
    recordRequest
  }
}
