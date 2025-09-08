import React, { useState } from 'react'
import { Search, MapPin, Settings, Navigation, Clock, Shield, Leaf, Mountain, Heart, DollarSign } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'
import ModeSelector from './ModeSelector'

interface RouteFormProps {
  onSubmit: (request: any) => void
  isLoading: boolean
}

const RouteForm: React.FC<RouteFormProps> = ({ onSubmit, isLoading }) => {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [preferences, setPreferences] = useState<string[]>(['fastest'])
  const [transportModes, setTransportModes] = useState<string[]>(['walking', 'biking', 'car', 'bus'])
  const [maxWalkingDistance, setMaxWalkingDistance] = useState(2000)

  const preferenceOptions = [
    { value: 'fastest', label: 'Fastest', icon: Clock, color: 'from-red-500 to-pink-500' },
    { value: 'safest', label: 'Safest', icon: Shield, color: 'from-green-500 to-emerald-500' },
    { value: 'energy_efficient', label: 'Eco-Friendly', icon: Leaf, color: 'from-blue-500 to-cyan-500' },
    { value: 'scenic', label: 'Scenic', icon: Mountain, color: 'from-yellow-500 to-orange-500' },
    { value: 'healthy', label: 'Healthy', icon: Heart, color: 'from-purple-500 to-violet-500' },
    { value: 'cheapest', label: 'Cheapest', icon: DollarSign, color: 'from-gray-500 to-slate-500' },
  ]


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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!origin.trim() || !destination.trim()) {
      return
    }

    // Mock coordinates for demo - in real app would geocode addresses
    const mockCoordinates = {
      'vancouver downtown': { lat: 49.2827, lng: -123.1207 },
      'vancouver airport': { lat: 49.1967, lng: -123.1815 },
      'stanley park': { lat: 49.3043, lng: -123.1443 },
      'ubc': { lat: 49.2606, lng: -123.2460 },
      'burnaby': { lat: 49.2488, lng: -122.9805 },
      'richmond': { lat: 49.1666, lng: -123.1336 }
    }

    const originLower = origin.toLowerCase()
    const destinationLower = destination.toLowerCase()

    const originPoint = mockCoordinates[originLower as keyof typeof mockCoordinates] || { lat: 49.2827, lng: -123.1207 }
    const destinationPoint = mockCoordinates[destinationLower as keyof typeof mockCoordinates] || { lat: 49.1967, lng: -123.1815 }

    const request = {
      origin: originPoint,
      destination: destinationPoint,
      preferences,
      transport_modes: transportModes,
      max_walking_distance: maxWalkingDistance,
      avoid_highways: false,
      accessibility_requirements: []
    }

    onSubmit(request)
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
          <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
            <MapPin className="w-4 h-4 mr-2 text-primary-600" />
            Origin
          </label>
          <input
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            placeholder="e.g., Vancouver Downtown, Stanley Park, UBC"
            className="input-field"
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
            <Navigation className="w-4 h-4 mr-2 text-primary-600" />
            Destination
          </label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="e.g., Vancouver Airport, Burnaby, Richmond"
            className="input-field"
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
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
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
                  "p-4 rounded-xl border-2 transition-all duration-300 relative overflow-hidden",
                  isSelected
                    ? 'border-primary-500/50 bg-primary-50/80 text-primary-700 shadow-lg'
                    : 'border-white/40 hover:border-white/60 text-gray-700 hover:bg-white/50'
                )}
              >
                <div className="text-center relative z-10">
                  <div className={cn(
                    "w-8 h-8 mx-auto mb-2 rounded-lg flex items-center justify-center text-white",
                    `bg-gradient-to-br ${option.color}`
                  )}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="text-xs font-medium">{option.label}</div>
                </div>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-2 right-2 w-4 h-4 bg-primary-500 rounded-full flex items-center justify-center"
                  >
                    <div className="w-2 h-2 bg-white rounded-full" />
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
            min="500"
            max="5000"
            step="500"
            value={maxWalkingDistance}
            onChange={(e) => setMaxWalkingDistance(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>500m</span>
            <span className="font-semibold text-primary-600">{maxWalkingDistance}m</span>
            <span>5000m</span>
          </div>
        </div>
      </motion.div>

      {/* Submit Button */}
      <motion.button
        type="submit"
        disabled={isLoading || !origin.trim() || !destination.trim()}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 1.0 }}
        whileHover={{ scale: isLoading ? 1 : 1.02 }}
        whileTap={{ scale: isLoading ? 1 : 0.98 }}
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {isLoading ? (
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
