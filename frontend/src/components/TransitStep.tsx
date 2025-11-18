import React from 'react'
import { Clock, AlertTriangle, Bus, Train, MapPin, ArrowRight } from 'lucide-react'
import { cn } from '../utils/cn'
import type { TransitDetails } from '../types'
import { formatTimeString } from '../utils/formatting'

interface TransitStepProps {
  transitDetails: TransitDetails
  estimatedTime: number
  className?: string
}

const TransitStep: React.FC<TransitStepProps> = ({
  transitDetails,
  estimatedTime,
  className
}) => {

  const getVehicleIcon = (vehicleType?: string) => {
    const type = vehicleType?.toLowerCase() || ''
    if (type.includes('train') || type.includes('subway') || type.includes('skytrain')) {
      return <Train className="w-4 h-4" />
    }
    return <Bus className="w-4 h-4" />
  }

  const hasDelay = transitDetails.is_delayed && (transitDetails.delay_minutes || 0) > 0
  const hasAlerts = transitDetails.service_alerts && transitDetails.service_alerts.length > 0

  return (
    <div className={cn("space-y-2", className)}>
      {/* Main Transit Info */}
      <div className="flex items-start space-x-3 p-3 bg-blue-50/50 rounded-lg border border-blue-100">
        <div className="flex-shrink-0 mt-0.5">
          {getVehicleIcon(transitDetails.vehicle_type)}
        </div>

        <div className="flex-1 min-w-0">
          {/* Route Info */}
          <div className="flex items-center space-x-2 mb-1">
            <span className="font-semibold text-gray-900">
              {transitDetails.short_name || transitDetails.line || 'Transit'}
            </span>
            {transitDetails.headsign && (
              <>
                <ArrowRight className="w-3 h-3 text-gray-400" />
                <span className="text-sm text-gray-600">{transitDetails.headsign}</span>
              </>
            )}
          </div>

          {/* Stops */}
          <div className="text-sm text-gray-600 space-y-1">
            {transitDetails.departure_stop && (
              <div className="flex items-center space-x-2">
                <MapPin className="w-3 h-3 text-green-600" />
                <span>{transitDetails.departure_stop}</span>
              </div>
            )}
            {transitDetails.arrival_stop && (
              <div className="flex items-center space-x-2">
                <MapPin className="w-3 h-3 text-red-600" />
                <span>{transitDetails.arrival_stop}</span>
              </div>
            )}
          </div>

          {/* Departure Time with Delay */}
          {transitDetails.departure_time && (
            <div className="flex items-center space-x-2 mt-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">
                Departs: {formatTimeString(transitDetails.departure_time) || transitDetails.departure_time}
              </span>
              {hasDelay && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">
                  +{transitDetails.delay_minutes} min delay
                </span>
              )}
              {transitDetails.real_time_departure && !hasDelay && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                  On time
                </span>
              )}
            </div>
          )}

          {/* Arrival Time */}
          {transitDetails.arrival_time && (
            <div className="flex items-center space-x-2 mt-1">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">
                Arrives: {formatTimeString(transitDetails.arrival_time) || transitDetails.arrival_time}
              </span>
            </div>
          )}

          {/* Stops Count */}
          {transitDetails.num_stops !== undefined && transitDetails.num_stops > 0 && (
            <div className="text-xs text-gray-500 mt-1">
              {transitDetails.num_stops} stop{transitDetails.num_stops !== 1 ? 's' : ''}
            </div>
          )}
        </div>

        {/* Duration */}
        <div className="text-sm text-gray-600 flex-shrink-0">
          {Math.floor(estimatedTime / 60)}m
        </div>
      </div>

      {/* Service Alerts */}
      {hasAlerts && (
        <div className="space-y-2">
          {transitDetails.service_alerts!.map((alert, index) => (
            <div
              key={index}
              className="flex items-start space-x-2 p-2 bg-yellow-50 border border-yellow-200 rounded-lg"
            >
              <AlertTriangle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                {alert.header && (
                  <div className="text-sm font-medium text-yellow-900">
                    {alert.header}
                  </div>
                )}
                {alert.description && (
                  <div className="text-xs text-yellow-700 mt-0.5">
                    {alert.description}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TransitStep

