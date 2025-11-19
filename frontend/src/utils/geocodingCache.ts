/**
 * Geocoding cache utility
 * Caches geocoded addresses to avoid redundant API calls
 */

import type { Point } from '../types'

interface CacheEntry {
  point: Point
  timestamp: number
}

// Cache with 5 minute TTL
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes
const geocodingCache = new Map<string, CacheEntry>()

/**
 * Get cached geocoding result if available and not expired
 */
export const getCachedGeocode = (address: string): Point | null => {
  const normalizedAddress = address.toLowerCase().trim()
  const entry = geocodingCache.get(normalizedAddress)

  if (!entry) {
    return null
  }

  const age = Date.now() - entry.timestamp
  if (age > CACHE_TTL) {
    geocodingCache.delete(normalizedAddress)
    return null
  }

  return entry.point
}

/**
 * Cache a geocoding result
 */
export const cacheGeocode = (address: string, point: Point): void => {
  const normalizedAddress = address.toLowerCase().trim()
  geocodingCache.set(normalizedAddress, {
    point,
    timestamp: Date.now(),
  })
}

/**
 * Clear expired cache entries
 */
export const clearExpiredCache = (): void => {
  const now = Date.now()
  for (const [key, entry] of geocodingCache.entries()) {
    if (now - entry.timestamp > CACHE_TTL) {
      geocodingCache.delete(key)
    }
  }
}

/**
 * Clear all cache entries
 */
export const clearCache = (): void => {
  geocodingCache.clear()
}

