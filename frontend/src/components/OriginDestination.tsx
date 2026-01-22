import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, Navigation, Search } from 'lucide-react'
import AddressAutocomplete from './AddressAutocomplete'

interface OriginDestinationProps {
  origin: string
  destination: string
  onOriginChange: (value: string) => void
  onDestinationChange: (value: string) => void
  originError?: string | null
  destinationError?: string | null
  onSubmit?: () => void
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
      className="glass-card-strong p-4 sm:p-6 mb-6 relative z-50"
    >
      <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <div className="w-2 h-2 bg-primary-500 rounded-full mr-3" />
        Plan Your Route
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
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

        {/* Submit Button */}
        {onSubmit && (
          <motion.button
            type="submit"
            disabled={isLoading || isGeocoding || !origin.trim() || !destination.trim()}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            whileHover={{ scale: isLoading || isGeocoding ? 1 : 1.02 }}
            whileTap={{ scale: isLoading || isGeocoding ? 1 : 0.98 }}
            className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden mt-4 text-sm"
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
                  <div className="loading-spinner mr-2" />
                  <span className="text-sm">Finding Locations...</span>
                </motion.div>
              ) : isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-center"
                >
                  <div className="loading-spinner mr-2" />
                  <span className="text-sm">Calculating Routes...</span>
                </motion.div>
              ) : (
                <motion.div
                  key="search"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-center"
                >
                  <Search className="w-4 h-4 mr-2" />
                  <span>Find Routes</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        )}
      </form>
    </motion.div>
  )
}

export default OriginDestination
