# Oil Price Prediction - Web Client

Simple web interface for the Oil Price Prediction API.

## Features

1. **Generate Sample Data** - Create test data in the backend
2. **Train Model** - Train prediction models for different fuel types
3. **Predict Prices** - Get price predictions for next N days
4. **Search Similar Prices** - Find historical prices close to a target value
5. **Add Price Entry** - Manually add price data
6. **Get Latest Prices** - View the most recent price data
7. **Upload Data from EPPO** - Load real data from EPPO CSV URL
8. **Health Check** - Check API status

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Test API with Scripts

### Bash Script

```bash
# Run all tests
./test_api.sh
```

### Python Script

```bash
# Requires: pip install requests
python test_api.py
```

## Manual Testing with curl

```bash
# 1. Health Check
curl http://localhost:8000/

# 2. Generate Sample Data
curl -X POST http://localhost:8000/generate-sample-data

# 3. Train Model
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "retrain": true}'

# 4. Predict Prices
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": "diesel", "horizon": 7}'

# 5. Search Similar Prices
curl "http://localhost:8000/search?price=32.5&fuel_type=diesel&limit=5"

# 6. Get Latest Prices
curl http://localhost:8000/prices/latest
```

## Build for Production

```bash
npm run build
npm run preview
```

## API Proxy Configuration

The Vite dev server proxies requests to the backend:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000` (proxied via `/api`)

## Supported Fuel Types

- `diesel` - Diesel B7
- `gasohol_95` - Gasohol 95
- `gasohol_91` - Gasohol 91
- `e20` - Gasohol E20
- `e85` - Gasohol E85
