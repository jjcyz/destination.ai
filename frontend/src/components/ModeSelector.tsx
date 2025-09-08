import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'

interface ModeSelectorProps {
  selectedModes: string[]
  onModeChange: (modes: string[]) => void
  className?: string
}

const transportModeOptions = [
  {
    value: 'walking',
    label: 'Walking',
    icon: '🚶',
    color: 'from-blue-500 to-blue-600',
    description: 'Best for short distances'
  },
  {
    value: 'biking',
    label: 'Biking',
    icon: '🚴',
    color: 'from-green-500 to-green-600',
    description: 'Eco-friendly and healthy'
  },
  {
    value: 'scooter',
    label: 'Scooter',
    icon: '🛴',
    color: 'from-yellow-500 to-orange-500',
    description: 'Quick and convenient'
  },
  {
    value: 'car',
    label: 'Car',
    icon: '🚗',
    color: 'from-red-500 to-red-600',
    description: 'Fastest for long distances'
  },
  {
    value: 'bus',
    label: 'Bus',
    icon: '🚌',
    color: 'from-purple-500 to-purple-600',
    description: 'Public transit option'
  },
  {
    value: 'skytrain',
    label: 'SkyTrain',
    icon: '🚇',
    color: 'from-indigo-500 to-indigo-600',
    description: 'Rapid transit system'
  },
]

const ModeSelector: React.FC<ModeSelectorProps> = ({
  selectedModes,
  onModeChange,
  className
}) => {
  const handleModeToggle = (mode: string) => {
    const newModes = selectedModes.includes(mode)
      ? selectedModes.filter(m => m !== mode)
      : [...selectedModes, mode]

    onModeChange(newModes)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn("space-y-4", className)}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Transport Modes</h3>
        <div className="text-sm text-gray-500">
          {selectedModes.length} selected
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {transportModeOptions.map((mode, index) => {
          const isSelected = selectedModes.includes(mode.value)

          return (
            <motion.button
              key={mode.value}
              type="button"
              onClick={() => handleModeToggle(mode.value)}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 0.3,
                delay: index * 0.1,
                type: "spring",
                stiffness: 200
              }}
              whileHover={{
                scale: 1.05,
                transition: { duration: 0.2 }
              }}
              whileTap={{
                scale: 0.95,
                transition: { duration: 0.1 }
              }}
              className={cn(
                "relative p-4 rounded-2xl border-2 transition-all duration-300 group",
                "min-h-[80px] flex flex-col items-center justify-center",
                isSelected
                  ? 'border-primary-500/50 bg-primary-50/80 text-primary-700 shadow-lg'
                  : 'border-white/40 hover:border-white/60 text-gray-700 hover:bg-white/50'
              )}
            >
              {/* Background gradient effect */}
              <div className={cn(
                "absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300",
                `bg-gradient-to-br ${mode.color}`,
                isSelected ? "opacity-10" : "group-hover:opacity-5"
              )} />

              {/* Content */}
              <div className="relative z-10 text-center">
                <motion.div
                  className="text-2xl mb-2"
                  animate={isSelected ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 0.3 }}
                >
                  {mode.icon}
                </motion.div>
                <div className="text-sm font-medium leading-tight">
                  {mode.label}
                </div>
              </div>

              {/* Selection indicator */}
              <AnimatePresence>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-2 right-2 w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center shadow-lg"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.1, duration: 0.2 }}
                      className="w-2 h-2 bg-white rounded-full"
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Hover tooltip */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileHover={{ opacity: 1, y: 0 }}
                className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded-lg opacity-0 pointer-events-none whitespace-nowrap z-20"
              >
                {mode.description}
                <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45" />
              </motion.div>
            </motion.button>
          )
        })}
      </div>

      {/* Quick select buttons */}
      <div className="flex flex-wrap gap-2 pt-2">
        <motion.button
          type="button"
          onClick={() => onModeChange(['walking', 'biking'])}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-3 py-1.5 text-xs font-medium bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
        >
          Eco-Friendly
        </motion.button>
        <motion.button
          type="button"
          onClick={() => onModeChange(['car'])}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-3 py-1.5 text-xs font-medium bg-red-100 text-red-700 rounded-full hover:bg-red-200 transition-colors"
        >
          Fastest
        </motion.button>
        <motion.button
          type="button"
          onClick={() => onModeChange(['bus', 'skytrain'])}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-3 py-1.5 text-xs font-medium bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
        >
          Public Transit
        </motion.button>
        <motion.button
          type="button"
          onClick={() => onModeChange(transportModeOptions.map(m => m.value))}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-3 py-1.5 text-xs font-medium bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
        >
          All Modes
        </motion.button>
      </div>
    </motion.div>
  )
}

export default ModeSelector
