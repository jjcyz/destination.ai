/// <reference types="vite/client" />

/**
 * Type definitions for custom environment variables
 *
 * Vite automatically provides: DEV, PROD, MODE, SSR, BASE_URL
 * Only custom VITE_* variables need to be declared here for type safety
 *
 * @see https://vitejs.dev/guide/env-and-mode.html
 */
interface ImportMetaEnv {
  /**
   * Base URL for the backend API
   * @example 'http://localhost:8000/api/v1'
   */
  readonly VITE_API_BASE_URL?: string

  /**
   * Google Maps API key for Places and Maps services
   * @example 'AIzaSy...'
   */
  readonly VITE_GOOGLE_MAPS_API_KEY?: string
}

