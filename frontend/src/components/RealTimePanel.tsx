import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Cloud,
  CloudRain,
  Sun,
  CloudSnow,
  Wind,
  Eye,
  Thermometer,
  Droplets,
  Car,
  AlertTriangle,
  Construction,
  MapPin,
  Bus,
  Clock
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useRoute } from '../contexts/RouteContext'

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

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'construction':
        return <Construction className="w-4 h-4 text-orange-500" />
      case 'closure':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case 'accident':
        return <Car className="w-4 h-4 text-red-500" />
      default:
        return <MapPin className="w-4 h-4 text-gray-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'border-l-green-500'
      case 'medium':
        return 'border-l-yellow-500'
      case 'high':
        return 'border-l-red-500'
      default:
        return 'border-l-gray-500'
    }
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
        Real-Time Updates
      </h3>

      {/* Weather Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Weather</span>
          <div className="flex items-center space-x-2">
            {getWeatherIcon(currentWeather.condition)}
            <span className="text-sm text-gray-600 capitalize">{currentWeather.condition}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center space-x-2 text-sm">
            <Thermometer className="w-4 h-4 text-red-500" />
            <span className="text-gray-600">{currentWeather.temperature}°C</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Droplets className="w-4 h-4 text-blue-500" />
            <span className="text-gray-600">{currentWeather.humidity}%</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Wind className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">{currentWeather.windSpeed} km/h</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Eye className="w-4 h-4 text-purple-500" />
            <span className="text-gray-600">{currentWeather.visibility} km</span>
          </div>
        </div>
      </div>

      {/* Traffic Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Traffic</span>
          <div className={cn(
            "px-2 py-1 rounded-full text-xs font-medium",
            getTrafficColor(currentTraffic.level)
          )}>
            {currentTraffic.level.charAt(0).toUpperCase() + currentTraffic.level.slice(1)}
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Active incidents</span>
          <span className="font-medium text-gray-900">{currentTraffic.incidents}</span>
        </div>
      </div>

      {/* Transit Delays */}
      {transitDelays.length > 0 && (
        <div className="space-y-3">
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
                className="flex items-center space-x-3 p-3 rounded-lg border-l-4 border-orange-500 bg-orange-50/50"
              >
                <Clock className="w-4 h-4 text-orange-600" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    Route {delay.route}
                  </div>
                  <div className="text-xs text-gray-600">
                    {delay.stop} • +{delay.delay} min delay
                  </div>
                </div>
                <div className="text-sm font-semibold text-orange-600">
                  +{delay.delay}m
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Transit Service Alerts */}
      {transitAlerts.length > 0 && (
        <div className="space-y-3">
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
                className="flex items-start space-x-3 p-3 rounded-lg border-l-4 border-yellow-500 bg-yellow-50/50"
              >
                <AlertTriangle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
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

      {/* Road Events */}
      {currentRoadEvents.length > 0 && (
        <div className="space-y-3">
          <span className="text-sm font-medium text-gray-700">Road Events</span>
          <div className="space-y-2">
            {currentRoadEvents.map((event, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={cn(
                  "flex items-center space-x-3 p-3 rounded-lg border-l-4 bg-white/50",
                  getSeverityColor(event.severity)
                )}
              >
                {getEventIcon(event.type)}
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 capitalize">
                    {event.type}
                  </div>
                  <div className="text-xs text-gray-600">{event.location}</div>
                </div>
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  event.severity === 'high' ? 'bg-red-500' :
                  event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                )} />
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
