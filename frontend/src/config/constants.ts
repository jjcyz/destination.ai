/**
 * Application constants and configuration values.
 * Centralized location for all hardcoded values and configuration.
 */

/**
 * API configuration
 */
const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
}

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000, // 30 seconds
} as const

/**
 * Vancouver address options for autocomplete
 * These are well-known locations that users can select from
 */
export interface AddressOption {
  label: string
  value: string
  category: 'landmark' | 'neighborhood' | 'transit' | 'institution'
}

export const VANCOUVER_ADDRESSES: AddressOption[] = [
  // Landmarks
  { label: 'Stanley Park', value: 'Stanley Park', category: 'landmark' },
  { label: 'Vancouver Downtown', value: 'Vancouver Downtown', category: 'landmark' },
  { label: 'Gastown', value: 'Gastown', category: 'landmark' },
  { label: 'Granville Island', value: 'Granville Island', category: 'landmark' },
  { label: 'Canada Place', value: 'Canada Place', category: 'landmark' },
  { label: 'Science World', value: 'Science World', category: 'landmark' },
  { label: 'Vancouver Art Gallery', value: 'Vancouver Art Gallery', category: 'landmark' },
  { label: 'Queen Elizabeth Park', value: 'Queen Elizabeth Park', category: 'landmark' },
  { label: 'Capilano Suspension Bridge', value: 'Capilano Suspension Bridge', category: 'landmark' },
  { label: 'Grouse Mountain', value: 'Grouse Mountain', category: 'landmark' },

  // Neighborhoods
  { label: 'Yaletown', value: 'Yaletown', category: 'neighborhood' },
  { label: 'Kitsilano', value: 'Kitsilano', category: 'neighborhood' },
  { label: 'Commercial Drive', value: 'Commercial Drive', category: 'neighborhood' },
  { label: 'Chinatown', value: 'Chinatown', category: 'neighborhood' },
  { label: 'West End', value: 'West End', category: 'neighborhood' },
  { label: 'Mount Pleasant', value: 'Mount Pleasant', category: 'neighborhood' },
  { label: 'Olympic Village', value: 'Olympic Village', category: 'neighborhood' },
  { label: 'False Creek', value: 'False Creek', category: 'neighborhood' },
  { label: 'Coal Harbour', value: 'Coal Harbour', category: 'neighborhood' },
  { label: 'East Vancouver', value: 'East Vancouver', category: 'neighborhood' },

  // Transit Hubs
  { label: 'Vancouver Airport (YVR)', value: 'Vancouver Airport', category: 'transit' },
  { label: 'Waterfront Station', value: 'Waterfront Station', category: 'transit' },
  { label: 'Pacific Centre Station', value: 'Pacific Centre Station', category: 'transit' },
  { label: 'Broadway-City Hall Station', value: 'Broadway-City Hall Station', category: 'transit' },
  { label: 'King Edward Station', value: 'King Edward Station', category: 'transit' },
  { label: 'Oakridge-41st Station', value: 'Oakridge-41st Station', category: 'transit' },
  { label: 'Marine Drive Station', value: 'Marine Drive Station', category: 'transit' },
  { label: 'Bridgeport Station', value: 'Bridgeport Station', category: 'transit' },
  { label: 'Main Street-Science World Station', value: 'Main Street-Science World Station', category: 'transit' },

  // Institutions
  { label: 'UBC (University of British Columbia)', value: 'UBC', category: 'institution' },
  { label: 'BC Place Stadium', value: 'BC Place Stadium', category: 'institution' },
  { label: 'Rogers Arena', value: 'Rogers Arena', category: 'institution' },
  { label: 'Vancouver General Hospital', value: 'Vancouver General Hospital', category: 'institution' },
  { label: 'St. Paul\'s Hospital', value: 'St. Paul\'s Hospital', category: 'institution' },

  // Other Cities (Greater Vancouver)
  { label: 'Burnaby', value: 'Burnaby', category: 'neighborhood' },
  { label: 'Richmond', value: 'Richmond', category: 'neighborhood' },
  { label: 'North Vancouver', value: 'North Vancouver', category: 'neighborhood' },
  { label: 'West Vancouver', value: 'West Vancouver', category: 'neighborhood' },
  { label: 'New Westminster', value: 'New Westminster', category: 'neighborhood' },
] as const

/**
 * Legacy mock coordinates - kept for reference but no longer used as fallback
 * @deprecated Use VANCOUVER_ADDRESSES with geocoding instead
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

