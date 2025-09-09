# Deployment Guide

This guide covers deploying the Route Recommendation System to various platforms.

## 🐳 Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- API keys configured

### Docker Setup

1. **Create Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - TRANSLINK_API_KEY=${TRANSLINK_API_KEY}
      - LIME_API_KEY=${LIME_API_KEY}
      - DATABASE_URL=sqlite:///./data/route_recommendation.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

3. **Create nginx.conf**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

4. **Deploy with Docker Compose**
```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. Backend (AWS Elastic Beanstalk)

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB Application**
```bash
eb init vancouver-route-system
```

3. **Create Environment**
```bash
eb create production
```

4. **Set Environment Variables**
```bash
eb setenv GOOGLE_MAPS_API_KEY=your_key
eb setenv OPENWEATHER_API_KEY=your_key
eb setenv DATABASE_URL=postgresql://user:pass@host:port/db
```

5. **Deploy**
```bash
eb deploy
```

#### 2. Frontend (AWS S3 + CloudFront)

1. **Build Frontend**
```bash
cd frontend
npm run build
```

2. **Upload to S3**
```bash
aws s3 sync build/ s3://your-bucket-name
```

3. **Create CloudFront Distribution**
- Origin: S3 bucket
- Default root object: index.html
- Custom error pages: 404 → index.html

#### 3. Database (AWS RDS)

1. **Create RDS Instance**
- Engine: PostgreSQL
- Instance class: db.t3.micro
- Storage: 20GB
- Security group: Allow port 5432

2. **Update DATABASE_URL**
```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

---

### Google Cloud Platform

#### 1. Backend (Cloud Run)

1. **Create Dockerfile** (see Docker section)

2. **Build and Deploy**
```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT-ID/vancouver-routes

# Deploy to Cloud Run
gcloud run deploy vancouver-routes \
  --image gcr.io/PROJECT-ID/vancouver-routes \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Set Environment Variables**
```bash
gcloud run services update vancouver-routes \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_key \
  --set-env-vars OPENWEATHER_API_KEY=your_key
```

#### 2. Frontend (Firebase Hosting)

1. **Install Firebase CLI**
```bash
npm install -g firebase-tools
```

2. **Initialize Firebase**
```bash
cd frontend
firebase init hosting
```

3. **Build and Deploy**
```bash
npm run build
firebase deploy
```

---

### Azure Deployment

#### 1. Backend (Azure App Service)

1. **Create App Service**
```bash
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name vancouver-routes-api \
  --runtime "PYTHON|3.9"
```

2. **Set Environment Variables**
```bash
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name vancouver-routes-api \
  --settings GOOGLE_MAPS_API_KEY=your_key
```

3. **Deploy Code**
```bash
az webapp deployment source config-zip \
  --resource-group myResourceGroup \
  --name vancouver-routes-api \
  --src app.zip
```

#### 2. Frontend (Azure Static Web Apps)

1. **Create Static Web App**
```bash
az staticwebapp create \
  --name vancouver-routes-frontend \
  --resource-group myResourceGroup \
  --source https://github.com/your-username/your-repo \
  --location "Central US" \
  --branch main \
  --app-location "/frontend" \
  --output-location "build"
```

---

## 🚀 Production Considerations

### 1. Environment Variables

**Never hardcode API keys in your code!**

Use environment variables or secret management:

```python
# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")

    class Config:
        env_file = ".env"
```

### 2. Database Configuration

**Production Database Setup:**

```python
# Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@host:port/database

# Or use managed database service
DATABASE_URL=postgresql://user:password@aws-rds-endpoint:5432/database
```

### 3. CORS Configuration

**Update CORS settings for production:**

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "https://www.your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Security Headers

**Add security middleware:**

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)
```

### 5. Rate Limiting

**Implement rate limiting:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/route")
@limiter.limit("10/minute")
async def calculate_route(request: Request, route_request: RouteRequest):
    # Route calculation logic
    pass
```

### 6. Monitoring and Logging

**Add monitoring:**

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### 7. Health Checks

**Implement health checks:**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "database": await check_database_connection(),
            "apis": await check_api_connections()
        }
    }
```

---

## 📊 Performance Optimization

### 1. Caching

**Implement Redis caching:**

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 2. Database Optimization

**Use connection pooling:**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### 3. API Optimization

**Implement request batching:**

```python
async def batch_api_calls(requests):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in requests]
        responses = await asyncio.gather(*tasks)
        return responses
```

---

## 🔒 Security Checklist

- [ ] API keys stored in environment variables
- [ ] HTTPS enabled for all endpoints
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Security headers configured
- [ ] Regular security updates
- [ ] Monitoring and alerting setup

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers
- Implement stateless design
- Use external session storage
- Database read replicas

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Implement caching layers
- Use CDN for static assets

### Microservices
- Split into smaller services
- Use message queues
- Implement service discovery
- Add circuit breakers

---

## 🚨 Monitoring and Alerting

### 1. Application Monitoring
- **Uptime monitoring**: Pingdom, UptimeRobot
- **Performance monitoring**: New Relic, DataDog
- **Error tracking**: Sentry, Rollbar

### 2. Infrastructure Monitoring
- **Server metrics**: CPU, memory, disk usage
- **Database metrics**: Connection pools, query performance
- **API metrics**: Response times, error rates

### 3. Business Metrics
- **Route calculations per day**
- **User engagement metrics**
- **API usage and costs**
- **Sustainability impact**

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to AWS
        run: |
          # Deploy backend
          eb deploy production
          # Deploy frontend
          npm run build
          aws s3 sync build/ s3://your-bucket
```

---

**Remember**: Always test your deployment in a staging environment before going to production!
