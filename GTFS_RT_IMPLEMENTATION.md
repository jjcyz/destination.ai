# GTFS-RT Implementation Guide

## Overview

GTFS-RT (GTFS Realtime) parsing has been implemented to provide **real-time, accurate transit data** for your Vancouver route planning app. This integrates TransLink's real-time feeds with Google Maps routes.

---

## What Was Implemented

### 1. **GTFS-RT Parser Module** (`backend/app/gtfs_parser.py`)
   - Parses Protocol Buffer feeds from TransLink
   - Extracts trip updates (delays, arrival times)
   - Extracts vehicle positions (live bus/train locations)
   - Extracts service alerts (disruptions, delays)

### 2. **Enhanced TransLink Client** (`backend/app/api_clients.py`)
   - Added parsed GTFS-RT methods:
     - `get_parsed_trip_updates()` - Real-time trip delays
     - `get_parsed_vehicle_positions()` - Live vehicle locations
     - `get_parsed_service_alerts()` - Service disruptions
   - Caching (30-second TTL) to reduce API calls

### 3. **Route Integration** (`backend/app/routing_engine.py`)
   - Real-time delays applied to transit routes
   - Service alerts shown for affected routes
   - Route times adjusted based on actual delays

---

## Installation

Install the required library:

```bash
pip install gtfs-realtime-bindings protobuf
```

Or install all requirements:

```bash
pip install -r backend/requirements.txt
```

---

## How It Works

### Flow:

1. **Route Planning** (Google Maps):
   - User requests route → Google Maps provides transit route
   - Route includes: route number ("99"), stops, scheduled times

2. **Real-Time Enhancement** (TransLink GTFS-RT):
   - Fetch GTFS-RT trip updates feed
   - Parse Protocol Buffer data
   - Match route number with GTFS-RT data
   - Extract delays and apply to route times

3. **Result**:
   - Route shows **actual** arrival times (not just scheduled)
   - Delays are displayed to users
   - Service alerts shown if route is affected

---

## Testing

### Test GTFS-RT Parsing:

```bash
python backend/test_gtfs_rt.py
```

This will:
- Fetch TransLink GTFS-RT feeds
- Parse trip updates, vehicle positions, and alerts
- Show sample data

### Test Full Integration:

Make a route request through your API - transit routes will now include:
- `delay_minutes` - Real-time delay
- `is_delayed` - Whether route is delayed
- `real_time_departure` - Actual departure time
- `service_alerts` - Any alerts affecting the route

---

## Data Structure

### Trip Updates Include:
```python
{
    "route_id": "99",
    "trip_id": "12345",
    "stop_time_updates": [
        {
            "stop_id": "12345",
            "arrival": {
                "delay": 180,  # seconds
                "time": 1234567890  # Unix timestamp
            }
        }
    ]
}
```

### Route Transit Details (Enhanced):
```python
{
    "line": "99 B-Line",
    "short_name": "99",
    "departure_time": "2:45 PM",
    "delay_minutes": 3,  # Real-time delay
    "is_delayed": True,
    "real_time_departure": "2024-01-15T14:48:00",
    "service_alerts": [
        {
            "header": "Route 99 delayed",
            "description": "Due to traffic",
            "effect": "DELAY"
        }
    ]
}
```

---

## Matching Google Maps with GTFS-RT

**Challenge:** Google Maps uses route names like "99 B-Line", GTFS-RT uses route IDs like "99"

**Solution:**
- Extract `short_name` from Google Maps route (e.g., "99")
- Match with GTFS-RT `route_id`
- Find stop matches using stop IDs or names

**Note:** Stop ID matching may require GTFS static feed for complete mapping. Current implementation uses route matching which works for most cases.

---

## Performance

- **Caching:** GTFS-RT data cached for 30 seconds
- **Async:** All API calls are asynchronous
- **Fallback:** If GTFS-RT fails, falls back to Google Maps scheduled times

---

## Limitations & Future Improvements

### Current Limitations:
1. **Stop ID Matching:** Google Maps doesn't always provide GTFS stop IDs
   - **Solution:** Could use GTFS static feed to map stop names to IDs

2. **Route Matching:** Relies on route short name matching
   - Works for most routes (99, 4, etc.)
   - May need refinement for SkyTrain lines

### Future Enhancements:
1. **GTFS Static Feed Integration:**
   - Download TransLink GTFS static feed
   - Map stop names to stop IDs
   - More accurate matching

2. **Vehicle Tracking:**
   - Show live bus/train positions on map
   - "Next bus is 2 stops away"

3. **Predictive Delays:**
   - Analyze historical delays
   - Predict future delays

---

## API Usage

### In Your Code:

```python
from app.api_clients import TransLinkClient

client = TransLinkClient()

# Get real-time trip updates
trip_updates = await client.get_parsed_trip_updates()

# Get arrival info for specific stop
arrival_info = await client.get_stop_arrival_info(
    route_id="99",
    stop_id="12345"
)

# Get all delays for a route
delays = await client.get_route_real_time_delays("99")
```

---

## Troubleshooting

### "gtfs-realtime-bindings not installed"
```bash
pip install gtfs-realtime-bindings
```

### "No trip updates found"
- Check TransLink API key is valid
- Verify API endpoint is accessible
- Check network connection

### "Could not match route"
- Route short name may not match GTFS-RT route_id
- Check route name format (e.g., "99" vs "099")

---

## Summary

✅ **GTFS-RT parsing implemented**
✅ **Real-time delays integrated with routes**
✅ **Service alerts displayed**
✅ **Caching for performance**
✅ **Graceful fallback if GTFS-RT unavailable**

Your app now provides **real-time, accurate transit data** for Vancouver routes! 🚌

