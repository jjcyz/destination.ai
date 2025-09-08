import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bell,
  AlertTriangle,
  Info,
  CheckCircle,
  X,
  Clock,
  MapPin,
  Zap,
  Leaf,
  Shield
} from 'lucide-react'
import { cn } from '../utils/cn'

interface Notification {
  id: string
  type: 'warning' | 'info' | 'success' | 'alert'
  title: string
  message: string
  timestamp: Date
  priority: 'low' | 'medium' | 'high'
  category: 'traffic' | 'weather' | 'route' | 'safety' | 'eco'
  actionable?: boolean
  actionText?: string
  onAction?: () => void
}

interface PredictiveNotificationsProps {
  className?: string
}

const PredictiveNotifications: React.FC<PredictiveNotificationsProps> = ({
  className
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isExpanded, setIsExpanded] = useState(false)

  // Mock notifications for demo
  useEffect(() => {
    const mockNotifications: Notification[] = [
      {
        id: '1',
        type: 'warning',
        title: 'Traffic Alert',
        message: 'Heavy traffic expected on Granville St Bridge in 15 minutes. Consider alternative routes.',
        timestamp: new Date(),
        priority: 'high',
        category: 'traffic',
        actionable: true,
        actionText: 'Find Alternative',
        onAction: () => {
          // TODO: Implement alternative route finding
        }
      },
      {
        id: '2',
        type: 'info',
        title: 'Weather Update',
        message: 'Light rain starting in 30 minutes. Consider bringing an umbrella for walking routes.',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        priority: 'medium',
        category: 'weather'
      },
      {
        id: '3',
        type: 'success',
        title: 'Eco-Friendly Route',
        message: 'Your selected route saves 2.3kg CO₂ compared to driving. Great choice!',
        timestamp: new Date(Date.now() - 10 * 60 * 1000),
        priority: 'low',
        category: 'eco'
      },
      {
        id: '4',
        type: 'alert',
        title: 'Safety Notice',
        message: 'Construction zone ahead on Robson St. Exercise caution when walking or cycling.',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        priority: 'high',
        category: 'safety',
        actionable: true,
        actionText: 'View Details',
        onAction: () => {
          // TODO: Implement safety details viewing
        }
      }
    ]

    setNotifications(mockNotifications)
  }, [])

  const getNotificationIcon = (type: string, category: string) => {
    if (category === 'traffic') return <MapPin className="w-4 h-4" />
    if (category === 'weather') return <Zap className="w-4 h-4" />
    if (category === 'eco') return <Leaf className="w-4 h-4" />
    if (category === 'safety') return <Shield className="w-4 h-4" />

    switch (type) {
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />
      case 'info':
        return <Info className="w-4 h-4" />
      case 'success':
        return <CheckCircle className="w-4 h-4" />
      case 'alert':
        return <Bell className="w-4 h-4" />
      default:
        return <Info className="w-4 h-4" />
    }
  }

  const getNotificationColor = (type: string, priority: string) => {
    const baseColors = {
      warning: 'from-yellow-500 to-orange-500',
      info: 'from-blue-500 to-cyan-500',
      success: 'from-green-500 to-emerald-500',
      alert: 'from-red-500 to-pink-500'
    }

    const priorityIntensity = {
      low: 'opacity-70',
      medium: 'opacity-85',
      high: 'opacity-100'
    }

    return `${baseColors[type as keyof typeof baseColors]} ${priorityIntensity[priority as keyof typeof priorityIntensity]}`
  }

  const getBorderColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'border-l-yellow-500'
      case 'info':
        return 'border-l-blue-500'
      case 'success':
        return 'border-l-green-500'
      case 'alert':
        return 'border-l-red-500'
      default:
        return 'border-l-gray-500'
    }
  }

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return timestamp.toLocaleDateString()
  }

  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const highPriorityCount = notifications.filter(n => n.priority === 'high').length
  const unreadCount = notifications.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn("space-y-4", className)}
    >
      {/* Header */}
      <motion.button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full glass-card p-4 flex items-center justify-between hover:bg-white/60 transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-xl flex items-center justify-center text-white">
              <Bell className="w-5 h-5" />
            </div>
            {unreadCount > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold"
              >
                {unreadCount > 9 ? '9+' : unreadCount}
              </motion.div>
            )}
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-gray-900">Smart Alerts</h3>
            <p className="text-sm text-gray-500">
              {unreadCount} notification{unreadCount !== 1 ? 's' : ''}
              {highPriorityCount > 0 && (
                <span className="text-red-500 ml-1">({highPriorityCount} urgent)</span>
              )}
            </p>
          </div>
        </div>

        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <Clock className="w-5 h-5 text-gray-400" />
        </motion.div>
      </motion.button>

      {/* Notifications List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-3 overflow-hidden"
          >
            {notifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={cn(
                  "glass-card p-4 border-l-4 relative",
                  getBorderColor(notification.type)
                )}
              >
                {/* Dismiss Button */}
                <button
                  onClick={() => dismissNotification(notification.id)}
                  className="absolute top-2 right-2 w-6 h-6 rounded-full bg-white/60 hover:bg-white/80 flex items-center justify-center transition-colors"
                >
                  <X className="w-3 h-3 text-gray-500" />
                </button>

                {/* Notification Content */}
                <div className="flex items-start space-x-3 pr-8">
                  <div className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center text-white",
                    `bg-gradient-to-br ${getNotificationColor(notification.type, notification.priority)}`
                  )}>
                    {getNotificationIcon(notification.type, notification.category)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-gray-900 text-sm">
                        {notification.title}
                      </h4>
                      {notification.priority === 'high' && (
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-2 leading-relaxed">
                      {notification.message}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {formatTimeAgo(notification.timestamp)}
                      </span>

                      {notification.actionable && (
                        <motion.button
                          onClick={notification.onAction}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors"
                        >
                          {notification.actionText}
                        </motion.button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}

            {notifications.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-8 text-gray-500"
              >
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No notifications at the moment</p>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default PredictiveNotifications
