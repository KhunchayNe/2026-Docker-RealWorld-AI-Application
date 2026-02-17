# API Reference - Backend Endpoints

## Add Price Entry
**POST** `/prices`

### Request Body
```json
{
  "date": "2026-02-18",
  "diesel": 33.50,
  "gasohol_95": 43.80,
  "gasohol_91": 41.50,
  "gasohol_e20": 39.20,
  "diesel_b7": 33.00,
  "lpg": 21.50
}
```

### Required Fields
- `date` - Must be a valid date string (YYYY-MM-DD format)
- At least one fuel price field

### Fuel Price Fields (at least one required)
- `diesel` - Diesel price
- `gasohol_95` - Gasohol 95 price
- `gasohol_91` - Gasohol 91 price
- `gasohol_e20` - E20 price
- `diesel_b7` - Diesel B7 price
- `lpg` - LPG price

### Example Valid Requests
```json
// Only diesel
{ "date": "2026-02-18", "diesel": 33.50 }

// Multiple fuels
{ "date": "2026-02-18", "diesel": 33.50, "gasohol_95": 43.80 }

// All fuels
{
  "date": "2026-02-18",
  "diesel": 33.50,
  "gasohol_95": 43.80,
  "gasohol_91": 41.50,
  "gasohol_e20": 39.20,
  "diesel_b7": 33.00,
  "lpg": 21.50
}
```

### Error Response
```json
{
  "detail": "'date'"
}
```
This error occurs when:
- `date` field is missing
- `date` is empty string
- `date` is invalid format

### Success Response
```json
{
  "status": "success",
  "date": "2026-02-18"
}
```

---

## Other Endpoints

### Generate Sample Data
**POST** `/generate-sample-data`

Creates sample price data for testing.

### Train Model
**POST** `/train`

### Request Body
```json
{
  "fuel_type": "diesel",
  "retrain": true
}
```

### Valid Fuel Types
- `diesel`
- `gasohol_95`
- `gasohol_91`
- `e20`
- `e85`

### Predict Prices
**POST** `/predict`

### Request Body
```json
{
  "fuel_type": "diesel",
  "horizon": 7
}
```

- `fuel_type` - Fuel type to predict
- `horizon` - Number of days to predict (1-30)

### Search Similar Prices
**GET** `/search`

### Query Parameters
- `price` - Target price (e.g., 32.5)
- `fuel_type` - Fuel type to search
- `limit` - Number of results to return (default: 5)

### Example
```
GET /search?price=32.5&fuel_type=diesel&limit=5
```

### Get Latest Prices
**GET** `/prices/latest`

Returns the most recent price for all fuel types.

### Health Check
**GET** `/`

Returns API status and health information.

---

## Common Errors

### Missing Date
```json
{ "detail": "'date'" }
```
**Solution**: Ensure `date` field is present and not empty

### Invalid Fuel Type
```json
{ "detail": "Invalid fuel type" }
```
**Solution**: Use valid fuel types: diesel, 95, 91, e20, e85

### No Prices Entered
```json
{ "detail": "At least one fuel price required" }
```
**Solution**: Provide at least one fuel price value

### Model Not Trained
```json
{ "detail": "Model not trained for fuel_type: diesel" }
```
**Solution**: Train the model first using `/train` endpoint

---

## Testing with curl

### Add Price
```bash
curl -X POST http://localhost:8000/prices \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-18",
    "diesel": 33.50,
    "gasohol_95": 43.80
  }'
```

### Train Model
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "retrain": true
  }'
```

### Predict Prices
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "horizon": 7
  }'
```
