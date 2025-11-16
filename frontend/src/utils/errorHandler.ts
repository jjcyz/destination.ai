/**
 * Centralized error handling utilities
 */

/**
 * Extract a user-friendly error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unknown error occurred'
}

/**
 * Check if an error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message.includes('network') ||
      error.message.includes('fetch') ||
      error.message.includes('timeout')
    )
  }
  return false
}

/**
 * Format error for display to user
 */
export function formatErrorForUser(error: unknown): string {
  const message = getErrorMessage(error)

  if (isNetworkError(error)) {
    return 'Network error. Please check your connection and try again.'
  }

  return message || 'Something went wrong. Please try again.'
}

