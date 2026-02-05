import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, Navigation, Search, ArrowUpDown } from 'lucide-react'
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
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSubmit) {
      onSubmit()
    }
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

        {/* Submit Button - Top Right */}
        {onSubmit && (
          <motion.button
            type="submit"
            onClick={handleSubmit}
            disabled={isLoading || isGeocoding || !origin.trim() || !destination.trim()}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            whileHover={{ scale: isLoading || isGeocoding ? 1 : 1.05 }}
            whileTap={{ scale: isLoading || isGeocoding ? 1 : 0.95 }}
            className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden text-sm flex items-center gap-2"
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
                  <div className="loading-spinner" />
                </motion.div>
              ) : isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-center"
                >
                  <div className="loading-spinner" />
                </motion.div>
              ) : (
                <motion.div
                  key="search"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center"
                >
                  <Search className="w-4 h-4 mr-1" />
                  <span>Find Routes</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <AddressAutocomplete
              value={origin}
              onChange={onOriginChange}
              placeholder="Select or search for origin..."
              label="Origin"
              icon={<MapPin className="w-4 h-4 mr-2 text-primary-600" />}
              error={originError}
              required
            />
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
