# Frontend - Destination AI

React + TypeScript frontend for the Route Recommendation System.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, for custom API URL):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Running

### Development Server
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Configuration

The frontend connects to the backend API at `http://localhost:8000/api/v1` by default. This can be configured via:
- Environment variable: `VITE_API_BASE_URL`
- Vite proxy configuration in `vite.config.ts`
