import React, { useState, useEffect } from 'react'
import { Search, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'
import ModeSelector from './ModeSelector'
import OriginDestination from './OriginDestination'
import type { RouteRequest, Point } from '../types'
import { DEFAULT_PREFERENCES, DEFAULT_TRANSPORT_MODES, WALKING_DISTANCE_CONFIG, ROUTE_PREFERENCE_OPTIONS } from '../config'
import { routeAPI } from '../services/api'
import { getCachedGeocode, cacheGeocode } from '../utils/geocodingCache'
import { getPreferenceIconAlt } from '../utils/routePreferences'
import { saveFormState, loadFormState } from '../utils/formPersistence'

interface RouteFormProps {
  onSubmit: (request: RouteRequest) => void
  isLoading: boolean
  onOriginChange?: (origin: string) => void
  onDestinationChange?: (destination: string) => void
  initialOrigin?: string
  initialDestination?: string
  onFormSubmit?: () => void
  isGeocoding?: boolean
  onGeocodingChange?: (isGeocoding: boolean) => void
}

const RouteForm: React.FC<RouteFormProps> = ({
  onSubmit,
  isLoading,
  onOriginChange,
  onDestinationChange,
  initialOrigin = '',
  initialDestination = '',
  onFormSubmit,
  isGeocoding = false,
  onGeocodingChange,
}) => {
  const [origin, setOrigin] = useState(initialOrigin)
  const [destination, setDestination] = useState(initialDestination)
  const [preferences, setPreferences] = useState<string[]>([...DEFAULT_PREFERENCES])
  const [transportModes, setTransportModes] = useState<string[]>([...DEFAULT_TRANSPORT_MODES])
  const [maxWalkingDistance, setMaxWalkingDistance] = useState<number>(WALKING_DISTANCE_CONFIG.DEFAULT)
  const [geocodingError, setGeocodingError] = useState<string | null>(null)
  const [originError, setOriginError] = useState<string | null>(null)
  const [destinationError, setDestinationError] = useState<string | null>(null)

  // Load persisted form state on mount
  useEffect(() => {
    const savedState = loadFormState()
    if (savedState) {
      setPreferences(savedState.preferences)
      setTransportModes(savedState.transportModes)
      setMaxWalkingDistance(savedState.maxWalkingDistance)
    }
  }, [])

  const preferenceOptions = ROUTE_PREFERENCE_OPTIONS.map((option) => ({
    ...option,
    icon: getPreferenceIconAlt(option.value),
  }))

  // Update form when initial values change externally
  useEffect(() => {
    if (initialOrigin) setOrigin(initialOrigin)
  }, [initialOrigin])

  useEffect(() => {
    if (initialDestination) setDestination(initialDestination)
  }, [initialDestination])


  const handlePreferenceChange = (preference: string) => {
    setPreferences(prev =>
      prev.includes(preference)
        ? prev.filter(p => p !== preference)
        : [...prev, preference]
    )
  }

  const handleTransportModeChange = (modes: string[]) => {
    setTransportModes(modes)
  }

  const geocodeAddress = async (address: string): Promise<Point> => {
    if (!address.trim()) {
      throw new Error('Please enter an address')
    }

    // Check cache first
    const cached = getCachedGeocode(address)
    if (cached) {
      if (import.meta.env.DEV) {
        console.log(`Using cached geocode for "${address}"`)
      }
      return cached
    }

    try {
      // Geocode the address using Google Places API
      const point = await routeAPI.geocodeAddress(address)

      // Cache the result
      cacheGeocode(address, point)

      // Validate that we got valid coordinates
      if (!point || typeof point.lat !== 'number' || typeof point.lng !== 'number') {
        throw new Error('Invalid coordinates returned from geocoding service')
      }

      // Log for debugging
      if (import.meta.env.DEV) {
        console.log(`Geocoded "${address}" to:`, point)
      }

      return point
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Geocoding failed'
      console.error(`Geocoding error for "${address}":`, error)
      throw new Error(
        `Could not find location "${address}". Please select a valid address from the dropdown. ` +
        `Error: ${errorMessage}`
      )
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Clear previous errors
    setOriginError(null)
    setDestinationError(null)
    setGeocodingError(null)

    // Use initialOrigin/initialDestination if origin/destination are empty (they come from parent)
    const finalOrigin = origin.trim() || initialOrigin.trim()
    const finalDestination = destination.trim() || initialDestination.trim()

    if (!finalOrigin || !finalDestination) {
      if (!finalOrigin) {
        setOriginError('Please select an origin address')
      }
      if (!finalDestination) {
        setDestinationError('Please select a destination address')
      }
      return
    }

    onGeocodingChange?.(true)

    try {
      // Geocode both addresses in parallel
      const [originPoint, destinationPoint] = await Promise.all([
        geocodeAddress(finalOrigin).catch((error) => {
          const errorMsg = error instanceof Error ? error.message : 'Failed to geocode origin'
          setOriginError(errorMsg)
          throw error
        }),
        geocodeAddress(finalDestination).catch((error) => {
          const errorMsg = error instanceof Error ? error.message : 'Failed to geocode destination'
          setDestinationError(errorMsg)
          throw error
        }),
      ])

      // Save form state for next time
      saveFormState({
        origin: finalOrigin,
        destination: finalDestination,
        preferences,
        transportModes,
        maxWalkingDistance
      })

      const request: RouteRequest = {
        origin: originPoint,
        destination: destinationPoint,
        preferences,
        transport_modes: transportModes,
        max_walking_distance: maxWalkingDistance,
        avoid_highways: false,
        accessibility_requirements: [],
      }

      onSubmit(request)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to geocode addresses'
      setGeocodingError(errorMessage)
      console.error('Geocoding error:', error)
    } finally {
      onGeocodingChange?.(false)
    }
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      {/* Origin and Destination - Now handled by parent component */}

      {/* Route Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
      >
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Route Preferences
        </label>
        <div className="flex flex-wrap gap-2">
          {preferenceOptions.map((option, index) => {
            const isSelected = preferences.includes(option.value)
            return (
              <motion.button
                key={option.value}
                type="button"
                onClick={() => handlePreferenceChange(option.value)}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2, delay: 0.6 + index * 0.05 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  "px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all duration-200",
                  isSelected
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'bg-white/60 text-gray-700 hover:bg-white/80 border border-white/40'
                )}
              >
                {option.label}
              </motion.button>
            )
          })}
        </div>
      </motion.div>

      {/* Transport Modes */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.7 }}
      >
        <ModeSelector
          selectedModes={transportModes}
          onModeChange={handleTransportModeChange}
        />
      </motion.div>

      {/* Max Walking Distance Slider */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.9 }}
        className="sm:glass-input"
      >
        <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
          Max Walking Distance Slider
        </label>
        <div className="flex items-center gap-2 sm:gap-3">
          <input
            type="range"
            min={WALKING_DISTANCE_CONFIG.MIN}
            max={WALKING_DISTANCE_CONFIG.MAX}
            step={WALKING_DISTANCE_CONFIG.STEP}
            value={maxWalkingDistance}
            onChange={(e) => setMaxWalkingDistance(Number(e.target.value))}
            className="flex-1 h-1.5 sm:h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <span className="text-xs sm:text-sm font-semibold text-primary-600 min-w-[50px] sm:min-w-[60px] text-right">
            {maxWalkingDistance}m
          </span>
        </div>
        <div className="hidden sm:flex justify-between text-xs text-gray-600 mt-1">
          <span>{WALKING_DISTANCE_CONFIG.MIN}m</span>
          <span>{WALKING_DISTANCE_CONFIG.MAX}m</span>
        </div>
      </motion.div>

      {/* Geocoding Error Display */}
      <AnimatePresence>
        {geocodingError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-card border-l-4 border-red-500 bg-red-50/80 p-4"
          >
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5 mr-3" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-800 mb-1">Geocoding Error</h3>
                <p className="text-sm text-red-700 mb-2">{geocodingError}</p>
                <p className="text-xs text-red-600">
                  Please select addresses from the dropdown above.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.form>
  )
}

export default RouteForm
