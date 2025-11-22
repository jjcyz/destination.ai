# Destination AI

AI-powered multi-modal route recommendation system for Vancouver with real-time data integration and gamification.

**Preview:** https://destination-ai.vercel.app/

## Status Badges
![CI](https://github.com/jjcyz/destination.ai/workflows/CI/badge.svg)
![Deploy](https://github.com/jjcyz/destination.ai/workflows/Deploy/badge.svg)
[![codecov](https://codecov.io/gh/jjcyz/destination.ai/branch/main/graph/badge.svg)](https://codecov.io/gh/jjcyz/destination.ai)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run server
python -m backend.app.main
# Or: uvicorn backend.app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### CLI

```bash
python backend/cli.py --origin "vancouver downtown" --destination "ubc"
```

**Access:**
- Web: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Features

- **Multi-Modal Routing**: Walking, biking, scooters, cars, buses, SkyTrain, SeaBus, West Coast Express
- **Real-Time Data**: Google Maps, TransLink, OpenWeatherMap, Vancouver Open Data
- **AI Optimization**: A* algorithm with dynamic edge costs
- **Route Preferences**: Fastest, safest, eco-friendly, scenic, healthy, cheapest
- **Gamification**: Points, achievements, badges, leaderboards

## Configuration

Copy `env.example` to `.env` and add your API keys:

```env
GOOGLE_MAPS_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
TRANSLINK_API_KEY=your_key_here
LIME_API_KEY=your_key_here       # Optional
```

**Note:** The system works without API keys using demo data.

## Project Structure

```
destination.ai/
├── backend/          # Python FastAPI backend
│   ├── app/         # Application code
│   └── cli.py       # CLI tool
├── frontend/         # React TypeScript frontend
│   └── src/         # Source code
└── .env             # Environment variables
```

## API Usage

### Calculate Routes

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

## Documentation

- **Backend:** See `backend/README.md`
- **Frontend:** See `frontend/README.md`

## Data Flow

```
Backend (GTFS-RT)
  ↓
Route Calculation
  ↓
transit_details with:
  - delay_minutes
  - is_delayed
  - service_alerts
  ↓
Frontend API Response
  ↓
RouteContext
  ↓
AlternativeRoutes Component
  ↓
TransitStep Component (displays transit details)
  ↓
RealTimePanel (extracts delays/alerts)

##GTFS static feed
   - Stops: 5000+
   - Routes: 200+

##WISHLIST
- [ ] Search business names
- [ ] Add "Use Current Location" button
- [ ] Add Saved locations section: Home, School, and other customizables
### Error Boundary
- [ ] Integrate with Sentry for error tracking
- [ ] Add error reporting form
- [ ] Track error frequency and types
