import React, { useMemo, useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Cloud,
  CloudRain,
  Sun,
  CloudSnow,
  Wind,
  Eye,
  Thermometer,
  Droplets,
  AlertTriangle,
  MapPin,
  Bus,
  Clock,
  Bell,
  Info,
  CheckCircle,
  X,
  Zap,
  Leaf,
  Shield
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useRoute } from '../contexts/RouteContext'
import { formatTimeAgo } from '../utils/formatting'

interface WeatherData {
  condition: string
  temperature: number
  humidity: number
  windSpeed: number
  visibility: number
}

interface TrafficData {
  level: 'low' | 'moderate' | 'high' | 'severe'
  incidents: number
}

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

interface RealTimePanelProps {
  weather?: WeatherData
  traffic?: TrafficData
  roadEvents?: Array<{
    type: 'construction' | 'closure' | 'accident'
    location: string
    severity: 'low' | 'medium' | 'high'
  }>
}

const RealTimePanel: React.FC<RealTimePanelProps> = ({
  weather,
  traffic,
  roadEvents = []
}) => {
  const { state: routeState } = useRoute()
  const [notifications, setNotifications] = useState<Notification[]>([])

  // Mock data for demo
  const mockWeather: WeatherData = {
    condition: 'clear',
    temperature: 18,
    humidity: 65,
    windSpeed: 12,
    visibility: 15
  }

  const mockTraffic: TrafficData = {
    level: 'moderate',
    incidents: 3
  }

  const mockRoadEvents = [
    { type: 'construction' as const, location: 'Granville St Bridge', severity: 'medium' as const },
    { type: 'closure' as const, location: 'Robson St', severity: 'high' as const }
  ]

  const currentWeather = weather || mockWeather
  const currentTraffic = traffic || mockTraffic
  const currentRoadEvents = roadEvents.length > 0 ? roadEvents : mockRoadEvents

  // Mock notifications for demo (including road events as alerts)
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
          window.location.href = '/'
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
      }
    ]

    // Convert road events to alerts
    const roadEventNotifications: Notification[] = currentRoadEvents.map((event, index) => ({
      id: `road-event-${index}`,
      type: event.severity === 'high' ? 'alert' : event.severity === 'medium' ? 'warning' : 'info',
      title: `${event.type.charAt(0).toUpperCase() + event.type.slice(1)} Alert`,
      message: `${event.type.charAt(0).toUpperCase() + event.type.slice(1)} on ${event.location}. Exercise caution.`,
      timestamp: new Date(Date.now() - (index + 1) * 20 * 60 * 1000),
      priority: event.severity,
      category: 'safety' as const
    }))

    setNotifications([...mockNotifications, ...roadEventNotifications])
  }, [currentRoadEvents])

  // Extract transit delays and alerts from selected route
  const transitDelays = useMemo(() => {
    if (!routeState.selectedRoute) return []

    const delays: Array<{ route: string; delay: number; stop: string }> = []
    routeState.selectedRoute.steps.forEach((step) => {
      if (step.transit_details && step.transit_details.is_delayed) {
        delays.push({
          route: step.transit_details.short_name || step.transit_details.line || 'Transit',
          delay: step.transit_details.delay_minutes || 0,
          stop: step.transit_details.departure_stop || 'Unknown'
        })
      }
    })
    return delays
  }, [routeState.selectedRoute])

  const transitAlerts = useMemo(() => {
    if (!routeState.selectedRoute) return []

    const alerts: Array<{ header: string; description: string; route: string }> = []
    routeState.selectedRoute.steps.forEach((step) => {
      if (step.transit_details?.service_alerts) {
        step.transit_details.service_alerts.forEach((alert) => {
          alerts.push({
            header: alert.header || 'Service Alert',
            description: alert.description || '',
            route: step.transit_details!.short_name || step.transit_details!.line || 'Transit'
          })
        })
      }
    })
    return alerts
  }, [routeState.selectedRoute])

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'clear':
      case 'sunny':
        return <Sun className="w-5 h-5 text-yellow-500" />
      case 'rain':
      case 'rainy':
        return <CloudRain className="w-5 h-5 text-blue-500" />
      case 'snow':
        return <CloudSnow className="w-5 h-5 text-blue-300" />
      case 'cloudy':
      case 'overcast':
        return <Cloud className="w-5 h-5 text-gray-500" />
      default:
        return <Sun className="w-5 h-5 text-yellow-500" />
    }
  }

  const getTrafficColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-100'
      case 'moderate':
        return 'text-yellow-600 bg-yellow-100'
      case 'high':
        return 'text-orange-600 bg-orange-100'
      case 'severe':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

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

  const getNotificationBorderColor = (type: string) => {
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

  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="card-compact space-y-4"
    >
      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
        <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
        Real-Time Updates & Alerts
      </h3>

      {/* Smart Alerts - Always Visible */}
      {notifications.length > 0 && (
        <div className="space-y-2">
          {notifications.map((notification, index) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={cn(
                "p-3 border-l-4 relative bg-white/40 backdrop-blur-sm rounded-lg",
                getNotificationBorderColor(notification.type)
              )}
            >
              {/* Dismiss Button */}
              <button
                onClick={() => dismissNotification(notification.id)}
                className="absolute top-2 right-2 w-5 h-5 rounded-full bg-white/60 hover:bg-white/80 flex items-center justify-center transition-colors"
              >
                <X className="w-3 h-3 text-gray-500" />
              </button>

              {/* Notification Content */}
              <div className="flex items-start space-x-2 pr-6">
                <div className={cn(
                  "w-7 h-7 rounded-lg flex items-center justify-center text-white flex-shrink-0",
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
                      <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
                    )}
                  </div>

                  <p className="text-xs text-gray-600 mb-1 leading-relaxed">
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
        </div>
      )}

      {/* Weather Section */}
      <div className="space-y-2 pt-2 border-t border-white/30">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Weather</span>
          <div className="flex items-center space-x-2">
            {getWeatherIcon(currentWeather.condition)}
            <span className="text-sm text-gray-600 capitalize">{currentWeather.condition}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center space-x-2 text-xs">
            <Thermometer className="w-3 h-3 text-red-500" />
            <span className="text-gray-600">{currentWeather.temperature}°C</span>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <Droplets className="w-3 h-3 text-blue-500" />
            <span className="text-gray-600">{currentWeather.humidity}%</span>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <Wind className="w-3 h-3 text-gray-500" />
            <span className="text-gray-600">{currentWeather.windSpeed} km/h</span>
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <Eye className="w-3 h-3 text-purple-500" />
            <span className="text-gray-600">{currentWeather.visibility} km</span>
          </div>
        </div>
      </div>

      {/* Traffic Section */}
      <div className="space-y-2 pt-2 border-t border-white/30">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Traffic</span>
          <div className={cn(
            "px-2 py-1 rounded-full text-xs font-medium",
            getTrafficColor(currentTraffic.level)
          )}>
            {currentTraffic.level.charAt(0).toUpperCase() + currentTraffic.level.slice(1)}
          </div>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600">Active incidents</span>
          <span className="font-medium text-gray-900">{currentTraffic.incidents}</span>
        </div>
      </div>

      {/* Transit Delays */}
      {transitDelays.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-white/30">
          <span className="text-sm font-medium text-gray-700 flex items-center">
            <Bus className="w-4 h-4 mr-2" />
            Transit Delays
          </span>
          <div className="space-y-2">
            {transitDelays.map((delay, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-center space-x-2 p-2 rounded-lg border-l-4 border-orange-500 bg-orange-50/50"
              >
                <Clock className="w-3 h-3 text-orange-600" />
                <div className="flex-1">
                  <div className="text-xs font-medium text-gray-900">
                    Route {delay.route}
                  </div>
                  <div className="text-xs text-gray-600">
                    {delay.stop} • +{delay.delay} min delay
                  </div>
                </div>
                <div className="text-xs font-semibold text-orange-600">
                  +{delay.delay}m
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Transit Service Alerts */}
      {transitAlerts.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-white/30">
          <span className="text-sm font-medium text-gray-700 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2 text-yellow-600" />
            Service Alerts
          </span>
          <div className="space-y-2">
            {transitAlerts.map((alert, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-start space-x-2 p-2 rounded-lg border-l-4 border-yellow-500 bg-yellow-50/50"
              >
                <AlertTriangle className="w-3 h-3 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-xs font-medium text-gray-900">
                    {alert.header}
                  </div>
                  {alert.description && (
                    <div className="text-xs text-gray-600 mt-0.5">
                      {alert.description}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1">
                    Route {alert.route}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}


      {/* Update Time */}
      <div className="text-xs text-gray-500 text-center pt-2 border-t border-white/30">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </motion.div>
  )
}

export default RealTimePanel
