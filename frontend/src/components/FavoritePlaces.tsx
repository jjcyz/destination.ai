import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Clock, Navigation, Loader2, Plus } from 'lucide-react'
import { routeAPI } from '../services/api'
import type { Point, RouteRequest } from '../types'
import { DEFAULT_PREFERENCES, DEFAULT_TRANSPORT_MODES, WALKING_DISTANCE_CONFIG } from '../config'

interface FavoritePlace {
  id: string
  name: string
  address: string
  location: Point
}

interface FavoritePlacesProps {
  onSelectPlace: (place: FavoritePlace) => void
  currentOrigin?: Point
}

const FavoritePlaces: React.FC<FavoritePlacesProps> = ({ onSelectPlace, currentOrigin }) => {
  const [favorites, setFavorites] = useState<FavoritePlace[]>([])
  const [routeTimes, setRouteTimes] = useState<Record<string, { time: number; distance: number; loading: boolean }>>({})

  // Initialize with default favorites
  useEffect(() => {
    const defaultFavorites: FavoritePlace[] = [
      {
        id: 'home',
        name: 'Home',
        address: 'Vancouver, BC',
        location: { lat: 49.2827, lng: -123.1207 }
      },
      {
        id: 'school',
        name: 'School',
        address: 'UBC Campus, Vancouver',
        location: { lat: 49.2606, lng: -123.2460 }
      },
      {
        id: 'work',
        name: 'Work',
        address: 'Downtown Vancouver',
        location: { lat: 49.2819, lng: -123.1187 }
      }
    ]

    const saved = localStorage.getItem('favoritePlaces')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setFavorites(parsed.map((p: any) => ({
          ...p,
          location: p.location || defaultFavorites.find(d => d.id === p.id)?.location || { lat: 49.2827, lng: -123.1207 }
        })))
      } catch {
        setFavorites(defaultFavorites)
      }
    } else {
      setFavorites(defaultFavorites)
    }
  }, [])

  // Calculate route times when origin changes
  useEffect(() => {
    if (!currentOrigin || favorites.length === 0) return

    const calculateRouteTimes = async () => {
      const times: Record<string, { time: number; distance: number; loading: boolean }> = {}
      favorites.forEach(fav => {
        times[fav.id] = { time: 0, distance: 0, loading: true }
      })
      setRouteTimes(times)

      for (const favorite of favorites) {
        try {
          const request: RouteRequest = {
            origin: currentOrigin,
            destination: favorite.location,
            preferences: [...DEFAULT_PREFERENCES],
            transport_modes: [...DEFAULT_TRANSPORT_MODES],
            max_walking_distance: WALKING_DISTANCE_CONFIG.DEFAULT,
            avoid_highways: false,
            accessibility_requirements: []
          }

          const response = await routeAPI.calculateRoute(request)
          if (response.routes.length > 0) {
            const fastestRoute = response.routes[0]
            times[favorite.id] = {
              time: fastestRoute.total_time,
              distance: fastestRoute.total_distance,
              loading: false
            }
          } else {
            times[favorite.id] = { time: 0, distance: 0, loading: false }
          }
        } catch (error) {
          console.warn(`Failed to calculate route to ${favorite.name}:`, error)
          times[favorite.id] = { time: 0, distance: 0, loading: false }
        }
      }

      setRouteTimes({ ...times })
    }

    calculateRouteTimes()
  }, [currentOrigin, favorites])

  const formatTime = (seconds: number): string => {
    if (seconds === 0) return '--'
    const minutes = Math.round(seconds / 60)
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  const formatDistance = (meters: number): string => {
    if (meters === 0) return '--'
    if (meters < 1000) return `${Math.round(meters)}m`
    return `${(meters / 1000).toFixed(1)}km`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card-strong p-4 sm:p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Favorite Places
        </h3>
        <button
          className="p-1.5 rounded-lg hover:bg-white/60 transition-colors touch-manipulation"
          aria-label="Add favorite place"
        >
          <Plus className="w-4 h-4 text-gray-600" />
        </button>
      </div>

      <div className="space-y-2">
        {favorites.map((place) => {
          const routeInfo = routeTimes[place.id] || { time: 0, distance: 0, loading: false }

          return (
            <button
              key={place.id}
              onClick={() => onSelectPlace(place)}
              className="w-full p-3 rounded-lg hover:bg-white/60 transition-colors text-left touch-manipulation"
            >
              <div className="flex items-center justify-between mb-1">
                <h4 className="font-semibold text-gray-900 text-sm">
                  {place.name}
                </h4>
                {routeInfo.loading ? (
                  <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
                ) : (
                  <div className="flex items-center gap-3 text-xs text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTime(routeInfo.time)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Navigation className="w-3 h-3" />
                      {formatDistance(routeInfo.distance)}
                    </span>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-600 line-clamp-1">
                {place.address}
              </p>
            </button>
          )
        })}
      </div>
    </motion.div>
  )
}

export default FavoritePlaces
