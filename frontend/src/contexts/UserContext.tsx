import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import type { UserProfile } from '../types'

interface UserState {
  profile: UserProfile
  isAuthenticated: boolean
}

type UserAction =
  | { type: 'SET_PROFILE'; payload: UserProfile }
  | { type: 'UPDATE_POINTS'; payload: number }
  | { type: 'ADD_ACHIEVEMENT'; payload: string }
  | { type: 'ADD_BADGE'; payload: string }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }

const initialProfile: UserProfile = {
  user_id: 'demo_user',
  preferred_modes: ['walking', 'biking', 'bus'],
  fitness_level: 'moderate',
  sustainability_goals: true,
  accessibility_needs: [],
  total_sustainability_points: 0,
  level: 1,
  achievements: [],
  badges: [],
  streak_days: 0,
  total_distance_saved: 0,
}

const initialState: UserState = {
  profile: initialProfile,
  isAuthenticated: false,
}

function userReducer(state: UserState, action: UserAction): UserState {
  switch (action.type) {
    case 'SET_PROFILE':
      return { ...state, profile: action.payload }
    case 'UPDATE_POINTS':
      const newPoints = (state.profile.total_sustainability_points || 0) + action.payload
      const newLevel = Math.floor(newPoints / 100) + 1
      return {
        ...state,
        profile: {
          ...state.profile,
          total_sustainability_points: newPoints,
          level: newLevel,
        },
      }
    case 'ADD_ACHIEVEMENT':
      return {
        ...state,
        profile: {
          ...state.profile,
          achievements: [...(state.profile.achievements || []), action.payload],
        },
      }
    case 'ADD_BADGE':
      return {
        ...state,
        profile: {
          ...state.profile,
          badges: [...(state.profile.badges || []), action.payload],
        },
      }
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload }
    default:
      return state
  }
}

interface UserContextType {
  state: UserState
  dispatch: React.Dispatch<UserAction>
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(userReducer, initialState)

  return (
    <UserContext.Provider value={{ state, dispatch }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
