import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { MapPin, Trophy, BarChart3, Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../utils/cn'

const TopNavigation: React.FC = () => {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const navItems = [
    { path: '/', label: 'Route Planner', icon: MapPin },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/gamification', label: 'Achievements', icon: Trophy },
  ]

  return (
    <>
      {/* Floating Menu Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 right-4 z-[100] text-gray-700 hover:text-gray-900 transition-colors duration-200"
        aria-label="Navigation menu"
      >
        {isOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <Menu className="w-6 h-6" />
        )}
      </motion.button>

      {/* Floating Navigation Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-[90] bg-black/10 backdrop-blur-sm"
            />

            {/* Menu */}
            <motion.nav
              initial={{ opacity: 0, scale: 0.9, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -10 }}
              transition={{ duration: 0.2 }}
              className="fixed top-16 right-4 z-[100] bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-white/40 p-2 min-w-[180px]"
            >
              {navItems.map(({ path, label, icon: Icon }) => {
                const isActive = location.pathname === path
                return (
                  <Link
                    key={path}
                    to={path}
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                      isActive
                        ? 'bg-primary-500/10 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100/80'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{label}</span>
                  </Link>
                )
              })}
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

export default TopNavigation
