# Backend - Destination AI

FastAPI backend for the Route Recommendation System.

## Structure

```
backend/
├── app/              # Main application package
│   ├── models.py     # Pydantic models
│   ├── main.py       # FastAPI application
│   ├── config.py     # Configuration and settings
│   ├── api_clients.py # External API clients
│   ├── routing_engine.py # Route calculation engine
│   ├── graph_builder.py  # Graph construction
│   ├── gamification.py   # Gamification system
│   └── demo.py       # Demo data provider
├── cli.py            # Command-line interface
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root (not in backend/) with your API keys:
```env
GOOGLE_MAPS_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
TRANS
```

## Running

### Development Server
```bash
# From project root
python -m backend.app.main

# Or using uvicorn directly
uvicorn backend.app.main:app --reload
```

### CLI Tool
```bash
# From project root
python backend/cli.py --help
python backend/cli.py --origin "vancouver downtown" --destination "ubc"
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

![CI](https://github.com/YOUR_USERNAME/destination.ai/workflows/CI/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/destination.ai/workflows/Deploy/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/destination.ai/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/destination.ai)

