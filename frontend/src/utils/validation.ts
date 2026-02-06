/**
 * Input validation and sanitization utilities
 */

/**
 * Sanitize text input by removing potentially harmful characters
 */
export const sanitizeInput = (input: string): string => {
  if (!input) return ''

  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .slice(0, 500) // Limit length
}

/**
 * Validate address input
 */
export const validateAddress = (address: string): { isValid: boolean; error?: string } => {
  if (!address || !address.trim()) {
    return { isValid: false, error: 'Address is required' }
  }

  const sanitized = sanitizeInput(address)

  if (sanitized.length < 3) {
    return { isValid: false, error: 'Address must be at least 3 characters' }
  }

  if (sanitized.length > 500) {
    return { isValid: false, error: 'Address is too long' }
  }

  // Check for suspicious patterns
  const suspiciousPatterns = [
    /script/i,
    /javascript/i,
    /<iframe/i,
    /onerror/i,
    /onload/i
  ]

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(address)) {
      return { isValid: false, error: 'Invalid characters in address' }
    }
  }

  return { isValid: true }
}

/**
 * Validate coordinates
 */
export const validateCoordinates = (
  lat: number,
  lng: number
): { isValid: boolean; error?: string } => {
  if (typeof lat !== 'number' || typeof lng !== 'number') {
    return { isValid: false, error: 'Invalid coordinate format' }
  }

  if (isNaN(lat) || isNaN(lng)) {
    return { isValid: false, error: 'Coordinates must be numbers' }
  }

  if (lat < -90 || lat > 90) {
    return { isValid: false, error: 'Latitude must be between -90 and 90' }
  }

  if (lng < -180 || lng > 180) {
    return { isValid: false, error: 'Longitude must be between -180 and 180' }
  }

  return { isValid: true }
}

/**
 * Validate Vancouver area coordinates (rough bounds)
 */
export const isInVancover = (lat: number, lng: number): boolean => {
  // Vancouver metro area rough bounds
  const bounds = {
    north: 49.4,
    south: 49.0,
    east: -122.5,
    west: -123.3
  }

  return (
    lat >= bounds.south &&
    lat <= bounds.north &&
    lng >= bounds.west &&
    lng <= bounds.east
  )
}

/**
 * Sanitize and validate preferences array
 */
export const validatePreferences = (
  preferences: string[]
): { isValid: boolean; sanitized: string[]; error?: string } => {
  if (!Array.isArray(preferences)) {
    return { isValid: false, sanitized: [], error: 'Preferences must be an array' }
  }

  const validPreferences = [
    'fastest',
    'safest',
    'eco_friendly',
    'scenic',
    'healthy',
    'cheapest'
  ]

  const sanitized = preferences
    .filter(pref => typeof pref === 'string')
    .map(pref => sanitizeInput(pref))
    .filter(pref => validPreferences.includes(pref))

  if (sanitized.length === 0) {
    return { isValid: false, sanitized: [], error: 'At least one valid preference required' }
  }

  return { isValid: true, sanitized }
}

/**
 * Sanitize and validate transport modes array
 */
export const validateTransportModes = (
  modes: string[]
): { isValid: boolean; sanitized: string[]; error?: string } => {
  if (!Array.isArray(modes)) {
    return { isValid: false, sanitized: [], error: 'Transport modes must be an array' }
  }

  const validModes = [
    'walking',
    'biking',
    'scooter',
    'car',
    'bus',
    'skytrain',
    'seabus',
    'west_coast_express'
  ]

  const sanitized = modes
    .filter(mode => typeof mode === 'string')
    .map(mode => sanitizeInput(mode))
    .filter(mode => validModes.includes(mode))

  if (sanitized.length === 0) {
    return { isValid: false, sanitized: [], error: 'At least one valid transport mode required' }
  }

  return { isValid: true, sanitized }
}
