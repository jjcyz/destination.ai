/**
 * Form persistence utility for saving and restoring form state
 */

const STORAGE_KEY = 'destination_ai_last_search'

export interface PersistedFormState {
  origin: string
  destination: string
  preferences: string[]
  transportModes: string[]
  maxWalkingDistance: number
  timestamp: number
}

/**
 * Save form state to localStorage
 */
export const saveFormState = (state: Omit<PersistedFormState, 'timestamp'>): void => {
  try {
    const dataToSave: PersistedFormState = {
      ...state,
      timestamp: Date.now()
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave))
  } catch (error) {
    console.warn('Failed to save form state:', error)
  }
}

/**
 * Load form state from localStorage
 * Returns null if not found or expired (> 7 days old)
 */
export const loadFormState = (): PersistedFormState | null => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return null

    const data: PersistedFormState = JSON.parse(saved)

    // Expire after 7 days
    const sevenDaysInMs = 7 * 24 * 60 * 60 * 1000
    if (Date.now() - data.timestamp > sevenDaysInMs) {
      clearFormState()
      return null
    }

    return data
  } catch (error) {
    console.warn('Failed to load form state:', error)
    return null
  }
}

/**
 * Clear saved form state
 */
export const clearFormState = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.warn('Failed to clear form state:', error)
  }
}
