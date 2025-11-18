import React, { useState, useRef, useEffect, useMemo } from 'react'
import { MapPin, ChevronDown, X, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'
import { useGoogleMaps } from '../contexts/GoogleMapsContext'

interface AddressAutocompleteProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label: string
  icon?: React.ReactNode
  error?: string | null
  required?: boolean
}

const AddressAutocomplete: React.FC<AddressAutocompleteProps> = ({
  value,
  onChange,
  placeholder = 'Select or type an address...',
  label,
  icon,
  error,
  required = false,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [highlightedIndex, setHighlightedIndex] = useState(0)
  const [googlePlacesResults, setGooglePlacesResults] = useState<google.maps.places.AutocompletePrediction[]>([])
  const [isLoadingPlaces, setIsLoadingPlaces] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const autocompleteServiceRef = useRef<google.maps.places.AutocompleteService | null>(null)
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Use shared Google Maps context (loaded once at app level)
  const { isLoaded: isGoogleMapsLoaded } = useGoogleMaps()
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

  // Initialize Google Places Autocomplete Service when loaded
  useEffect(() => {
    if (isGoogleMapsLoaded && window.google?.maps?.places) {
      autocompleteServiceRef.current = new google.maps.places.AutocompleteService()
    } else if (isGoogleMapsLoaded && !window.google?.maps?.places) {
      // Diagnostic: Places library not loaded
      console.error('Google Places library not loaded. Make sure Places API is enabled in Google Cloud Console.')
    } else if (!apiKey) {
      console.warn('Google Maps API key not found. Add VITE_GOOGLE_MAPS_API_KEY to your .env file.')
    }
  }, [isGoogleMapsLoaded, apiKey])

  // Fetch Google Places suggestions
  useEffect(() => {
    // Clear previous timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    if (!searchQuery.trim()) {
      setGooglePlacesResults([])
      setIsLoadingPlaces(false)
      return
    }

    // Don't call Google Places if API is not loaded or service not available
    if (!isGoogleMapsLoaded || !autocompleteServiceRef.current) {
      setGooglePlacesResults([])
      setIsLoadingPlaces(false)
      return
    }

    setIsLoadingPlaces(true)

    // Debounce Google Places API calls
    debounceTimerRef.current = setTimeout(() => {
      const request: google.maps.places.AutocompletionRequest = {
        input: searchQuery,
        types: ['geocode'], // Includes addresses and establishments
        location: new google.maps.LatLng(49.2827, -123.1207), // Vancouver center
        radius: 50000, // 50km radius around Vancouver
        componentRestrictions: { country: 'ca' }, // Restrict to Canada
      }

      try {
        autocompleteServiceRef.current?.getPlacePredictions(
          request,
          (results, status) => {
            setIsLoadingPlaces(false)

            if (status === google.maps.places.PlacesServiceStatus.OK && results) {
              // Limit to 10 Google Places results
              setGooglePlacesResults(results.slice(0, 10))
            } else {
              // Handle different error statuses
              if (status === google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
                if (import.meta.env.DEV) {
                  console.log(`Google Places API: No results found for "${searchQuery}"`)
                }
                setGooglePlacesResults([])
              } else if (status === google.maps.places.PlacesServiceStatus.OVER_QUERY_LIMIT) {
                console.warn('Google Places API: Over query limit')
                setGooglePlacesResults([])
              } else if (status === google.maps.places.PlacesServiceStatus.REQUEST_DENIED) {
                console.error('Google Places API: Request denied')
                setGooglePlacesResults([])
              } else if (status === google.maps.places.PlacesServiceStatus.INVALID_REQUEST) {
                console.warn(`Google Places API: Invalid request for "${searchQuery}"`)
                setGooglePlacesResults([])
              } else {
                console.warn(`Google Places API error: ${status} for query "${searchQuery}"`)
                setGooglePlacesResults([])
              }
            }
          }
        )
      } catch (error) {
        // Handle any synchronous errors
        console.error('Error calling Google Places API:', error)
        setIsLoadingPlaces(false)
        setGooglePlacesResults([])
      }
    }, 300) // 300ms debounce

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [searchQuery, isGoogleMapsLoaded])

  // Convert Google Places results to display format
  const allResults = useMemo(() => {
    return googlePlacesResults.map(result => ({
      type: 'google' as const,
      label: result.structured_formatting.main_text,
      value: result.description,
      description: result.structured_formatting.secondary_text,
      placeId: result.place_id,
    }))
  }, [googlePlacesResults])

  const filteredAddresses = allResults

  // Reset highlighted index when filtered results change
  useEffect(() => {
    setHighlightedIndex(0)
  }, [filteredAddresses.length, searchQuery])

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
        setSearchQuery('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && (e.key === 'ArrowDown' || e.key === 'Enter')) {
      setIsOpen(true)
      return
    }

    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setHighlightedIndex((prev) =>
          prev < filteredAddresses.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : 0))
        break
      case 'Enter':
        e.preventDefault()
        if (filteredAddresses[highlightedIndex]) {
          handleSelect(filteredAddresses[highlightedIndex])
        } else if (filteredAddresses.length === 0 && searchQuery.trim()) {
          // Allow submitting the typed value if no results
          onChange(searchQuery)
          setIsOpen(false)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSearchQuery('')
        inputRef.current?.blur()
        break
    }
  }

  const handleSelect = (result: typeof allResults[0]) => {
    onChange(result.value)
    setIsOpen(false)
    setSearchQuery('')
    inputRef.current?.blur()
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setSearchQuery(newValue)
    onChange(newValue)
    setIsOpen(true)
  }

  const handleInputFocus = () => {
    setIsOpen(true)
    if (value && !searchQuery) {
      setSearchQuery(value)
    }
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange('')
    setSearchQuery('')
    inputRef.current?.focus()
  }


  const displayValue = value || searchQuery

  return (
    <div ref={containerRef} className="relative">
      <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
        {icon || <MapPin className="w-4 h-4 mr-2 text-primary-600" />}
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={displayValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'input-field pr-10',
            error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
            isOpen && 'rounded-b-none'
          )}
          required={required}
          autoComplete="off"
        />

        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
          {value && (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              tabIndex={-1}
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <ChevronDown
            className={cn(
              'w-4 h-4 text-gray-400 transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </div>
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && searchQuery && (filteredAddresses.length > 0 || isLoadingPlaces || (!isLoadingPlaces && filteredAddresses.length === 0)) && (
          <motion.div
            ref={dropdownRef}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute z-50 w-full mt-0 glass-card-strong border-t-0 rounded-b-xl shadow-lg max-h-64 overflow-y-auto"
          >
            <div className="p-2">
              {/* Google Places results */}
              {isLoadingPlaces && (
                <div className="px-4 py-3 flex items-center justify-center text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  <span className="text-sm">Searching...</span>
                </div>
              )}

              {googlePlacesResults.map((result, index) => (
                <motion.button
                  key={`google-${result.place_id}-${index}`}
                  type="button"
                  onClick={() => handleSelect({
                    type: 'google',
                    label: result.structured_formatting.main_text,
                    value: result.description,
                    description: result.structured_formatting.secondary_text,
                    placeId: result.place_id,
                  })}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={cn(
                    'w-full text-left px-4 py-3 rounded-lg transition-colors flex items-center space-x-3',
                    highlightedIndex === index
                      ? 'bg-primary-50 text-primary-900'
                      : 'hover:bg-white/60 text-gray-700'
                  )}
                >
                  <span className="text-lg">📍</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{result.structured_formatting.main_text}</div>
                    {result.structured_formatting.secondary_text && (
                      <div className="text-xs text-gray-500 truncate">
                        {result.structured_formatting.secondary_text}
                      </div>
                    )}
                  </div>
                </motion.button>
              ))}

              {/* No results message */}
              {!isLoadingPlaces && filteredAddresses.length === 0 && searchQuery && (
                <div className="text-center text-sm text-gray-600 p-4">
                  <p className="mb-2">No addresses found for "{searchQuery}"</p>
                  <p className="text-xs text-gray-500 mb-2">
                    {isGoogleMapsLoaded
                      ? 'Try a different address or check your spelling.'
                      : 'Please wait for Google Maps to load or try a different search term.'}
                  </p>
                  {import.meta.env.DEV && (
                    <div className="text-xs text-gray-400 mt-2 pt-2 border-t border-white/20">
                      <p>Debug: Google Maps loaded: {isGoogleMapsLoaded ? 'Yes' : 'No'}</p>
                      <p>Places service available: {autocompleteServiceRef.current ? 'Yes' : 'No'}</p>
                      <p>API Key present: {apiKey ? 'Yes' : 'No'}</p>
                      <p>Search query: "{searchQuery}"</p>
                      <p>Google Places results: {googlePlacesResults.length}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-sm text-red-600 flex items-center space-x-1"
        >
          <span>⚠️</span>
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  )
}

export default AddressAutocomplete

