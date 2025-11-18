/**
 * Centralized formatting utilities
 * Provides consistent formatting for time, distance, and other values
 */

/**
 * Format time in seconds to human-readable string
 * @param seconds - Time in seconds
 * @returns Formatted string (e.g., "5m", "1h 30m", "45s")
 */
export const formatTime = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds}s`
  }
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

/**
 * Format distance in meters to human-readable string
 * @param meters - Distance in meters
 * @returns Formatted string (e.g., "500m", "2.5km")
 */
export const formatDistance = (meters: number): string => {
  if (meters < 1000) return `${meters}m`
  return `${(meters / 1000).toFixed(1)}km`
}

/**
 * Format time string (HH:MM:SS, HH:MM, or ISO date string) to readable format
 * Used for transit departure/arrival times
 * @param timeString - Time string in various formats
 * @returns Formatted string or null if invalid
 */
export const formatTimeString = (timeString?: string): string | null => {
  if (!timeString) return null

  // Try parsing as Date first (handles ISO format)
  try {
    const date = new Date(timeString)
    if (!isNaN(date.getTime())) {
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    }
  } catch {
    // Fall through to string parsing
  }

  // Handle HH:MM:SS or HH:MM format
  const parts = timeString.split(':')
  if (parts.length >= 2) {
    const hours = parseInt(parts[0], 10)
    const minutes = parseInt(parts[1], 10)
    if (!isNaN(hours) && !isNaN(minutes)) {
      const period = hours >= 12 ? 'PM' : 'AM'
      const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours
      return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`
    }
  }

  return timeString
}

/**
 * Format relative time (time ago)
 * @param timestamp - Date to format
 * @returns Formatted string (e.g., "5 minutes ago", "2 hours ago")
 */
export const formatTimeAgo = (timestamp: Date): string => {
  const now = new Date()
  const diffMs = now.getTime() - timestamp.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
}

