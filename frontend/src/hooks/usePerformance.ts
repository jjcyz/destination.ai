import { useEffect, useRef } from 'react'

interface PerformanceMetrics {
  componentName: string
  renderTime: number
  mountTime: number
  updateCount: number
}

/**
 * Hook for monitoring component performance
 * Useful for identifying slow components and optimization opportunities
 */
export const usePerformanceMonitor = (componentName: string, enabled = import.meta.env.DEV) => {
  const mountTime = useRef<number>(Date.now())
  const renderCount = useRef<number>(0)
  const lastRenderTime = useRef<number>(Date.now())

  useEffect(() => {
    if (!enabled) return

    renderCount.current++
    const renderTime = Date.now() - lastRenderTime.current
    lastRenderTime.current = Date.now()

    // Log slow renders (>16ms = dropping below 60fps)
    if (renderTime > 16 && renderCount.current > 1) {
      console.warn(
        `⚠️ Slow render in ${componentName}: ${renderTime}ms (render #${renderCount.current})`
      )
    }

    // Log on first mount
    if (renderCount.current === 1) {
      const initialLoadTime = Date.now() - mountTime.current
      console.log(`✅ ${componentName} mounted in ${initialLoadTime}ms`)
    }
  })

  const logMetric = (metricName: string, value: number) => {
    if (!enabled) return
    console.log(`📊 ${componentName} - ${metricName}: ${value}ms`)
  }

  return { logMetric }
}

/**
 * Hook for measuring async operation performance
 */
export const useMeasureAsync = (operationName: string) => {
  const measure = async <T,>(operation: () => Promise<T>): Promise<T> => {
    const startTime = performance.now()

    try {
      const result = await operation()
      const duration = performance.now() - startTime

      if (import.meta.env.DEV) {
        console.log(`⏱️ ${operationName} completed in ${duration.toFixed(2)}ms`)
      }

      // Log slow operations (>2 seconds)
      if (duration > 2000) {
        console.warn(`⚠️ Slow operation: ${operationName} took ${duration.toFixed(2)}ms`)
      }

      return result
    } catch (error) {
      const duration = performance.now() - startTime
      console.error(`❌ ${operationName} failed after ${duration.toFixed(2)}ms`, error)
      throw error
    }
  }

  return { measure }
}

/**
 * Log web vitals (Core Web Vitals metrics)
 */
export const useWebVitals = () => {
  useEffect(() => {
    if (import.meta.env.PROD) {
      // In production, you would send these to analytics
      // For now, just log in development
      return
    }

    // Largest Contentful Paint (LCP)
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log('📈 LCP:', entry)
      }
    })
    observer.observe({ entryTypes: ['largest-contentful-paint'] })

    // First Input Delay would be measured here
    // Cumulative Layout Shift would be measured here

    return () => observer.disconnect()
  }, [])
}

/**
 * Monitor API call performance
 */
export const useAPIMetrics = () => {
  const metrics = useRef<Map<string, number[]>>(new Map())

  const recordAPICall = (endpoint: string, duration: number) => {
    if (!metrics.current.has(endpoint)) {
      metrics.current.set(endpoint, [])
    }
    metrics.current.get(endpoint)!.push(duration)
  }

  const getAverageTime = (endpoint: string): number => {
    const times = metrics.current.get(endpoint)
    if (!times || times.length === 0) return 0

    const sum = times.reduce((a, b) => a + b, 0)
    return sum / times.length
  }

  const logSummary = () => {
    if (import.meta.env.DEV) {
      console.group('📊 API Performance Summary')
      metrics.current.forEach((times, endpoint) => {
        const avg = times.reduce((a, b) => a + b, 0) / times.length
        const min = Math.min(...times)
        const max = Math.max(...times)
        console.log(`${endpoint}:`, {
          calls: times.length,
          avg: `${avg.toFixed(2)}ms`,
          min: `${min.toFixed(2)}ms`,
          max: `${max.toFixed(2)}ms`
        })
      })
      console.groupEnd()
    }
  }

  return {
    recordAPICall,
    getAverageTime,
    logSummary
  }
}
