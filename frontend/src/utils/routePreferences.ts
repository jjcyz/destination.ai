/**
 * Centralized route preference utilities
 * Provides consistent colors, icons, and styling across components
 */

import { Clock, Shield, Leaf, MapPin, Mountain, Heart, DollarSign, Navigation } from 'lucide-react'

export type RoutePreference =
  | 'fastest'
  | 'safest'
  | 'energy_efficient'
  | 'scenic'
  | 'healthy'
  | 'cheapest'

/**
 * Get hex color for route preference (for Google Maps)
 */
export const getRouteColorHex = (preference: string): string => {
  const colors: Record<RoutePreference | string, string> = {
    fastest: '#ef4444',
    safest: '#22c55e',
    energy_efficient: '#3b82f6',
    scenic: '#f59e0b',
    healthy: '#10b981',
    cheapest: '#8b5cf6',
  }
  return colors[preference] || '#6b7280'
}

/**
 * Get Tailwind gradient classes for route preference
 */
export const getRouteColorGradient = (preference: string): string => {
  const colors: Record<RoutePreference | string, string> = {
    fastest: 'from-red-500 to-pink-500',
    safest: 'from-green-500 to-emerald-500',
    energy_efficient: 'from-blue-500 to-cyan-500',
    scenic: 'from-yellow-500 to-orange-500',
    healthy: 'from-purple-500 to-violet-500',
    cheapest: 'from-gray-500 to-slate-500',
  }
  return colors[preference] || 'from-gray-500 to-slate-500'
}

/**
 * Get icon component for route preference
 */
export const getPreferenceIcon = (preference: string) => {
  const icons: Record<RoutePreference | string, typeof Clock> = {
    fastest: Clock,
    safest: Shield,
    energy_efficient: Leaf,
    scenic: MapPin,
    healthy: Heart,
    cheapest: DollarSign,
  }
  return icons[preference] || Navigation
}

/**
 * Get icon component for route preference (alternative set)
 * Used when different icons are needed (e.g., Mountain instead of MapPin for scenic)
 */
export const getPreferenceIconAlt = (preference: string) => {
  const icons: Record<RoutePreference | string, typeof Clock> = {
    fastest: Clock,
    safest: Shield,
    energy_efficient: Leaf,
    scenic: Mountain,
    healthy: Heart,
    cheapest: DollarSign,
  }
  return icons[preference] || Clock
}

