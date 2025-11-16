/**
 * Application constants and configuration values.
 * Centralized location for all hardcoded values and configuration.
 */

/**
 * API configuration
 */
const getApiBaseUrl = (): string => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const env = (import.meta as any).env
  return env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
}

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000, // 30 seconds
} as const

/**
 * Mock coordinates for demo mode (Vancouver locations)
 */
export const MOCK_COORDINATES: Record<string, { lat: number; lng: number }> = {
  'vancouver downtown': { lat: 49.2827, lng: -123.1207 },
  'vancouver airport': { lat: 49.1967, lng: -123.1815 },
  'stanley park': { lat: 49.3043, lng: -123.1443 },
  'ubc': { lat: 49.2606, lng: -123.2460 },
  'burnaby': { lat: 49.2488, lng: -122.9805 },
  'richmond': { lat: 49.1666, lng: -123.1336 },
} as const

/**
 * Default route preferences
 */
export const DEFAULT_PREFERENCES = ['fastest'] as const

/**
 * Default transport modes
 */
export const DEFAULT_TRANSPORT_MODES = ['walking', 'biking', 'car', 'bus'] as const

/**
 * Max walking distance configuration
 */
export const WALKING_DISTANCE_CONFIG = {
  MIN: 500,
  MAX: 5000,
  STEP: 500,
  DEFAULT: 2000,
} as const

/**
 * Route preference options with UI metadata
 */
export const ROUTE_PREFERENCE_OPTIONS = [
  { value: 'fastest', label: 'Fastest', color: 'from-red-500 to-pink-500' },
  { value: 'safest', label: 'Safest', color: 'from-green-500 to-emerald-500' },
  { value: 'energy_efficient', label: 'Eco-Friendly', color: 'from-blue-500 to-cyan-500' },
  { value: 'scenic', label: 'Scenic', color: 'from-yellow-500 to-orange-500' },
  { value: 'healthy', label: 'Healthy', color: 'from-purple-500 to-violet-500' },
  { value: 'cheapest', label: 'Cheapest', color: 'from-gray-500 to-slate-500' },
] as const

