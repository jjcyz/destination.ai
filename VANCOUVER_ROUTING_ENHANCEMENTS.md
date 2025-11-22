# Vancouver Real-Time Routing Enhancements

## Current Data Sources ✅

**Already Integrated:**
- ✅ Google Maps API (base routing)
- ✅ TransLink GTFS-RT (real-time transit delays, service alerts)
- ✅ OpenWeather API (weather conditions)
- ✅ Vancouver Open Data (road closures, construction zones)
- ✅ Lime API (bike/scooter availability)
- ✅ Google Maps Traffic API

**Currently Fetched But Not Fully Utilized:**
- ⚠️ Road closures (fetched but not used to modify routes)
- ⚠️ Construction zones (fetched but not used to modify routes)
- ⚠️ Traffic data (fetched but only partially used)

---

## Recommended Enhancements for Vancouver

### 🔴 High Priority (Biggest Impact)

#### 1. **TransLink Real-Time Integration** ⭐⭐⭐⭐⭐
**Current:** You're fetching GTFS-RT but only adding delays to transit steps

**Enhancements:**
- ✅ **Route Selection**: Prefer routes with on-time transit over delayed routes
- ✅ **Alternative Transit Routes**: When a route is delayed, suggest alternative transit routes automatically
- ✅ **Service Alerts Integration**: Filter out routes affected by service disruptions
- ✅ **Bay Selection**: Use GTFS static feed for accurate multi-bay stop selection (you're already doing this!)

**Implementation:**
```python
# Filter routes based on TransLink delays
def filter_delayed_routes(routes, max_delay_minutes=5):
    """Prefer routes with minimal delays."""
    return sorted(routes, key=lambda r: r.max_transit_delay)

# Suggest alternatives when delays exceed threshold
def suggest_alternatives_when_delayed(route, delay_threshold=10):
    """If route has >10min delay, find alternative routes."""
    if route.max_transit_delay > delay_threshold:
        return find_alternative_transit_routes(route)
```

#### 2. **Road Closure & Construction Avoidance** ⭐⭐⭐⭐⭐
**Current:** Data is fetched but routes aren't modified

**Enhancements:**
- ✅ **Route Filtering**: Remove routes that pass through closures/construction
- ✅ **Waypoint Injection**: Add waypoints to Google Maps requests to route around closures
- ✅ **Time-Based Closures**: Handle temporary closures (e.g., events, rush hour restrictions)
- ✅ **Severity-Based Avoidance**: Avoid major closures, warn about minor ones

**Implementation:**
```python
# Filter routes through closures
def filter_routes_with_closures(routes, closures):
    """Remove routes passing through road closures."""
    valid_routes = []
    for route in routes:
        if not route_passes_through_closures(route, closures):
            valid_routes.append(route)
    return valid_routes

# Modify Google Maps request to avoid closures
def add_avoidance_waypoints(origin, destination, closures):
    """Create waypoints to route around closures."""
    waypoints = calculate_avoidance_waypoints(origin, destination, closures)
    return waypoints
```

#### 3. **Weather-Based Route Modification** ⭐⭐⭐⭐
**Current:** Weather adjusts time estimates but doesn't change routes

**Enhancements:**
- ✅ **Route Preference**: In rain/snow, prefer routes with more covered areas (SkyTrain, covered walkways)
- ✅ **Bike Route Safety**: In bad weather, avoid exposed bike routes, prefer protected lanes
- ✅ **Walking Routes**: Prefer routes with more shelter (buildings, covered areas)
- ✅ **Transit Preference**: Increase transit preference in extreme weather

**Implementation:**
```python
def adjust_routes_for_weather(routes, weather):
    """Modify route preferences based on weather."""
    if weather.condition in ["rain", "snow", "extreme"]:
        # Boost routes with more covered segments
        for route in routes:
            covered_score = calculate_covered_segments(route)
            route.score *= (1 + covered_score * 0.2)

        # Prefer transit over walking/biking
        transit_routes = [r for r in routes if has_transit(r)]
        return sorted(transit_routes + routes, key=lambda r: r.score, reverse=True)
```

---

### 🟡 Medium Priority (Significant Improvements)

#### 4. **Vancouver-Specific Traffic Patterns** ⭐⭐⭐⭐
**Enhancements:**
- ✅ **Rush Hour Adjustments**: Use historical + real-time data for Vancouver rush hours
  - Morning rush: 7-9 AM (downtown-bound)
  - Afternoon rush: 4-6 PM (outbound)
- ✅ **Bridge Traffic**: Monitor Lions Gate, Second Narrows, Oak Street Bridge delays
- ✅ **Downtown Core**: Special handling for downtown Vancouver traffic patterns
- ✅ **Event-Based Traffic**: Adjust for Canucks games, concerts at Rogers Arena, etc.

**Data Sources:**
- Google Maps Traffic API (you have this)
- BC Ministry of Transportation (bridge delays)
- City of Vancouver traffic cameras API

**Implementation:**
```python
def get_vancouver_rush_hour_multiplier(datetime, direction):
    """Apply Vancouver-specific rush hour penalties."""
    hour = datetime.hour
    is_morning_rush = 7 <= hour <= 9
    is_afternoon_rush = 16 <= hour <= 18

    if is_morning_rush and direction == "downtown":
        return 1.5  # 50% slower
    elif is_afternoon_rush and direction == "outbound":
        return 1.4  # 40% slower
    return 1.0
```

#### 5. **Bike Infrastructure Integration** ⭐⭐⭐⭐
**Enhancements:**
- ✅ **Bike Lane Network**: Use Vancouver's bike lane data to prefer protected routes
- ✅ **Bike Route Safety Scoring**: Score routes based on bike infrastructure quality
- ✅ **Separated vs Shared Lanes**: Prefer separated bike lanes over shared roads
- ✅ **Bike Route Network**: Use Vancouver's official bike route network data

**Data Sources:**
- City of Vancouver Open Data: Bike Routes
- Strava Heatmap (popular bike routes)
- Bike lane quality data

**Implementation:**
```python
def score_bike_route_safety(route):
    """Score route based on bike infrastructure."""
    score = 0
    for step in route.steps:
        if step.has_separated_bike_lane:
            score += 10
        elif step.has_bike_lane:
            score += 5
        elif step.is_shared_road:
            score += 1
    return score
```

#### 6. **Transit Transfer Optimization** ⭐⭐⭐⭐
**Enhancements:**
- ✅ **Transfer Time Optimization**: Use real-time data to minimize transfer wait times
- ✅ **Transfer Station Selection**: Choose transfer points with better connections
- ✅ **Multi-Modal Transfers**: Optimize bike-transit, walk-transit transfers
- ✅ **Transfer Reliability**: Prefer transfer points with more frequent service

**Implementation:**
```python
def optimize_transit_transfers(route):
    """Optimize transfer points using real-time data."""
    transfers = find_transfers(route)
    for transfer in transfers:
        # Check real-time arrival of connecting route
        next_arrival = get_next_arrival(transfer.stop, transfer.route)
        if next_arrival.wait_time > 10:
            # Find alternative transfer point
            alt_transfer = find_alternative_transfer(transfer)
            if alt_transfer:
                route = modify_route_with_transfer(route, alt_transfer)
    return route
```

#### 7. **SeaBus & West Coast Express Integration** ⭐⭐⭐
**Enhancements:**
- ✅ **SeaBus Schedule Integration**: Use actual SeaBus schedule (not just Google Maps)
- ✅ **West Coast Express**: Integrate WCE schedule for commuter routes
- ✅ **Ferry Wait Times**: Account for SeaBus boarding/wait times
- ✅ **Multi-Modal Connections**: Optimize connections to SeaBus/WCE

**Data Sources:**
- TransLink API (you have this)
- BC Ferries API (for SeaBus-like data)

---

### 🟢 Lower Priority (Nice to Have)

#### 8. **Parking Availability** ⭐⭐⭐
**Enhancements:**
- ✅ **Parking Spot Availability**: For car routes, show parking availability at destination
- ✅ **Parking Cost Integration**: Factor parking costs into route scoring
- ✅ **EV Charging Stations**: For EV routes, prefer routes with charging stations

**Data Sources:**
- Parkopedia API
- City of Vancouver parking data
- PlugShare API (EV charging)

#### 9. **Pedestrian Infrastructure** ⭐⭐
**Enhancements:**
- ✅ **Sidewalk Quality**: Prefer routes with better sidewalks
- ✅ **Accessibility**: Consider wheelchair accessibility, ramps
- ✅ **Pedestrian-Friendly Streets**: Prefer pedestrian-priority streets

**Data Sources:**
- City of Vancouver sidewalk data
- Accessibility mapping data

#### 10. **Event-Based Routing** ⭐⭐
**Enhancements:**
- ✅ **Event Detection**: Detect major events (sports, concerts, festivals)
- ✅ **Event Traffic Avoidance**: Route around event areas
- ✅ **Transit Service Changes**: Account for event-related transit changes

**Data Sources:**
- Eventbrite API
- City of Vancouver events calendar
- TransLink service alerts (you have this)

#### 11. **Air Quality & Health Routes** ⭐⭐
**Enhancements:**
- ✅ **Air Quality Data**: Prefer routes with better air quality
- ✅ **Wildfire Smoke Avoidance**: During wildfire season, prefer indoor routes
- ✅ **Health Impact Scoring**: Score routes based on air quality exposure

**Data Sources:**
- BC Air Quality API
- Environment Canada air quality data

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 weeks)
1. ✅ Road closure avoidance (filter routes)
2. ✅ TransLink delay-based route selection
3. ✅ Weather-based route preference adjustment

### Phase 2: Core Enhancements (2-4 weeks)
4. ✅ Construction zone avoidance with waypoints
5. ✅ Vancouver rush hour traffic adjustments
6. ✅ Bike infrastructure scoring
7. ✅ Transit transfer optimization

### Phase 3: Advanced Features (1-2 months)
8. ✅ SeaBus/WCE integration
9. ✅ Parking availability
10. ✅ Event-based routing
11. ✅ Air quality integration

---

## Data Source Recommendations

### Free/Open Data
- ✅ **City of Vancouver Open Data**: Road closures, construction, bike routes, events
- ✅ **TransLink API**: Real-time transit (you have this)
- ✅ **BC Air Quality**: Air quality data
- ✅ **Environment Canada**: Weather alerts, air quality

### Paid APIs (Consider)
- **Parkopedia API**: Parking availability ($)
- **Strava Heatmap API**: Popular bike/walk routes ($)
- **TomTom Traffic API**: More detailed traffic than Google ($)
- **Here Traffic API**: Alternative to Google Maps traffic ($)

### Custom Data Sources
- **Traffic Camera Feeds**: City of Vancouver traffic cameras
- **Bridge Status**: BC MOT bridge delays
- **Event Calendars**: Rogers Arena, BC Place event schedules

---

## Code Structure Recommendations

```
backend/app/routing/
├── route_filter.py          # Filter routes (closures, delays)
├── route_modifier.py        # Modify routes (waypoints, alternatives)
├── vancouver_specific.py    # Vancouver-specific logic
│   ├── rush_hour.py
│   ├── bike_infrastructure.py
│   ├── transit_transfers.py
│   └── events.py
├── data_integration.py      # Integrate all data sources
└── route_scorer.py          # Enhanced scoring with all factors
```

---

## Next Steps

1. **Start with Phase 1** - Quick wins that provide immediate value
2. **Implement route filtering** - Remove routes through closures
3. **Enhance TransLink integration** - Use delays for route selection
4. **Add weather-based preferences** - Adjust routes for weather

Would you like me to implement any of these enhancements?

