import React, { useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRoute } from '../contexts/RouteContext'
import { useUser } from '../contexts/UserContext'
import GoogleMapView from './GoogleMapView'
import RouteForm from './RouteForm'
import OriginDestination from './OriginDestination'
import RealTimePanel from './RealTimePanel'
import AlternativeRoutes from './AlternativeRoutes'
import FavoritePlaces from './FavoritePlaces'
import TopNavigation from './TopNavigation'
import { routeAPI, configAPI } from '../services/api'
import type { RouteRequest, Route, Point } from '../types'

const RoutePlanner: React.FC = () => {
  const { state: routeState, dispatch: routeDispatch } = useRoute()
  const { state: userState, dispatch: userDispatch } = useUser()
  const requestInProgressRef = useRef(false)
  const [currentOrigin, setCurrentOrigin] = useState<Point | undefined>()
  const [formOrigin, setFormOrigin] = useState('')
  const [formDestination, setFormDestination] = useState('')
  const [originError, setOriginError] = useState<string | null>(null)
  const [destinationError, setDestinationError] = useState<string | null>(null)
  const routeFormRef = useRef<HTMLDivElement>(null)
  const [isGeocoding, setIsGeocoding] = useState(false)

  const handleRouteRequest = async (request: RouteRequest): Promise<void> => {
    // Prevent duplicate requests
    if (requestInProgressRef.current) {
      if (import.meta.env.DEV) {
        console.log('Route request already in progress, skipping duplicate')
      }
      return
    }

    requestInProgressRef.current = true
    routeDispatch({ type: 'SET_LOADING', payload: true })
    routeDispatch({ type: 'CLEAR_ERROR' })

    try {
      // Log request for debugging
      if (import.meta.env.DEV) {
        console.log('Calculating route:', {
          origin: request.origin,
          destination: request.destination,
          preferences: request.preferences,
          transport_modes: request.transport_modes,
        })
      }

      const response = await routeAPI.calculateRoute(request)

      if (import.meta.env.DEV) {
        console.log('Route calculation successful:', {
          routesCount: response.routes.length,
          alternativesCount: response.alternatives.length,
          processingTime: response.processing_time,
        })
      }

      routeDispatch({ type: 'SET_ROUTES', payload: response })
      routeDispatch({
        type: 'SET_LAST_REQUEST',
        payload: {
          origin: request.origin,
          destination: request.destination,
          preferences: request.preferences
        }
      })

      // Update current origin if it's from the form
      if (!currentOrigin ||
          (Math.abs(currentOrigin.lat - request.origin.lat) > 0.001 ||
           Math.abs(currentOrigin.lng - request.origin.lng) > 0.001)) {
        setCurrentOrigin(request.origin)
      }

      // Calculate gamification rewards for the first route (non-blocking)
      if (response.routes.length > 0) {
        routeAPI.calculateRewards(response.routes[0], userState.profile)
          .then((rewards) => {
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
          })
          .catch((error) => {
            // Log error but don't block UI - rewards are non-critical
            console.warn('Failed to calculate rewards:', error)
          })
      }
    } catch (error) {
      let errorMessage = error instanceof Error ? error.message : 'Failed to calculate routes'

      // Check if backend is reachable
      if (errorMessage.includes('timeout') || errorMessage.includes('ECONNABORTED')) {
        try {
          // Try to check backend health
          await configAPI.healthCheck()
          errorMessage = 'Route calculation timed out. The backend is running but route calculation is taking too long. Please try again with simpler route preferences.'
        } catch (healthError) {
          errorMessage = 'Backend server is not responding. Please make sure the backend is running on http://localhost:8000'
        }
      }

      console.error('Route calculation error:', error)
      routeDispatch({ type: 'SET_ERROR', payload: errorMessage })
    } finally {
      routeDispatch({ type: 'SET_LOADING', payload: false })
      requestInProgressRef.current = false
    }
  }

  const handleRouteSelect = (route: Route): void => {
    routeDispatch({ type: 'SELECT_ROUTE', payload: route })
  }

  const handleFavoritePlaceSelect = async (place: { location: Point; address: string; name: string }) => {
    // Set the destination in the form
    setFormDestination(place.address)

    // If we have an origin, calculate route immediately
    if (currentOrigin) {
      const request: RouteRequest = {
        origin: currentOrigin,
        destination: place.location,
        preferences: routeState.lastRequest?.preferences || ['fastest'],
        transport_modes: ['walking', 'biking', 'bus'],
        max_walking_distance: 500,
        avoid_highways: false,
        accessibility_requirements: []
      }
      await handleRouteRequest(request)
    }
  }

  const handleOriginChange = async (address: string) => {
    setFormOrigin(address)
    setOriginError(null)
    if (address) {
      try {
        const point = await routeAPI.geocodeAddress(address)
        setCurrentOrigin(point)
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to geocode origin'
        setOriginError(errorMessage)
        console.warn('Failed to geocode origin:', error)
      }
    }
  }

  const handleDestinationChange = (address: string) => {
    setFormDestination(address)
    setDestinationError(null)
  }

  const handleFormSubmit = () => {
    // Trigger RouteForm submission by finding the form and submitting it
    if (routeFormRef.current) {
      const form = routeFormRef.current.querySelector('form') as HTMLFormElement
      if (form) {
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true })
        form.dispatchEvent(submitEvent)
      }
    }
  }

  return (
    <div className="min-h-screen">
      {/* Side Navigation */}
      <TopNavigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 pt-6">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-6 sm:mb-8"
        >
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900">
            <span className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">Destination AI</span>
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-2">
            AI-powered route planning for Vancouver
          </p>
        </motion.div>

      {/* Mobile-first responsive layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 items-stretch">
        {/* Origin/Destination and Favorite Places Row */}
        <div className="lg:col-span-2">
          <OriginDestination
            origin={formOrigin}
            destination={formDestination}
            onOriginChange={handleOriginChange}
            onDestinationChange={handleDestinationChange}
            originError={originError}
            destinationError={destinationError}
            onSubmit={handleFormSubmit}
            isLoading={routeState.isLoading}
            isGeocoding={isGeocoding}
          />
        </div>

        {/* Favorite Places */}
        <div className="lg:col-span-1 flex flex-col">
          <FavoritePlaces
            onSelectPlace={handleFavoritePlaceSelect}
            currentOrigin={currentOrigin}
          />
        </div>

        {/* Map */}
        <div className="lg:col-span-2 flex flex-col">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col flex-1 min-h-[400px] sm:min-h-[500px] lg:min-h-[600px] rounded-2xl overflow-hidden"
          >
            <GoogleMapView
              routes={routeState.currentRoutes}
              selectedRoute={routeState.selectedRoute}
              lastRequest={routeState.lastRequest}
              apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''}
            />
          </motion.div>
        </div>

        {/* Real-time Updates & Alerts */}
        <div className="lg:col-span-1 flex flex-col">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="h-full"
          >
            <RealTimePanel />
          </motion.div>
        </div>

        {/* Route Results */}
        {routeState.currentRoutes.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="lg:col-span-3"
          >
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
                className="glass-card-strong p-4 sm:p-6"
              >
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6 flex items-center">
                  <div className="w-2 h-2 bg-accent-500 rounded-full mr-3" />
                  Route Options
                </h2>
                <AlternativeRoutes
                  routes={routeState.currentRoutes}
                  selectedRoute={routeState.selectedRoute}
                  onRouteSelect={handleRouteSelect}
                />
              </motion.div>
            </AnimatePresence>
          </motion.div>
        )}

        {/* Route Preferences Form - Last Component */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="lg:col-span-3"
        >
          <div className="glass-card-strong p-4 sm:p-6" ref={routeFormRef}>
            <RouteForm
              onSubmit={handleRouteRequest}
              isLoading={routeState.isLoading}
              onOriginChange={handleOriginChange}
              onDestinationChange={handleDestinationChange}
              initialOrigin={formOrigin}
              initialDestination={formDestination}
              isGeocoding={isGeocoding}
              onGeocodingChange={setIsGeocoding}
            />
          </div>
        </motion.div>
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {routeState.error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-4 sm:mt-6 glass-card border-l-4 border-red-500 bg-red-50/80 p-4"
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
    </div>
  )
}

export default RoutePlanner
