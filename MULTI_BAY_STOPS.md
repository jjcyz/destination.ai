# Multi-Bay Stop Handling

## Problem

Many transit stops have multiple "bays" (loading areas), especially at major exchanges:
- **UBC Exchange** has 11 bays (Bay 1-11, plus unloading)
- **Commercial-Broadway Station** has multiple bays
- **Metrotown Station** has multiple bays

When Google Maps provides a stop name like "UBC Exchange" without specifying the bay, we need to determine which bay to use for real-time data lookup.

---

## Current Solution

### Strategy

1. **Find All Matching Stops**
   - When given "UBC Exchange", find all stops matching that name
   - This includes: Bay 1, Bay 2, Bay 3, ..., Bay 11, Unloading Only

2. **Prefer Station Stops**
   - If there's a station stop (location_type=1), prefer it over bay stops
   - Station stops represent the entire station, not individual bays

3. **Try All Matching Stops for Real-Time Data**
   - When looking up GTFS-RT trip updates, try all matching stop IDs
   - This ensures we find real-time data even if Google Maps doesn't specify the bay
   - First match wins (the bay that actually has the route)

### Example: UBC Exchange

```
Google Maps says: "UBC Exchange"
GTFS has: 11 stops (Bay 1-11, Unloading)

1. Find all matching: [Bay 1, Bay 2, ..., Bay 11, Unloading]
2. No station stop, so use bay stops
3. When looking up Route 99 real-time data:
   - Try stop_id for Bay 1 → No match
   - Try stop_id for Bay 2 → No match
   - Try stop_id for Bay 9 → ✅ Found! Route 99 uses Bay 9
   - Return real-time data for Bay 9
```

---

## Implementation

### Code Flow

```python
# 1. Get all matching stops
all_stops = gtfs_static.get_all_stops_by_name("UBC Exchange")
# Returns: [Bay 1, Bay 2, ..., Bay 11]

# 2. Select best stop (prefer station, then first bay)
selected = gtfs_static.get_stop_id_by_name("UBC Exchange", prefer_station=True)
# Returns: Bay 9 (first match)

# 3. When looking up real-time data, try all stops
stop_ids_to_try = [s.stop_id for s in all_stops]
for stop_id in stop_ids_to_try:
    if stop_id in gtfs_rt_trip_updates:
        return real_time_data  # Found it!
```

### Key Methods

**`get_all_stops_by_name(stop_name)`**
- Returns all stops matching the name
- Useful for multi-bay stops

**`get_stop_id_by_name(stop_name, route_id=None, prefer_station=True)`**
- Returns single best stop ID
- Prefers station stops over bay stops
- Can accept route_id for future route-based selection

**`_select_best_stop(stops, route_id, prefer_station)`**
- Selects best stop from multiple matches
- Currently prefers stations, then first match
- TODO: Route-based selection

---

## Future Improvements

### 1. Route-Based Bay Selection

Use `trips.txt` and `stop_times.txt` to determine which bay serves which route:

```python
# Load trips.txt and stop_times.txt
# Map: route_id → trip_id → stop_id
# When given route_id + stop_name, find exact bay
```

**Benefits:**
- More accurate bay selection
- Know exactly which bay Route 99 uses at UBC Exchange

**Requires:**
- Parsing `trips.txt` and `stop_times.txt`
- Building route → bay mapping

### 2. Location-Based Selection

Use coordinates to find closest bay:

```python
# Google Maps provides stop coordinates
# Find closest bay to those coordinates
closest_bay = find_stop_by_location(lat, lng, radius=50)
```

**Benefits:**
- Works even if stop name doesn't match exactly
- More robust matching

### 3. Try All Bays (Current Implementation)

When looking up real-time data, try all matching stops:

```python
# Try all bays until we find one with real-time data
for bay_stop_id in all_bay_stop_ids:
    real_time_data = lookup_gtfs_rt(route_id, bay_stop_id)
    if real_time_data:
        return real_time_data
```

**Benefits:**
- Works even if we don't know which bay
- Finds real-time data regardless of bay selection

**Current Status:** ✅ **Implemented**

**Example:**
```python
# Route 99 at UBC Exchange
# System knows Route 99 uses Bay 7 (from trips.txt + stop_times.txt)
selected_bay = get_stop_id_by_name("UBC Exchange", route_id="6641")
# Returns: Bay 7 (correct bay for Route 99!)
```

---

## Testing

Run the test script to see how multi-bay stops are handled:

```bash
python backend/test_multi_bay_stops.py
```

**Output shows:**
- All matching stops found
- Which stop was selected
- Stop type (Station vs Bay)

---

## Summary

**Current Approach:**
1. ✅ Find all matching stops
2. ✅ Prefer station stops
3. ✅ Try all matching stops when looking up real-time data

**Works Well For:**
- Stops with station entries (Commercial-Broadway, Metrotown)
- Multi-bay stops where any bay works (UBC Exchange)

**Could Be Improved:**
- Route-specific bay selection (requires trips.txt parsing)
- Location-based bay selection
- Better bay prioritization

**Bottom Line:** The current implementation handles multi-bay stops by trying all matching stops when looking up real-time data, which ensures we find the correct bay even if Google Maps doesn't specify it.

