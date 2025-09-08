# Quick Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+

## Installation

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys (optional for demo)
   ```

4. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Running the System

1. **Start the backend:**
   ```bash
   source venv/bin/activate
   python -m uvicorn app.main:app --reload
   ```

2. **Start the frontend (in another terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application:**
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## CLI Interface

```bash
source venv/bin/activate
python cli.py --interactive
```

## API Keys (Optional)

The system works without API keys using mock data. To use real data, add your keys to `.env`:
- Google Maps API
- OpenWeatherMap API
- TransLink API (Vancouver transit)
- Lime API (bike/scooter sharing)
