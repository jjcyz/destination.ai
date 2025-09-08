import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { Route } from '../contexts/RouteContext'

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface MapViewProps {
  routes: Route[]
  selectedRoute: Route | null
  lastRequest: {
    origin: { lat: number; lng: number } | null
    destination: { lat: number; lng: number } | null
    preferences: string[]
  } | null
}

const MapView: React.FC<MapViewProps> = ({ routes, selectedRoute, lastRequest }) => {
  const mapRef = useRef<L.Map>(null)
  const [isMapReady, setIsMapReady] = useState(false)
  const [mapError, setMapError] = useState<string | null>(null)

  // Vancouver center coordinates
  const vancouverCenter: [number, number] = [49.2827, -123.1207]

  // Enhanced color mapping for different route preferences
  const getRouteColor = (preference: string): string => {
    const colors: { [key: string]: string } = {
      fastest: '#ef4444',
      safest: '#22c55e',
      energy_efficient: '#3b82f6',
      scenic: '#f59e0b',
      healthy: '#10b981',
      cheapest: '#8b5cf6',
    }
    return colors[preference] || '#6b7280'
  }

  // Get route weight based on selection
  const getRouteWeight = (isSelected: boolean, preference: string): number => {
    if (isSelected) return 8
    return preference === 'fastest' ? 6 : 4
  }

  // Get route opacity based on selection
  const getRouteOpacity = (isSelected: boolean): number => {
    return isSelected ? 0.9 : 0.5
  }

  // Get mode icon
  const getModeIcon = (mode: string): string => {
    const icons: { [key: string]: string } = {
      walking: '🚶',
      biking: '🚴',
      scooter: '🛴',
      car: '🚗',
      bus: '🚌',
      skytrain: '🚇',
    }
    return icons[mode] || '🚶'
  }

  // Handle map ready state
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMapReady(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  // Fit map to show all routes
  useEffect(() => {
    if (mapRef.current && routes.length > 0 && isMapReady) {
      const bounds = L.latLngBounds([])

      // Add origin and destination
      if (lastRequest && lastRequest.origin && lastRequest.destination) {
        bounds.extend([lastRequest.origin.lat, lastRequest.origin.lng])
        bounds.extend([lastRequest.destination.lat, lastRequest.destination.lng])
      }

      // Add all route points
      routes.forEach(route => {
        route.steps.forEach(step => {
          bounds.extend([step.start_point.lat, step.start_point.lng])
          bounds.extend([step.end_point.lat, step.end_point.lng])
        })
      })

      // Use setTimeout to ensure map is fully rendered
      setTimeout(() => {
        if (mapRef.current) {
      mapRef.current.fitBounds(bounds, { padding: [20, 20] })
        }
      }, 100)
    }
  }, [routes, lastRequest, isMapReady])

  // Show loading state
  if (!isMapReady) {
    return (
      <div style={{ height: '100%', width: '100%', minHeight: '300px' }} className="flex items-center justify-center bg-gray-100 rounded-xl">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (mapError) {
    return (
      <div style={{ height: '100%', width: '100%', minHeight: '300px' }} className="flex items-center justify-center bg-red-50 rounded-xl">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-4">🗺️</div>
          <p className="text-red-600 font-medium">Map failed to load</p>
          <p className="text-red-500 text-sm mt-2">{mapError}</p>
          <button
            onClick={() => {
              setMapError(null)
              setIsMapReady(false)
            }}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ height: '100%', width: '100%', minHeight: '300px' }}>
      <MapContainer
        center={vancouverCenter}
        zoom={12}
        style={{ height: '100%', width: '100%', minHeight: '300px' }}
        ref={mapRef}
        whenReady={() => setIsMapReady(true)}
        zoomControl={true}
        scrollWheelZoom={true}
        doubleClickZoom={true}
        touchZoom={true}
        dragging={true}
      >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Origin and Destination Markers */}
      {lastRequest && lastRequest.origin && lastRequest.destination && (
        <>
          <Marker position={[lastRequest.origin.lat, lastRequest.origin.lng]}>
            <Popup>
              <div className="text-center">
                <div className="text-lg mb-1">📍</div>
                <div className="font-semibold">Origin</div>
              </div>
            </Popup>
          </Marker>
          <Marker position={[lastRequest.destination.lat, lastRequest.destination.lng]}>
            <Popup>
              <div className="text-center">
                <div className="text-lg mb-1">🎯</div>
                <div className="font-semibold">Destination</div>
              </div>
            </Popup>
          </Marker>
        </>
      )}

      {/* Route Lines */}
      {routes.map((route) => {
        const isSelected = selectedRoute?.id === route.id
        const opacity = getRouteOpacity(isSelected)
        const weight = getRouteWeight(isSelected, route.preference)

        return (
          <React.Fragment key={route.id}>
            {route.steps.map((step, stepIndex) => {
              const positions: [number, number][] = [
                [step.start_point.lat, step.start_point.lng],
                [step.end_point.lat, step.end_point.lng]
              ]

              return (
                <Polyline
                  key={`${route.id}-${stepIndex}`}
                  positions={positions}
                  color={getRouteColor(route.preference)}
                  weight={weight}
                  opacity={opacity}
                  dashArray={step.mode === 'walking' ? '8, 8' : step.mode === 'biking' ? '4, 4' : undefined}
                  lineCap="round"
                  lineJoin="round"
                />
              )
            })}

            {/* Mode change markers */}
            {route.steps.map((step, stepIndex) => {
              if (stepIndex === 0) return null // Skip first step

              const prevStep = route.steps[stepIndex - 1]
              if (prevStep.mode !== step.mode) {
                return (
                  <Marker
                    key={`mode-change-${route.id}-${stepIndex}`}
                    position={[step.start_point.lat, step.start_point.lng]}
                  >
                    <Popup>
                      <div className="text-center">
                        <div className="text-lg mb-1">
                          {getModeIcon(prevStep.mode)} → {getModeIcon(step.mode)}
                        </div>
                        <div className="text-sm">
                          Switch to {step.mode}
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                )
              }
              return null
            })}
          </React.Fragment>
        )
      })}

      {/* Enhanced Legend - Only show if there are routes */}
      {routes.length > 0 && (
      <div className="absolute top-4 right-4 glass-card-strong p-4 z-[1000] max-w-xs">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
          <div className="w-2 h-2 bg-primary-500 rounded-full mr-2" />
          Route Types
        </h3>
        <div className="space-y-2">
          {routes.map((route) => (
            <div key={route.id} className="flex items-center space-x-3">
              <div
                className="w-5 h-1.5 rounded-full"
                style={{ backgroundColor: getRouteColor(route.preference) }}
              />
              <span className="text-sm text-gray-700 capitalize flex-1">
                {route.preference.replace('_', ' ')}
              </span>
              {selectedRoute?.id === route.id && (
                <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-medium">
                  Selected
                </span>
              )}
            </div>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t border-white/30">
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-0.5 bg-gray-400 rounded" style={{ borderStyle: 'dashed' }} />
              <span>Walking</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-0.5 bg-gray-400 rounded" />
              <span>Other modes</span>
            </div>
          </div>
        </div>
      </div>
      )}

      {/* No routes message */}
      {routes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center z-[1000]">
          <div className="glass-card-strong p-6 text-center max-w-sm mx-4">
            <div className="text-4xl mb-4">🗺️</div>
            <h3 className="font-semibold text-gray-900 mb-2">Vancouver Map</h3>
            <p className="text-gray-600 text-sm">
              Plan a route above to see it displayed on the map
            </p>
          </div>
        </div>
      )}
      </MapContainer>
    </div>
  )
}

export default MapView
