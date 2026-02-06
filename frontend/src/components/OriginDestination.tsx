import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, Navigation, ArrowUpDown, Crosshair, Loader2 } from 'lucide-react'
import AddressAutocomplete from './AddressAutocomplete'

interface OriginDestinationProps {
  origin: string
  destination: string
  onOriginChange: (value: string) => void
  onDestinationChange: (value: string) => void
  originError?: string | null
  destinationError?: string | null
  onSubmit?: () => void
  onSwap?: () => void
  isLoading?: boolean
  isGeocoding?: boolean
}

const OriginDestination: React.FC<OriginDestinationProps> = ({
  origin,
  destination,
  onOriginChange,
  onDestinationChange,
  originError,
  destinationError,
  onSubmit,
  onSwap,
  isLoading = false,
  isGeocoding = false
}) => {
  const [isGettingLocation, setIsGettingLocation] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSubmit) {
      onSubmit()
    }
  }

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser')
      return
    }

    setIsGettingLocation(true)
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude

        // Reverse geocode to get address
        try {
          const response = await fetch(
            `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
          )
          const data = await response.json()

          if (data.results && data.results[0]) {
            onOriginChange(data.results[0].formatted_address)
          } else {
            onOriginChange(`${lat.toFixed(6)}, ${lng.toFixed(6)}`)
          }
        } catch (error) {
          console.error('Reverse geocoding failed:', error)
          onOriginChange(`${lat.toFixed(6)}, ${lng.toFixed(6)}`)
        } finally {
          setIsGettingLocation(false)
        }
      },
      (error) => {
        console.error('Error getting location:', error)
        alert('Unable to get your location. Please enable location services.')
        setIsGettingLocation(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card-strong p-4 sm:p-6 relative z-50"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 flex items-center">
          Plan Your Route
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <div className="flex gap-2">
              <div className="flex-1">
                <AddressAutocomplete
                  value={origin}
                  onChange={onOriginChange}
                  placeholder="Select or search for origin..."
                  label="Origin"
                  icon={<MapPin className="w-4 h-4 mr-2 text-primary-600" />}
                  error={originError}
                  required
                />
              </div>
              <div className="pt-8">
                <motion.button
                  type="button"
                  onClick={handleUseCurrentLocation}
                  disabled={isGettingLocation || isLoading || isGeocoding}
                  whileHover={{ scale: isGettingLocation ? 1 : 1.05 }}
                  whileTap={{ scale: isGettingLocation ? 1 : 0.95 }}
                  className="p-3 bg-primary-50 hover:bg-primary-100 border-2 border-primary-200 hover:border-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Use current location"
                  title="Use current location"
                >
                  {isGettingLocation ? (
                    <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                  ) : (
                    <Crosshair className="w-5 h-5 text-primary-600" />
                  )}
                </motion.button>
              </div>
            </div>
          </motion.div>

          {/* Swap Button */}
          {onSwap && (
            <div className="flex justify-center my-2 relative">
              <motion.button
                type="button"
                onClick={onSwap}
                disabled={isLoading || isGeocoding}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 bg-white hover:bg-primary-50 border-2 border-primary-200 hover:border-primary-400 rounded-full shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed z-10"
                aria-label="Swap origin and destination"
              >
                <ArrowUpDown className="w-4 h-4 text-primary-600" />
              </motion.button>
            </div>
          )}

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <AddressAutocomplete
              value={destination}
              onChange={onDestinationChange}
              placeholder="Select or search for destination..."
              label="Destination"
              icon={<Navigation className="w-4 h-4 mr-2 text-primary-600" />}
              error={destinationError}
              required
            />
          </motion.div>
        </div>

      </form>
    </motion.div>
  )
}

export default OriginDestination
