import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import type { Point, Route } from '../types'

interface RouteState {
  currentRoutes: Route[]
  alternatives: Route[]
  selectedRoute: Route | null
  isLoading: boolean
  error: string | null
  lastRequest: {
    origin: Point | null
    destination: Point | null
    preferences: string[]
  } | null
}

type RouteAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ROUTES'; payload: { routes: Route[]; alternatives: Route[] } }
  | { type: 'SELECT_ROUTE'; payload: Route }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LAST_REQUEST'; payload: { origin: Point; destination: Point; preferences: string[] } }

const initialState: RouteState = {
  currentRoutes: [],
  alternatives: [],
  selectedRoute: null,
  isLoading: false,
  error: null,
  lastRequest: null,
}

function routeReducer(state: RouteState, action: RouteAction): RouteState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload, error: null }
    case 'SET_ROUTES':
      return {
        ...state,
        currentRoutes: action.payload.routes,
        alternatives: action.payload.alternatives,
        selectedRoute: action.payload.routes[0] || null,
        isLoading: false,
        error: null,
      }
    case 'SELECT_ROUTE':
      return { ...state, selectedRoute: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    case 'SET_LAST_REQUEST':
      return { ...state, lastRequest: action.payload }
    default:
      return state
  }
}

interface RouteContextType {
  state: RouteState
  dispatch: React.Dispatch<RouteAction>
}

const RouteContext = createContext<RouteContextType | undefined>(undefined)

export function RouteProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(routeReducer, initialState)

  return (
    <RouteContext.Provider value={{ state, dispatch }}>
      {children}
    </RouteContext.Provider>
  )
}

export function useRoute() {
  const context = useContext(RouteContext)
  if (context === undefined) {
    throw new Error('useRoute must be used within a RouteProvider')
  }
  return context
}
