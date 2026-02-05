import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, MapPin } from 'lucide-react'
import type { Point } from '../types'

interface Destination {
  id: string
  name: string
  address: string
  location: Point
  image: string
  description: string
}

interface PopularDestinationsProps {
  onSelectDestination: (destination: { location: Point; address: string; name: string }) => void
}

const DESTINATIONS: Destination[] = [
  {
    id: 'stanley-park',
    name: 'Stanley Park',
    address: 'Stanley Park, Vancouver, BC',
    location: { lat: 49.3044, lng: -123.1446 },
    image: '/images/Stanley-Park.png',
    description: 'Iconic urban park'
  },
  {
    id: 'granville-island',
    name: 'Granville Island',
    address: 'Granville Island, Vancouver, BC',
    location: { lat: 49.2719, lng: -123.1349 },
    image: '/images/Granville-Island.png',
    description: 'Public market'
  },
  {
    id: 'gastown',
    name: 'Gastown',
    address: 'Gastown, Vancouver, BC',
    location: { lat: 49.2839, lng: -123.1094 },
    image: '/images/Gastown.png',
    description: 'Historic district'
  },
  {
    id: 'canada-place',
    name: 'Canada Place',
    address: 'Canada Place, Vancouver, BC',
    location: { lat: 49.2889, lng: -123.1111 },
    image: '/images/Canada-Place.png',
    description: 'Waterfront landmark'
  },
  {
    id: 'science-world',
    name: 'Science World',
    address: '1455 Quebec St, Vancouver, BC',
    location: { lat: 49.2734, lng: -123.1036 },
    image: '/images/Science-World.png',
    description: 'Science museum'
  },
  {
    id: 'kits-beach',
    name: 'Kitsilano Beach',
    address: 'Kitsilano Beach, Vancouver, BC',
    location: { lat: 49.2747, lng: -123.1551 },
    image: '/images/Kits-Beach.png',
    description: 'Popular beach'
  },
  {
    id: 'ubc',
    name: 'UBC Campus',
    address: 'University of British Columbia, Vancouver, BC',
    location: { lat: 49.2606, lng: -123.2460 },
    image: '/images/UBC.png',
    description: 'University campus'
  },
  {
    id: 'yvr',
    name: 'YVR Airport',
    address: 'Vancouver International Airport, Richmond, BC',
    location: { lat: 49.1967, lng: -123.1815 },
    image: '/images/YVR.png',
    description: 'International airport'
  },
  {
    id: 'quayside-marina',
    name: 'Quayside Marina',
    address: 'Quayside Marina, New Westminster, BC',
    location: { lat: 49.2010, lng: -122.9110 },
    image: '/images/Quayside-Marina.png',
    description: 'Scenic waterfront'
  }
]

const PopularDestinations: React.FC<PopularDestinationsProps> = ({ onSelectDestination }) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [direction, setDirection] = useState(0)
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({})
  const [isPaused, setIsPaused] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-advance carousel every 5 seconds
  useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      setDirection(1)
      setCurrentIndex((prev) => (prev + 1) % DESTINATIONS.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [isPaused])

  const nextSlide = () => {
    setDirection(1)
    setCurrentIndex((prev) => (prev + 1) % DESTINATIONS.length)
  }

  const prevSlide = () => {
    setDirection(-1)
    setCurrentIndex((prev) => (prev - 1 + DESTINATIONS.length) % DESTINATIONS.length)
  }

  const handleImageError = (id: string) => {
    setImageErrors(prev => ({ ...prev, [id]: true }))
  }

  const getVisibleDestinations = () => {
    const visible = []
    for (let i = 0; i < 3; i++) {
      const index = (currentIndex + i) % DESTINATIONS.length
      visible.push(DESTINATIONS[index])
    }
    return visible
  }

  const visibleDestinations = getVisibleDestinations()

  return (
    <div
      className="glass-card-strong p-3 sm:p-4"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm sm:text-base font-semibold text-gray-900 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-primary-600" />
          Popular Destinations
        </h3>
        <div className="flex gap-1">
          <button
            onClick={prevSlide}
            className="p-1 rounded-full bg-white/80 hover:bg-white shadow-sm transition-colors"
            aria-label="Previous destination"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={nextSlide}
            className="p-1 rounded-full bg-white/80 hover:bg-white shadow-sm transition-colors"
            aria-label="Next destination"
          >
            <ChevronRight className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      <div className="relative overflow-hidden" ref={scrollRef}>
        <div className="flex gap-2 sm:gap-3">
          <AnimatePresence mode="popLayout" initial={false} custom={direction}>
            {visibleDestinations.map((destination) => (
              <motion.button
                key={destination.id}
                onClick={() => onSelectDestination(destination)}
                className="relative flex-1 min-w-0 overflow-hidden rounded-lg bg-white hover:shadow-md transition-shadow group"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative h-40 sm:h-48 overflow-hidden bg-gray-100">
                  {!imageErrors[destination.id] ? (
                    <img
                      src={destination.image}
                      alt={destination.name}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                      onError={() => handleImageError(destination.id)}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-accent-100">
                      <MapPin className="w-8 h-8 text-primary-600 opacity-50" />
                    </div>
                  )}

                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

                  <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-3">
                    <h4 className="font-semibold text-white text-sm sm:text-base drop-shadow-lg line-clamp-1">
                      {destination.name}
                    </h4>
                    <p className="text-xs sm:text-sm text-white/90 drop-shadow-md line-clamp-1">
                      {destination.description}
                    </p>
                  </div>
                </div>
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

export default PopularDestinations
