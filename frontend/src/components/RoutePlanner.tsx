import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRoute } from '../contexts/RouteContext'
import { useUser } from '../contexts/UserContext'
import MapView from './MapView'
import RouteForm from './RouteForm'
import RealTimePanel from './RealTimePanel'
import AlternativeRoutes from './AlternativeRoutes'
import PredictiveNotifications from './PredictiveNotifications'
import { routeAPI } from '../services/api'
import type { RouteRequest, Route } from '../types'

const RoutePlanner: React.FC = () => {
  const { state: routeState, dispatch: routeDispatch } = useRoute()
  const { state: userState, dispatch: userDispatch } = useUser()
  const [showMap, setShowMap] = useState(true)

  const handleRouteRequest = async (request: RouteRequest): Promise<void> => {
    routeDispatch({ type: 'SET_LOADING', payload: true })
    routeDispatch({ type: 'CLEAR_ERROR' })

    try {
      const response = await routeAPI.calculateRoute(request)
      routeDispatch({ type: 'SET_ROUTES', payload: response })
      routeDispatch({ type: 'SET_LAST_REQUEST', payload: request })

      // Calculate gamification rewards for the first route
      if (response.routes.length > 0) {
        const rewards = await routeAPI.calculateRewards(response.routes[0], userState.profile)

        // Update user stats
        if (rewards.sustainability_points > 0) {
          userDispatch({ type: 'UPDATE_POINTS', payload: rewards.sustainability_points })
        }

        if (rewards.achievements_unlocked?.length > 0) {
          rewards.achievements_unlocked.forEach((achievementId: string) => {
            userDispatch({ type: 'ADD_ACHIEVEMENT', payload: achievementId })
          })
        }

        if (rewards.badges_earned?.length > 0) {
          rewards.badges_earned.forEach((badgeId: string) => {
            userDispatch({ type: 'ADD_BADGE', payload: badgeId })
          })
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to calculate routes'
      routeDispatch({ type: 'SET_ERROR', payload: errorMessage })
    }
  }

  const handleRouteSelect = (route: Route): void => {
    routeDispatch({ type: 'SELECT_ROUTE', payload: route })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-8 sm:mb-12"
      >
        <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 mb-4 sm:mb-6">
          <span className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">Destination AI</span>
        </h1>
        <p className="text-base sm:text-lg lg:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed px-4">
          AI-powered route planning for Vancouver. Find the best routes using multiple transportation modes.
          Get real-time traffic, weather, and transit information with intelligent recommendations.
        </p>
      </motion.div>

      {/* Mobile-first responsive layout */}
      <div className="space-y-6 lg:space-y-8">
        {/* Top Row - Form and Notifications (Mobile: stacked, Desktop: side by side) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Route Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <div className="glass-card-strong p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-3" />
                Plan Your Route
              </h2>
              <RouteForm onSubmit={handleRouteRequest} isLoading={routeState.isLoading} />
            </div>
          </motion.div>

          {/* Predictive Notifications */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="lg:col-span-1"
          >
            <PredictiveNotifications />
          </motion.div>
        </div>

        {/* Middle Row - Map */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="glass-card-strong p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <div className="w-2 h-2 bg-secondary-500 rounded-full mr-3" />
              Route Map
            </h2>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="hidden sm:inline">Live Updates</span>
              </div>
              <button
                onClick={() => setShowMap(!showMap)}
                className="btn-glass text-sm"
              >
                {showMap ? 'Hide Map' : 'Show Map'}
              </button>
            </div>
          </div>

          <AnimatePresence>
            {showMap && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
                className="h-[500px] sm:h-[600px] lg:h-[800px] xl:h-[900px] min-h-[200px]"
              >
                <MapView
                  routes={routeState.currentRoutes}
                  selectedRoute={routeState.selectedRoute}
                  lastRequest={routeState.lastRequest}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Bottom Row - Results and Real-time Updates */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Route Results */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="lg:col-span-2"
          >
            <AnimatePresence>
              {routeState.currentRoutes.length > 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -30 }}
                  transition={{ duration: 0.5 }}
                  className="glass-card-strong p-6"
                >
                  <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                    <div className="w-2 h-2 bg-accent-500 rounded-full mr-3" />
                    Route Options
                  </h2>
                  <AlternativeRoutes
                    routes={routeState.currentRoutes}
                    selectedRoute={routeState.selectedRoute}
                    onRouteSelect={handleRouteSelect}
                  />
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass-card-strong p-6 text-center"
                >
                  <div className="text-gray-400 mb-4">
                    <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Plan Your Route?</h3>
                  <p className="text-gray-600">Enter your origin and destination above to see route options.</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Real-time Updates Panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="lg:col-span-1"
          >
            <RealTimePanel />
          </motion.div>
        </div>
      </div>

      {/* Quick Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <div className="glass-card p-6 text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-xl">⚡</span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Fast Routes</h3>
          <p className="text-sm text-gray-600">Get the quickest path to your destination with real-time traffic data</p>
        </div>

        <div className="glass-card p-6 text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-xl">🌱</span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Eco-Friendly</h3>
          <p className="text-sm text-gray-600">Choose sustainable transportation options and earn rewards</p>
        </div>

        <div className="glass-card p-6 text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-xl">🎯</span>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Smart Planning</h3>
          <p className="text-sm text-gray-600">AI-powered recommendations based on weather, events, and preferences</p>
        </div>
      </motion.div>

      {/* Error Display */}
      <AnimatePresence>
        {routeState.error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-6 glass-card border-l-4 border-red-500 bg-red-50/80"
          >
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  {routeState.error}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default RoutePlanner
