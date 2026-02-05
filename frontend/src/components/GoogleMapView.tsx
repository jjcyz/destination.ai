import React, { useEffect, useRef, useState, useCallback } from 'react'
import { GoogleMap, Polyline, Marker, InfoWindow } from '@react-google-maps/api'
import type { Route } from '../types'
import { useGoogleMaps } from '../contexts/GoogleMapsContext'
import { getRouteColorHex } from '../utils/routePreferences'

interface GoogleMapViewProps {
  routes: Route[]
  selectedRoute: Route | null
  lastRequest: {
    origin: { lat: number; lng: number } | null
    destination: { lat: number; lng: number } | null
    preferences: string[]
  } | null
  apiKey: string
}

const GoogleMapView: React.FC<GoogleMapViewProps> = ({
  routes,
  selectedRoute,
  lastRequest,
  apiKey
}) => {
  const { isLoaded: isGoogleMapsLoaded, loadError } = useGoogleMaps()
  const mapRef = useRef<google.maps.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [selectedInfoWindow, setSelectedInfoWindow] = useState<number | null>(null)

  const containerStyle = {
    width: '100%',
    height: '100%',
    minHeight: '200px'
  }

  // Vancouver center coordinates
  const vancouverCenter = { lat: 49.2827, lng: -123.1207 }


  // Decode Google Maps polyline
  const decodePolyline = (encoded: string): google.maps.LatLng[] => {
    if (!encoded || encoded.length === 0) {
      return []
    }

    try {
      const poly: google.maps.LatLng[] = []
      let index = 0
      const len = encoded.length
      let lat = 0
      let lng = 0

      while (index < len) {
        let b: number
        let shift = 0
        let result = 0
        do {
          if (index >= len) break
          b = encoded.charCodeAt(index++) - 63
          result |= (b & 0x1f) << shift
          shift += 5
        } while (b >= 0x20)
        const dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
        lat += dlat

        shift = 0
        result = 0
        do {
          if (index >= len) break
          b = encoded.charCodeAt(index++) - 63
          result |= (b & 0x1f) << shift
          shift += 5
        } while (b >= 0x20)
        const dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1))
        lng += dlng

        poly.push(new google.maps.LatLng(lat * 1e-5, lng * 1e-5))
      }

      return poly
    } catch (error) {
      console.error('Error decoding polyline:', error)
      return []
    }
  }

  // Fit map to show all routes
  const fitBounds = useCallback(() => {
    if (!mapRef.current || routes.length === 0) return

    try {
      const bounds = new google.maps.LatLngBounds()
      let hasBounds = false

      // Add origin and destination
      if (lastRequest?.origin) {
        bounds.extend(new google.maps.LatLng(lastRequest.origin.lat, lastRequest.origin.lng))
        hasBounds = true
      }
      if (lastRequest?.destination) {
        bounds.extend(new google.maps.LatLng(lastRequest.destination.lat, lastRequest.destination.lng))
        hasBounds = true
      }

      // Add all route points
      routes.forEach((route: Route) => {
        route.steps.forEach((step) => {
          if (step.polyline) {
            // Decode polyline and add all points
            const decoded = decodePolyline(step.polyline)
            if (decoded.length > 0) {
              decoded.forEach(point => bounds.extend(point))
              hasBounds = true
            }
          }

          // Always add start/end points as fallback
          bounds.extend(new google.maps.LatLng(step.start_point.lat, step.start_point.lng))
          bounds.extend(new google.maps.LatLng(step.end_point.lat, step.end_point.lng))
          hasBounds = true
        })
      })

      if (hasBounds) {
        mapRef.current.fitBounds(bounds, 50)
      }
    } catch (error) {
      console.error('Error fitting bounds:', error)
    }
  }, [routes, lastRequest])

  useEffect(() => {
    if (mapLoaded && routes.length > 0) {
      const timeoutId = setTimeout(fitBounds, 100)
      // Cleanup: clear timeout if component unmounts or dependencies change
      return () => {
        clearTimeout(timeoutId)
      }
    }
  }, [mapLoaded, routes, fitBounds])

  const onLoad = useCallback((map: google.maps.Map) => {
    mapRef.current = map
    setMapLoaded(true)
  }, [])

  const onUnmount = useCallback(() => {
    // Cleanup: clear map reference and reset state
    if (mapRef.current) {
      // Clear any event listeners or custom overlays if needed
      mapRef.current = null
    }
    setMapLoaded(false)
    setSelectedInfoWindow(null)
  }, [])

  // Cleanup effect: ensure proper cleanup on component unmount
  useEffect(() => {
    return () => {
      // Cleanup on component unmount
      if (mapRef.current) {
        mapRef.current = null
      }
      setMapLoaded(false)
      setSelectedInfoWindow(null)
    }
  }, [])

  // Show error if Google Maps failed to load
  if (loadError) {
    return (
      <div style={containerStyle} className="flex items-center justify-center bg-gray-100 rounded-xl">
        <div className="text-center">
          <p className="text-red-600 font-medium">Failed to load Google Maps</p>
          <p className="text-gray-500 text-sm mt-2">{loadError.message}</p>
        </div>
      </div>
    )
  }

  // Show loading state while Google Maps is loading
  if (!isGoogleMapsLoaded) {
    return (
      <div style={containerStyle} className="flex items-center justify-center bg-gray-100 rounded-xl">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" />
          <p className="text-gray-600">Loading Google Maps...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full">
      {/* API Key Error Message */}
      {!apiKey && (
        <div className="absolute top-4 left-4 z-[1001] bg-red-50 border border-red-200 rounded-lg p-3 shadow-md max-w-sm">
          <p className="text-red-600 font-semibold text-sm">⚠️ Google Maps API key not configured</p>
          <p className="text-red-700 text-xs mt-1">Add VITE_GOOGLE_MAPS_API_KEY to .env</p>
        </div>
      )}

      <GoogleMap
        mapContainerStyle={containerStyle}
        center={vancouverCenter}
        zoom={12}
        onLoad={onLoad}
        onUnmount={onUnmount}
        options={{
          zoomControl: true,
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: true,
          disableDefaultUI: false,
        }}
      >
        {/* Origin Marker */}
        {lastRequest?.origin && (
          <Marker
            position={{ lat: lastRequest.origin.lat, lng: lastRequest.origin.lng }}
            icon={{
              url: 'data:image/svg+xml;base64,' + btoa(`
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="#22c55e">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
              `),
              scaledSize: new google.maps.Size(32, 32),
              anchor: new google.maps.Point(16, 32),
            }}
            onClick={() => setSelectedInfoWindow(selectedInfoWindow === 0 ? null : 0)}
          >
            {selectedInfoWindow === 0 && (
              <InfoWindow onCloseClick={() => setSelectedInfoWindow(null)}>
                <div className="text-center">
                  <div className="text-lg mb-1">📍</div>
                  <div className="font-semibold">Origin</div>
                </div>
              </InfoWindow>
            )}
          </Marker>
        )}

        {/* Destination Marker */}
        {lastRequest?.destination && (
          <Marker
            position={{ lat: lastRequest.destination.lat, lng: lastRequest.destination.lng }}
            icon={{
              url: 'data:image/svg+xml;base64,' + btoa(`
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="#ef4444">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
              `),
              scaledSize: new google.maps.Size(32, 32),
              anchor: new google.maps.Point(16, 32),
            }}
            onClick={() => setSelectedInfoWindow(selectedInfoWindow === 1 ? null : 1)}
          >
            {selectedInfoWindow === 1 && (
              <InfoWindow onCloseClick={() => setSelectedInfoWindow(null)}>
                <div className="text-center">
                  <div className="text-lg mb-1">🎯</div>
                  <div className="font-semibold">Destination</div>
                </div>
              </InfoWindow>
            )}
          </Marker>
        )}

        {/* Route Polylines */}
        {routes.map((route: Route) => {
          const isSelected = selectedRoute?.id === route.id
          const routeColor = getRouteColorHex(route.preference as string)
          const opacity = isSelected ? 0.9 : 0.5
          const weight = isSelected ? 8 : 4

          return (
            <React.Fragment key={route.id}>
              {route.steps.map((step, stepIndex: number) => {
                let path: google.maps.LatLng[] = []

                if (step.polyline) {
                  // Use decoded polyline for accurate route rendering
                  path = decodePolyline(step.polyline)
                }

                // Fallback to start/end points if no polyline or decoding failed
                if (path.length === 0) {
                  path = [
                    new google.maps.LatLng(step.start_point.lat, step.start_point.lng),
                    new google.maps.LatLng(step.end_point.lat, step.end_point.lng)
                  ]
                }

                // Skip if path is still empty
                if (path.length === 0) {
                  return null
                }

                // Determine line style based on mode
                const isWalking = step.mode === 'walking'
                const isBiking = step.mode === 'biking'
                const strokeOpacity = opacity
                const strokeWeight = weight

                return (
                  <Polyline
                    key={`${route.id}-${stepIndex}`}
                    path={path}
                    options={{
                      strokeColor: routeColor,
                      strokeOpacity,
                      strokeWeight,
                      geodesic: true,
                      icons: isWalking ? [
                        {
                          icon: {
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 3,
                            strokeColor: routeColor,
                            strokeWeight: 2,
                          },
                          offset: '0%',
                          repeat: '20px',
                        },
                      ] : isBiking ? [
                        {
                          icon: {
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 2,
                            strokeColor: routeColor,
                            strokeWeight: 1,
                          },
                          offset: '0%',
                          repeat: '15px',
                        },
                      ] : undefined,
                    }}
                  />
                )
              })}
            </React.Fragment>
          )
        })}

        {/* Legend */}
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
                    style={{ backgroundColor: getRouteColorHex(route.preference as string) }}
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
          </div>
        )}

        {/* No routes message */}
        {routes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center z-[1000] pointer-events-none">
            <div className="glass-card-strong p-6 text-center max-w-sm mx-4">
              <div className="text-4xl mb-4">🗺️</div>
              <h3 className="font-semibold text-gray-900 mb-2">Vancouver Map</h3>
              <p className="text-gray-600 text-sm">
                Plan a route above to see it displayed on the map
              </p>
            </div>
          </div>
        )}
      </GoogleMap>
    </div>
  )
}

export default GoogleMapView

