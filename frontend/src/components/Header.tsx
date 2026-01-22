import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { MapPin, Trophy, BarChart3, Menu, X, Leaf } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'
import { useUser } from '../contexts/UserContext'

const Header: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { state: userState } = useUser()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navItems = [
    { path: '/', label: 'Route Planner', icon: MapPin },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/gamification', label: 'Achievements', icon: Trophy },
  ]

  const handleNavClick = (path: string) => {
    setIsMenuOpen(false)
    navigate(path)
  }

  return (
    <>
      {/* Minimalist Nav Icon - Fixed Top Left */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        onClick={() => setIsMenuOpen(true)}
        className="fixed top-4 left-4 z-50 w-12 h-12 rounded-full glass-card flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 active:scale-95 touch-manipulation"
        aria-label="Open navigation menu"
      >
        <Menu className="w-6 h-6 text-gray-700" />
      </motion.button>


      {/* Drawer Menu Overlay */}
      <AnimatePresence>
        {isMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setIsMenuOpen(false)}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            />

            {/* Drawer */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed top-0 left-0 h-full w-72 max-w-[85vw] glass-card-strong shadow-2xl z-50 overflow-y-auto"
            >
              {/* Drawer Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/20">
                <Link to="/" onClick={() => setIsMenuOpen(false)} className="flex items-center space-x-3 group">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg">
                    <Leaf className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-lg font-bold text-gray-900">Destination AI</h1>
                    <p className="text-xs text-gray-600">AI-Powered Routes</p>
                  </div>
                </Link>
                <button
                  onClick={() => setIsMenuOpen(false)}
                  className="w-10 h-10 rounded-full glass-card flex items-center justify-center hover:bg-white/80 transition-colors touch-manipulation"
                  aria-label="Close menu"
                >
                  <X className="w-5 h-5 text-gray-700" />
                </button>
              </div>

              {/* Navigation Items */}
              <nav className="p-4 space-y-2">
                {navItems.map(({ path, label, icon: Icon }) => {
                  const isActive = location.pathname === path
                  return (
                    <motion.button
                      key={path}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleNavClick(path)}
                      className={cn(
                        "w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium text-left touch-manipulation",
                        isActive
                          ? 'bg-primary-500/10 text-primary-700 border border-primary-200/50'
                          : 'text-gray-700 hover:bg-white/60 hover:text-gray-900'
                      )}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      <span>{label}</span>
                    </motion.button>
                  )
                })}
              </nav>

              {/* User Info Section */}
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/20">
                <div className="glass-card p-4 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-900">Your Progress</span>
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-xs">{userState.profile.level}</span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-600">
                    {userState.profile.total_sustainability_points || 0} sustainability points
                  </div>
                  {(userState.profile.streak_days || 0) > 0 && (
                    <div className="text-xs text-green-600 mt-1">
                      🔥 {userState.profile.streak_days} day streak
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

export default Header
