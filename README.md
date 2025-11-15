# Destination AI

Preview: https://destination-ai.vercel.app/ [API KEYS REQUIRED]

An AI-powered multi-modal route recommendation system for Vancouver, Canada that provides sustainable transportation options with real-time data integration and gamification features.

## Quick Start

```bash
Backend:
   source venv/bin/activate
   python3 -m app.main

Frontend:
   cd frontend
   npm run dev
```

**Access the application**
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - API Health Check: http://localhost:8000/health

## Features

- **Multi-Modal Routing**: Supports walking, biking, scooters, cars, buses, SkyTrain, SeaBus, and West Coast Express
- **Real-Time Data Integration**:
  - Google Maps Traffic API
  - TransLink Public Transit API
  - Lime Bike/Scooter Sharing API
  - OpenWeatherMap Weather API
  - City of Vancouver Open Data
- **AI-Powered Optimization**: A* algorithm with dynamic edge costs
- **Route Preferences**: Fastest, safest, energy-efficient, scenic, healthy, and cheapest options
- **Gamification**: Points, achievements, badges, and leaderboards for sustainable choices
- **Interactive Web Interface**: Modern React frontend with map visualization
- **CLI Interface**: Command-line tool for testing and development


## API Setup

### Required API Keys

#### 1. Google Maps API
- **Purpose**: Traffic data, elevation, geocoding, directions
- **Setup**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a new project or select existing
  3. Enable the following APIs (only these 3 are actually used):
     - **Directions API** ⭐ (for route calculation and traffic data)
     - **Geocoding API** ⭐ (for address to coordinates conversion)
     - **Elevation API** ⭐ (for elevation/slope data)
  4. Create credentials (API Key)
  5. Set `GOOGLE_MAPS_API_KEY` in your `.env` file

  **Note:** See `GOOGLE_MAPS_API_SETUP.md` for detailed setup instructions.

#### 2. OpenWeatherMap API
- **Purpose**: Weather conditions for route optimization
- **Setup**:
  1. Go to [OpenWeatherMap API](https://openweathermap.org/api)
  2. Sign up for a free account
  3. Get your API key from the dashboard
  4. Set `OPENWEATHER_API_KEY` in your `.env` file

#### 3. TransLink API (Optional)
- **Purpose**: Vancouver public transit data
- **Setup**:
  1. Go to [TransLink Developer Portal](https://developer.translink.ca/)
  2. Register for an account
  3. Request API access
  4. Set `TRANSLINK_API_KEY` in your `.env` file

#### 4. Lime API (Optional)
- **Purpose**: Bike/scooter sharing availability
- **Setup**:
  1. Contact Lime for API access
  2. Set `LIME_API_KEY` in your `.env` file

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
TRANSLINK_API_KEY=your_translink_api_key_here
LIME_API_KEY=your_lime_api_key_here

# Database
DATABASE_URL=sqlite:///./route_recommendation.db

# Application settings
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Gamification settings
SUSTAINABILITY_POINTS_BIKE=10
SUSTAINABILITY_POINTS_WALK=15
SUSTAINABILITY_POINTS_TRANSIT=8
SUSTAINABILITY_POINTS_CAR=0
```

## Usage

### Web Interface

1. **Route Planning**: Enter origin and destination, select preferences and transport modes
2. **Map Visualization**: View routes on an interactive map with different layers
3. **Route Comparison**: Compare multiple route options with detailed metrics
4. **Gamification**: Track sustainability points, achievements, and badges

### CLI Interface

```bash
# Interactive mode
python cli.py --interactive

# Direct route calculation
python cli.py --origin "vancouver downtown" --destination "stanley park" --preferences fastest safest

# Help
python cli.py --help
```

### API Usage

#### Calculate Routes
```bash
curl -X POST "http://localhost:8000/api/v1/route" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 49.2827, "lng": -123.1207},
    "destination": {"lat": 49.3043, "lng": -123.1443},
    "preferences": ["fastest", "safest"],
    "transport_modes": ["walking", "biking", "bus"]
  }'
```

#### Get Gamification Data
```bash
# Get achievements
curl "http://localhost:8000/api/v1/gamification/achievements"

# Get leaderboard
curl "http://localhost:8000/api/v1/gamification/leaderboard"
```

## Architecture

### Backend Components

- **Models** (`app/models.py`): Pydantic models for data validation
- **API Clients** (`app/api_clients.py`): External service integrations
- **Graph Builder** (`app/graph_builder.py`): Street network and transit graph construction
- **Routing Engine** (`app/routing_engine.py`): A* algorithm implementation
- **Gamification** (`app/gamification.py`): Points, achievements, and badges system
- **Main App** (`app/main.py`): FastAPI application with REST endpoints

### Frontend Components

- **React App**: Modern web interface with TypeScript
- **Map Integration**: Leaflet maps with route visualization
- **State Management**: Context API for route and user data
- **API Service**: Axios-based HTTP client
- **Responsive Design**: Tailwind CSS styling

### Data Flow

1. **User Input**: Origin, destination, preferences, transport modes
2. **Graph Building**: Construct routing graph with real-time data
3. **Route Calculation**: A* algorithm with dynamic edge costs
4. **Route Optimization**: Multiple preference-based routes
5. **Gamification**: Calculate rewards and update user stats
6. **Response**: JSON with routes, alternatives, and metadata

## Gamification System

### Sustainability Points
- **Walking**: 15 points/km
- **Biking**: 10 points/km
- **Public Transit**: 8 points/km
- **Scooter**: 8 points/km
- **Car**: 0 points/km

### Achievements
- **First Steps**: Complete your first sustainable route
- **Eco Commuter**: Complete 10 routes without using a car
- **Bike Champion**: Bike a total of 50km
- **Multi-Modal Master**: Use 5 different transport modes
- **Sustainability Hero**: Earn 1000 sustainability points

### Badges
- **Eco Warrior** (Rare): Complete a high-sustainability route without a car
- **Speed Demon** (Common): Complete a route in under 30 minutes
- **Explorer** (Epic): Use 3 or more transport modes in a single route
- **Carbon Crusher** (Legendary): Save 10kg of CO2 emissions

### CLI Testing
```bash
# Test route calculation
python cli.py --origin "vancouver downtown" --destination "ubc" --preferences fastest

# Test interactive mode
python cli.py --interactive
```

### Adding New Features

1. **New Transport Mode**:
   - Add to `TransportMode` enum in `models.py`
   - Update speed mappings in `routing_engine.py`
   - Add API integration in `api_clients.py`
   - Update frontend components

2. **New Route Preference**:
   - Add to `RoutePreference` enum in `models.py`
   - Implement cost function in `routing_engine.py`
   - Update frontend form and display

3. **New Gamification Feature**:
   - Add to `gamification.py`
   - Update API endpoints in `main.py`
   - Add frontend components

**Built with ❤️ for sustainable transportation in Vancouver**
