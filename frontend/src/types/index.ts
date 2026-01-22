/**
 * Centralized TypeScript type definitions for the Route Recommendation System.
 * These types should match the backend Pydantic models in app/models.py
 */

/**
 * Geographic point with latitude and longitude
 */
export interface Point {
  lat: number
  lng: number
}

/**
 * Transport mode options
 */
export enum TransportMode {
  WALKING = 'walking',
  BIKING = 'biking',
  SCOOTER = 'scooter',
  CAR = 'car',
  BUS = 'bus',
  SKYTRAIN = 'skytrain',
  SEABUS = 'seabus',
  WESTCOAST_EXPRESS = 'westcoast_express',
  RIDESHARE = 'rideshare',
}

/**
 * Route preference options
 */
export enum RoutePreference {
  FASTEST = 'fastest',
  SAFEST = 'safest',
  ENERGY_EFFICIENT = 'energy_efficient',
  SCENIC = 'scenic',
  HEALTHY = 'healthy',
  CHEAPEST = 'cheapest',
}

/**
 * Transit details for transit route steps
 */
export interface TransitDetails {
  line?: string
  short_name?: string
  vehicle?: string
  vehicle_type?: string
  departure_stop?: string
  departure_stop_id?: string
  departure_time?: string
  departure_time_value?: number
  arrival_stop?: string
  arrival_stop_id?: string
  arrival_time?: string
  arrival_time_value?: number
  num_stops?: number
  headsign?: string
  // Real-time data
  real_time_departure?: string
  delay_seconds?: number
  delay_minutes?: number
  is_delayed?: boolean
  service_alerts?: Array<{
    header?: string
    description?: string
    effect?: string
  }>
}

/**
 * Individual step in a route
 */
export interface RouteStep {
  mode: TransportMode | string
  distance: number
  estimated_time: number
  slope?: number
  effort_level: string
  instructions: string
  start_point: Point
  end_point: Point
  polyline?: string  // Google Maps encoded polyline for accurate route rendering
  sustainability_points: number
  transit_details?: TransitDetails
}

/**
 * Complete route from origin to destination
 */
export interface Route {
  id: string
  origin: Point
  destination: Point
  steps: RouteStep[]
  total_distance: number
  total_time: number
  total_sustainability_points: number
  preference: RoutePreference | string
  safety_score: number
  energy_efficiency: number
  scenic_score: number
  created_at?: string
}

/**
 * Route calculation request
 */
export interface RouteRequest {
  origin: Point
  destination: Point
  preferences: RoutePreference[] | string[]
  transport_modes: TransportMode[] | string[]
  max_walking_distance: number
  avoid_highways?: boolean
  accessibility_requirements?: string[]
  departure_time?: string
}

/**
 * Response containing calculated routes
 */
export interface RouteResponse {
  request_id: string
  routes: Route[]
  alternatives: Route[]
  processing_time: number
  data_sources: string[]
}

/**
 * User profile for personalization
 */
export interface UserProfile {
  user_id: string
  preferred_modes?: TransportMode[] | string[]
  fitness_level?: string
  sustainability_goals?: boolean
  accessibility_needs?: string[]
  budget_preferences?: Record<string, number>
  time_preferences?: Record<string, number>
  level?: number
  total_sustainability_points?: number
  total_distance_saved?: number
  streak_days?: number
  achievements?: string[]
  badges?: string[]
}

/**
 * Gamification rewards
 */
export interface GamificationRewards {
  sustainability_points: number
  co2_saved: number
  achievements_unlocked: string[]
  badges_earned: string[]
  level_up: boolean
  streak_bonus: number
}

/**
 * Achievement data
 */
export interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  points_reward: number
}

/**
 * Badge data
 */
export interface Badge {
  id: string
  name: string
  description: string
  icon: string
  rarity: string
}

/**
 * Daily challenge data
 */
export interface DailyChallenge {
  id: string
  name: string
  description: string
  points_reward: number
  progress: number
  target: number
}

/**
 * Leaderboard entry
 */
export interface LeaderboardEntry {
  user_id: string
  username: string
  total_points: number
  rank: number
  level: number
}

/**
 * API configuration
 */
export interface ApiConfig {
  api_keys_status: {
    google_maps: boolean
    translink: boolean
    lime: boolean
    openweather: boolean
    all_required: boolean
  }
  instructions: string
  vancouver_bounds: {
    north: number
    south: number
    east: number
    west: number
  }
  supported_modes: string[]
  supported_preferences: string[]
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: string
  timestamp: string
  api_keys: {
    google_maps: boolean
    translink: boolean
    lime: boolean
    openweather: boolean
    all_required: boolean
  }
}

