# 🛢️ Oil Price Prediction Application

Full-stack AI application for predicting oil prices using time series forecasting and vector similarity search.

## 🚀 Quick Start with Docker

```bash
# Start all services
docker compose up --build

# Access the application
open http://localhost
```

### What You Get
- 🎯 **Web Interface**: http://localhost
- 📊 **API**: http://localhost/api/
- 📖 **API Docs**: http://localhost/api/docs
- 🔧 **Traefik Dashboard**: http://traefik.localhost
- 🗄️ **Qdrant UI**: http://qdrant.localhost

## 📋 Features

- **Generate Sample Data**: Create test oil price data
- **Train Models**: ARIMA/SARIMA for different fuel types
- **Predict Prices**: Forecast future prices with confidence intervals
- **Similarity Search**: Find historical prices using vector embeddings
- **Real-time Updates**: Hot-reload for both frontend and backend
- **Vector Database**: Qdrant for similarity search
- **Multiple Fuel Types**: Diesel, Gasohol 95, Gasohol 91, E20, E85

## 🏗️ Architecture

```
React (Vite)  ←→  FastAPI (Python)  ←→  Qdrant (Vector DB)
     ↓                    ↓                    ↓
   :5173               :8000                :6333
     ↓                    ↓
  Traefik Proxy (:80)
     ↓
  Browser (:80)
```

## 🛠️ Tech Stack

### Frontend
- **React 19** + **TypeScript**
- **Vite** for dev server with HMR
- **CSS** for styling

### Backend
- **FastAPI** (Python 3.12)
- **Uvicorn** ASGI server
- **Pydantic** for validation

### AI/ML
- **statsmodels** for ARIMA/SARIMA
- **scikit-learn** for preprocessing
- **sentence-transformers** for embeddings
- **Qdrant** for vector search

### Infrastructure
- **Docker** + **Docker Compose**
- **Traefik** reverse proxy
- **Compose Watch** for hot-reload

## 📦 Quick Commands

### Development
```bash
# Start all services
docker compose up --build

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend
```

### Testing
```bash
# Generate sample data
curl -X POST http://localhost/api/generate-sample-data

# Train model
curl -X POST http://localhost/api/train \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "retrain": true}'

# Predict prices
curl -X POST http://localhost/api/predict \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "horizon": 7}'

# Search similar prices
curl "http://localhost/api/search?price=32.5&fuel_type=diesel&limit=5"

# Get latest prices
curl http://localhost/api/prices/latest
```

## 📁 Project Structure

```
hands-on-3/
├── client/                 # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main application
│   │   ├── App.css        # Styles
│   │   └── main.tsx       # Entry point
│   ├── vite.config.ts     # Vite configuration
│   └── package.json       # Dependencies
│
├── backend/               # FastAPI backend
│   ├── main.py            # FastAPI app
│   ├── models/            # ML models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utilities
│   └── requirements.txt   # Python dependencies
│
├── compose.yaml           # Docker Compose config
├── Dockerfile             # Multi-stage build
├── DOCKER.md              # Detailed Docker guide
└── DOCKER_STATUS.md       # Current setup status
```

## 🔧 Configuration

### Environment Variables

Backend automatically connects to:
- `QDRANT_HOST=qdrant`
- `QDRANT_PORT=6333`

### Port Mappings

- **80**: Traefik proxy (main access)
- **8000**: Backend API (direct access)
- **5173**: Frontend (direct access)
- **6333**: Qdrant (direct access)
- **8080**: Traefik dashboard

## 🔍 Troubleshooting

### Containers not starting?
```bash
docker compose down -v    # Remove volumes
docker compose up --build # Rebuild and start
```

### Frontend shows 502?
Wait 10-20 seconds for backend to fully start (downloads ML models on first run)

### API returns errors?
Check logs: `docker compose logs backend`

## 📖 Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker guide
- [DOCKER_STATUS.md](DOCKER_STATUS.md) - Setup status and troubleshooting
- [client/README.md](client/README.md) - Frontend documentation
- [backend/README.md](backend/README.md) - Backend API documentation

## 🎯 Supported Fuel Types

- `diesel` - Diesel B7
- `gasohol_95` - Gasohol 95
- `gasohol_91` - Gasohol 91
- `e20` - Gasohol E20
- `e85` - Gasohol E85

## 🚀 Production Deployment

For production, use the `final` Docker stage:

```bash
docker build --target final -t oil-price-app:prod .
docker run -p 8000:8000 oil-price-app:prod
```

## 📝 License

Educational use only.

## 🤝 Contributing

This is a course project for learning Docker and AI applications.

---

**Status**: ✅ All services operational via Traefik at http://localhost
