import { createContext, useContext, ReactNode } from 'react'
import { useLoadScript } from '@react-google-maps/api'

interface GoogleMapsContextType {
  isLoaded: boolean
  loadError: Error | undefined
}

const GoogleMapsContext = createContext<GoogleMapsContextType | undefined>(undefined)

// Static libraries array to prevent LoadScript reload warnings
// Must be defined outside component to maintain reference stability
const GOOGLE_MAPS_LIBRARIES: ('places' | 'drawing' | 'geometry' | 'visualization')[] = ['places', 'geometry']

interface GoogleMapsProviderProps {
  children: ReactNode
}

export function GoogleMapsProvider({ children }: GoogleMapsProviderProps) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: apiKey,
    libraries: GOOGLE_MAPS_LIBRARIES,
    version: 'weekly',
  })

  return (
    <GoogleMapsContext.Provider value={{ isLoaded, loadError }}>
      {children}
    </GoogleMapsContext.Provider>
  )
}

export function useGoogleMaps() {
  const context = useContext(GoogleMapsContext)
  if (context === undefined) {
    throw new Error('useGoogleMaps must be used within a GoogleMapsProvider')
  }
  return context
}

