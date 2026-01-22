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
  {
    value: 'rideshare',
    label: 'Ride-Share',
    icon: '🚕',
    color: 'from-pink-500 to-rose-600',
    description: 'Uber, Lyft, and similar services'
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

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 gap-2">
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
                delay: index * 0.05,
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
                "relative p-2 sm:p-3 rounded-xl border-2 transition-all duration-300 group",
                "min-h-[60px] sm:min-h-[70px] flex flex-col items-center justify-center",
                isSelected
                  ? 'border-primary-500/50 bg-primary-50/80 text-primary-700 shadow-lg'
                  : 'border-white/40 hover:border-white/60 text-gray-700 hover:bg-white/50'
              )}
            >
              {/* Background gradient effect */}
              <div className={cn(
                "absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300",
                `bg-gradient-to-br ${mode.color}`,
                isSelected ? "opacity-10" : "group-hover:opacity-5"
              )} />

              {/* Content */}
              <div className="relative z-10 text-center">
                <motion.div
                  className="text-lg sm:text-xl mb-1"
                  animate={isSelected ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 0.3 }}
                >
                  {mode.icon}
                </motion.div>
                <div className="text-xs sm:text-sm font-medium leading-tight">
                  {mode.label}
                </div>
              </div>


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
    </motion.div>
  )
}

export default ModeSelector
