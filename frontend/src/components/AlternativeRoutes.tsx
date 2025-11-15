import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Clock,
  MapPin,
  TrendingUp,
  Leaf,
  Shield,
  DollarSign,
  ChevronDown,
  Navigation
} from 'lucide-react'
import { cn } from '../utils/cn'
import { Route } from '../contexts/RouteContext'

interface AlternativeRoutesProps {
  routes: Route[]
  selectedRoute: Route | null
  onRouteSelect: (route: Route) => void
  className?: string
}

const AlternativeRoutes: React.FC<AlternativeRoutesProps> = ({
  routes,
  selectedRoute,
  onRouteSelect,
  className
}) => {
  const [expandedRoute, setExpandedRoute] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'time' | 'distance' | 'sustainability' | 'cost'>('time')

  const getPreferenceIcon = (preference: string) => {
    const icons = {
      fastest: Clock,
      safest: Shield,
      energy_efficient: Leaf,
      scenic: MapPin,
      healthy: TrendingUp,
      cheapest: DollarSign,
    }
    return icons[preference as keyof typeof icons] || Navigation
  }

  const getPreferenceColor = (preference: string) => {
    const colors = {
      fastest: 'from-red-500 to-pink-500',
      safest: 'from-green-500 to-emerald-500',
      energy_efficient: 'from-blue-500 to-cyan-500',
      scenic: 'from-yellow-500 to-orange-500',
      healthy: 'from-purple-500 to-violet-500',
      cheapest: 'from-gray-500 to-slate-500',
    }
    return colors[preference as keyof typeof colors] || 'from-gray-500 to-slate-500'
  }

  const formatTime = (seconds: number) => {
    // Convert seconds to minutes (backend returns time in seconds)
    if (seconds < 60) {
      return `${seconds}s`
    }
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  const formatDistance = (meters: number) => {
    if (meters < 1000) return `${meters}m`
    return `${(meters / 1000).toFixed(1)}km`
  }

  const sortedRoutes = [...routes].sort((a, b) => {
    switch (sortBy) {
      case 'time':
        return a.total_time - b.total_time
      case 'distance':
        return a.total_distance - b.total_distance
      case 'sustainability':
        return (b.energy_efficiency || 0) - (a.energy_efficiency || 0)
      case 'cost':
        return (a.total_sustainability_points || 0) - (b.total_sustainability_points || 0)
      default:
        return 0
    }
  })

  if (routes.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn("space-y-4", className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <div className="w-2 h-2 bg-accent-500 rounded-full mr-3" />
          Alternative Routes
        </h3>

        {/* Sort options */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-sm bg-white/60 border border-white/40 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
          >
            <option value="time">Time</option>
            <option value="distance">Distance</option>
            <option value="sustainability">Eco-Friendly</option>
            <option value="cost">Cost</option>
          </select>
        </div>
      </div>

      {/* Routes List */}
      <div className="space-y-3">
        <AnimatePresence>
          {sortedRoutes.map((route, index) => {
            const isSelected = selectedRoute?.id === route.id
            const isExpanded = expandedRoute === route.id
            const PreferenceIcon = getPreferenceIcon(route.preference)

            return (
              <motion.div
                key={route.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={cn(
                  "glass-card p-4 cursor-pointer transition-all duration-300",
                  isSelected
                    ? "ring-2 ring-primary-500/50 bg-primary-50/50"
                    : "hover:bg-white/60"
                )}
                onClick={() => onRouteSelect(route)}
              >
                {/* Route Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center text-white",
                      `bg-gradient-to-br ${getPreferenceColor(route.preference)}`
                    )}>
                      <PreferenceIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 capitalize">
                        {route.preference.replace('_', ' ')} Route
                      </h4>
                      <p className="text-sm text-gray-500">
                        {route.steps.length} segments
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-1 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>{formatTime(route.total_time)}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-gray-600">
                      <MapPin className="w-4 h-4" />
                      <span>{formatDistance(route.total_distance)}</span>
                    </div>
                  </div>
                </div>

                {/* Route Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatTime(route.total_time)}
                    </div>
                    <div className="text-xs text-gray-500">Duration</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatDistance(route.total_distance)}
                    </div>
                    <div className="text-xs text-gray-500">Distance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">
                      {Math.round((route.energy_efficiency || 0.9) * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">Eco Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-600">
                      {route.total_sustainability_points || 0}
                    </div>
                    <div className="text-xs text-gray-500">Points</div>
                  </div>
                </div>

                {/* Expandable Details */}
                <motion.button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setExpandedRoute(isExpanded ? null : route.id)
                  }}
                  className="w-full flex items-center justify-center space-x-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
                >
                  <span>{isExpanded ? 'Hide' : 'Show'} Details</span>
                  <motion.div
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className="w-4 h-4" />
                  </motion.div>
                </motion.button>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="pt-4 border-t border-white/40">
                        <h5 className="font-medium text-gray-900 mb-3">Route Steps</h5>
                        <div className="space-y-2">
                          {route.steps.map((step, stepIndex) => (
                            <div
                              key={stepIndex}
                              className="flex items-center justify-between p-3 bg-white/40 rounded-lg hover:bg-white/60 transition-colors"
                            >
                              <div className="flex items-center space-x-3 flex-1 min-w-0">
                                <div className={cn(
                                  "w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm flex-shrink-0",
                                  `mode-${step.mode}`
                                )}>
                                  {step.mode === 'walking' && '🚶'}
                                  {step.mode === 'biking' && '🚴'}
                                  {step.mode === 'scooter' && '🛴'}
                                  {step.mode === 'car' && '🚗'}
                                  {step.mode === 'bus' && '🚌'}
                                  {step.mode === 'skytrain' && '🚇'}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="font-medium text-gray-900 text-sm sm:text-base truncate">
                                    {step.instructions || `Continue ${formatDistance(step.distance)}`}
                                  </div>
                                  <div className="text-xs sm:text-sm text-gray-500 mt-0.5">
                                    <span className="capitalize">{step.mode}</span>
                                    {step.distance > 0 && (
                                      <>
                                        <span className="mx-1">•</span>
                                        {formatDistance(step.distance)}
                                      </>
                                    )}
                                    {step.sustainability_points > 0 && (
                                      <>
                                        <span className="mx-1">•</span>
                                        <span className="text-green-600 font-medium">
                                          +{step.sustainability_points} pts
                                        </span>
                                      </>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div className="text-xs sm:text-sm text-gray-600 ml-3 flex-shrink-0">
                                {formatTime(step.estimated_time)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default AlternativeRoutes
