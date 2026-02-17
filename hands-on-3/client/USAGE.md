# Oil Price Predictor - Usage Guide

## New Features

### Success Notifications
- ✅ Visual success messages for each operation
- Context-aware messages showing details (e.g., record counts, sample sizes)
- Green notification with slide-in animation

### Enhanced Loading States
- 🔵 Blue loading indicator with spinning animation
- Clear "Processing request..." message
- Non-blocking UI during API calls

### Improved Error Handling
- ❌ Clear error messages with red indicator
- Displays API error details when available
- Validation for required inputs (e.g., price entries)

### Better Response Display
- **Predictions**: Table format showing day, date, predicted price, and confidence intervals
- **Latest Prices**: Clean card layout for each fuel type with dates
- **Similar Prices**: Shows date, price, and similarity percentage
- **Other responses**: Formatted JSON with syntax highlighting

## Quick Start

### 1. Start the Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd client
npm run dev
```

### 3. Open Browser
Navigate to `http://localhost:5173`

## Recommended Workflow

### Step 1: Generate Sample Data
1. Click "Generate Sample Data" button
2. Success message shows number of records added

### Step 2: Train Models
1. Select fuel type (Diesel, Gasohol 95, etc.)
2. Check "Retrain Model" if needed
3. Click "Train Model"
4. Success message shows training metrics

### Step 3: Make Predictions
1. Select fuel type
2. Set horizon (number of days to predict)
3. Click "Predict Prices"
4. Results displayed in table format with:
   - Current price
   - Predicted price for each day
   - Lower and upper bounds (confidence interval)

### Step 4: Search Similar Prices
1. Enter target price
2. Select fuel type
3. Set limit (number of results)
4. Click "Search"
5. Results show similar historical dates with similarity scores

### Step 5: Add Price Entry
1. Select date (defaults to today)
2. Enter prices for one or more fuel types
3. Click "Add Price"
4. Success message confirms entry added

### Step 6: Check Latest Prices
- Click "Get Latest Prices" to see current prices for all fuel types

### Step 7: Upload Real Data
- Edit CSV URL if needed
- Click "Load from EPPO" to fetch real data

### Step 8: Health Check
- Click "Check API Health" to verify backend is running

## Color Coding

- 🟢 **Green**: Success, completed operations
- 🔵 **Blue**: Loading, processing
- 🔴 **Red**: Errors, validation failures

## Tips

1. **Train before predicting**: Always train the model before making predictions
2. **Start with sample data**: Use "Generate Sample Data" to quickly test the system
3. **Check predictions table**: Review the full prediction table for confidence intervals
4. **Use similar prices**: Find historical patterns with the search feature
5. **Add real data**: Upload EPPO data for real-world predictions

## API Response Examples

### Prediction Response
```
Current Price: ฿32.5
Fuel Type: diesel

Predictions:
Day 1: ฿32.45 (31.89 - 33.01)
Day 2: ฿32.52 (31.96 - 33.08)
Day 3: ฿32.48 (31.92 - 33.04)
...
```

### Latest Prices Response
```
diesel: ฿32.5 (2026-02-17)
gasohol_95: ฿42.8 (2026-02-17)
gasohol_91: ฿40.5 (2026-02-17)
```

### Similar Prices Response
```
2026-02-16: ฿32.48 (similarity: 98.5%)
2026-02-15: ฿32.52 (similarity: 97.8%)
2026-02-14: ฿32.45 (similarity: 96.2%)
```

## Troubleshooting

### "API Error" message
- Check backend is running on port 8000
- Check browser console for detailed error

### "Please enter at least one fuel price"
- Enter at least one price when adding price entries

### Loading spinner doesn't stop
- Check network connection
- Verify backend is responding
- Refresh the page and try again

### Empty results
- Ensure data has been generated or uploaded
- Train the model before predicting
- Check the correct fuel type is selected
