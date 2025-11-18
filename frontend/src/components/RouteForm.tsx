import React, { useState } from 'react'
import { Search, MapPin, Settings, Navigation, Clock, Shield, Leaf, Mountain, Heart, DollarSign, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'
import ModeSelector from './ModeSelector'
import AddressAutocomplete from './AddressAutocomplete'
import type { RouteRequest, Point } from '../types'
import { DEFAULT_PREFERENCES, DEFAULT_TRANSPORT_MODES, WALKING_DISTANCE_CONFIG, ROUTE_PREFERENCE_OPTIONS } from '../config'
import { routeAPI } from '../services/api'

interface RouteFormProps {
  onSubmit: (request: RouteRequest) => void
  isLoading: boolean
}

const RouteForm: React.FC<RouteFormProps> = ({ onSubmit, isLoading }) => {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [preferences, setPreferences] = useState<string[]>([...DEFAULT_PREFERENCES])
  const [transportModes, setTransportModes] = useState<string[]>([...DEFAULT_TRANSPORT_MODES])
  const [maxWalkingDistance, setMaxWalkingDistance] = useState<number>(WALKING_DISTANCE_CONFIG.DEFAULT)
  const [isGeocoding, setIsGeocoding] = useState(false)
  const [geocodingError, setGeocodingError] = useState<string | null>(null)
  const [originError, setOriginError] = useState<string | null>(null)
  const [destinationError, setDestinationError] = useState<string | null>(null)

  const preferenceOptions = ROUTE_PREFERENCE_OPTIONS.map((option) => ({
    ...option,
    icon: {
      fastest: Clock,
      safest: Shield,
      energy_efficient: Leaf,
      scenic: Mountain,
      healthy: Heart,
      cheapest: DollarSign,
    }[option.value] || Clock,
  }))


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

    try {
      // Geocode the address using Google Places API
      const point = await routeAPI.geocodeAddress(address)

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

    if (!origin.trim() || !destination.trim()) {
      if (!origin.trim()) {
        setOriginError('Please select an origin address')
      }
      if (!destination.trim()) {
        setDestinationError('Please select a destination address')
      }
      return
    }

    setIsGeocoding(true)

    try {
      // Geocode both addresses in parallel
      const [originPoint, destinationPoint] = await Promise.all([
        geocodeAddress(origin).catch((error) => {
          setOriginError(error instanceof Error ? error.message : 'Failed to geocode origin')
          throw error
        }),
        geocodeAddress(destination).catch((error) => {
          setDestinationError(error instanceof Error ? error.message : 'Failed to geocode destination')
          throw error
        }),
      ])

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
      setIsGeocoding(false)
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
      {/* Origin and Destination */}
      <div className="space-y-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <AddressAutocomplete
            value={origin}
            onChange={(value) => {
              setOrigin(value)
              setOriginError(null)
            }}
            placeholder="Select or search for origin..."
            label="Origin"
            icon={<MapPin className="w-4 h-4 mr-2 text-primary-600" />}
            error={originError}
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <AddressAutocomplete
            value={destination}
            onChange={(value) => {
              setDestination(value)
              setDestinationError(null)
            }}
            placeholder="Select or search for destination..."
            label="Destination"
            icon={<Navigation className="w-4 h-4 mr-2 text-primary-600" />}
            error={destinationError}
            required
          />
        </motion.div>
      </div>

      {/* Route Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
      >
        <label className="flex items-center text-sm font-semibold text-gray-700 mb-4">
          <Settings className="w-4 h-4 mr-2 text-primary-600" />
          Route Preferences
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
          {preferenceOptions.map((option, index) => {
            const Icon = option.icon
            const isSelected = preferences.includes(option.value)
            return (
              <motion.button
                key={option.value}
                type="button"
                onClick={() => handlePreferenceChange(option.value)}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2, delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  "p-2 sm:p-3 rounded-xl border-2 transition-all duration-300 relative overflow-hidden min-h-[60px] sm:min-h-[70px] flex flex-col items-center justify-center",
                  isSelected
                    ? 'border-primary-500/50 bg-primary-50/80 text-primary-700 shadow-lg'
                    : 'border-white/40 hover:border-white/60 text-gray-700 hover:bg-white/50'
                )}
              >
                <div className="text-center relative z-10">
                  <div className={cn(
                    "w-6 h-6 mx-auto mb-1 rounded-lg flex items-center justify-center text-white",
                    `bg-gradient-to-br ${option.color}`
                  )}>
                    <Icon className="w-3 h-3" />
                  </div>
                  <div className="text-xs font-medium leading-tight">{option.label}</div>
                </div>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-1 right-1 w-3 h-3 bg-primary-500 rounded-full flex items-center justify-center"
                  >
                    <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  </motion.div>
                )}
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

      {/* Max Walking Distance */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.9 }}
      >
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Max Walking Distance
        </label>
        <div className="glass-card p-4">
          <input
            type="range"
            min={WALKING_DISTANCE_CONFIG.MIN}
            max={WALKING_DISTANCE_CONFIG.MAX}
            step={WALKING_DISTANCE_CONFIG.STEP}
            value={maxWalkingDistance}
            onChange={(e) => setMaxWalkingDistance(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>{WALKING_DISTANCE_CONFIG.MIN}m</span>
            <span className="font-semibold text-primary-600">{maxWalkingDistance}m</span>
            <span>{WALKING_DISTANCE_CONFIG.MAX}m</span>
          </div>
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

      {/* Submit Button */}
      <motion.button
        type="submit"
        disabled={isLoading || isGeocoding || !origin.trim() || !destination.trim()}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 1.0 }}
        whileHover={{ scale: isLoading || isGeocoding ? 1 : 1.02 }}
        whileTap={{ scale: isLoading || isGeocoding ? 1 : 0.98 }}
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {isGeocoding ? (
            <motion.div
              key="geocoding"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center"
            >
              <div className="loading-spinner mr-3" />
              <span>Finding Locations...</span>
            </motion.div>
          ) : isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center"
            >
              <div className="loading-spinner mr-3" />
              <span>Calculating Routes...</span>
            </motion.div>
          ) : (
            <motion.div
              key="search"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center"
            >
              <Search className="w-5 h-5 mr-2" />
              <span>Find Routes</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </motion.form>
  )
}

export default RouteForm
