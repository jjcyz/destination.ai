import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { MapPin, Trophy, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '../utils/cn'

const TopNavigation: React.FC = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Routes', icon: MapPin },
    { path: '/dashboard', label: 'Stats', icon: BarChart3 },
    { path: '/gamification', label: 'Rewards', icon: Trophy },
  ]

  return (
    <>
      {/* Desktop Navigation - Top right menu button */}
      <div className="hidden lg:block fixed top-4 right-4 z-[100]">
        <motion.nav
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-white/40 p-2 flex gap-2"
        >
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path
            return (
              <Link
                key={path}
                to={path}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200",
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
      </div>

      {/* Mobile Bottom Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="lg:hidden fixed bottom-0 left-0 right-0 z-[100] bg-white/95 backdrop-blur-lg border-t border-gray-200 shadow-2xl"
        style={{ paddingBottom: 'max(0.5rem, env(safe-area-inset-bottom))' }}
      >
        <div className="flex items-center justify-around px-4 py-2">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path
            return (
              <Link
                key={path}
                to={path}
                className={cn(
                  "flex flex-col items-center justify-center py-2 px-4 rounded-xl transition-all duration-200 flex-1",
                  isActive
                    ? 'text-primary-700'
                    : 'text-gray-600'
                )}
              >
                <Icon className={cn(
                  "w-6 h-6 mb-1",
                  isActive && 'stroke-[2.5]'
                )} />
                <span className={cn(
                  "text-xs",
                  isActive && 'font-semibold'
                )}>
                  {label}
                </span>
              </Link>
            )
          })}
        </div>
      </motion.nav>
    </>
  )
}

export default TopNavigation
