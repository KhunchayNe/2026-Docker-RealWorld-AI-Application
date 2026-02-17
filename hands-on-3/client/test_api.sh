#!/bin/bash
# test_api.sh - Complete API Testing Script

API_URL="http://localhost:8000"

echo "=================================="
echo "🚀 Oil Price Prediction API Testing"
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "\n${BLUE}1️⃣ Health Check${NC}"
curl -s "$API_URL/" | jq '.'

# Test 2: Generate Sample Data
echo -e "\n${BLUE}2️⃣ Generate Sample Data${NC}"
curl -s -X POST "$API_URL/generate-sample-data" | jq '.'

sleep 2

# Test 3: Check Latest Prices
echo -e "\n${BLUE}3️⃣ Get Latest Prices${NC}"
curl -s "$API_URL/prices/latest" | jq '.'

# Test 4: Add Individual Price
echo -e "\n${BLUE}4️⃣ Add Individual Price${NC}"
curl -s -X POST "$API_URL/prices" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-18",
    "diesel": 33.50,
    "gasohol_95": 43.80,
    "gasohol_91": 41.50,
    "lpg": 21.50
  }' | jq '.'

# Test 5: Train Model for Diesel
echo -e "\n${BLUE}5️⃣ Train Model (Diesel)${NC}"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "retrain": true
  }' | jq '.'

# Test 6: Train Model for Gasohol 95
echo -e "\n${BLUE}6️⃣ Train Model (Gasohol 95)${NC}"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "gasohol_95",
    "retrain": true
  }' | jq '.'

# Test 6b: Train Model for Gasohol 91
echo -e "\n${BLUE}6️⃣b. Train Model (Gasohol 91)${NC}"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "gasohol_91",
    "retrain": true
  }' | jq '.'

# Test 7: Predict Diesel Price (7 days)
echo -e "\n${BLUE}7️⃣ Predict Diesel Price (7 days)${NC}"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "diesel",
    "horizon": 7
  }' | jq '.'

# Test 8: Search Similar Diesel Prices
echo -e "\n${BLUE}8️⃣ Search Similar Diesel Prices (around 32.5)${NC}"
curl -s "$API_URL/search?price=32.5&fuel_type=diesel&limit=5" | jq '.'

# Test 9: Predict Gasohol 95 Price
echo -e "\n${BLUE}9️⃣ Predict Gasohol 95 Price (7 days)${NC}"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "gasohol_95",
    "horizon": 7
  }' | jq '.'

# Test 10: Predict Gasohol 91 Price
echo -e "\n${BLUE}🔟 Predict Gasohol 91 Price (7 days)${NC}"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "fuel_type": "gasohol_91",
    "horizon": 7
  }' | jq '.'

echo -e "\n${GREEN}=================================="
echo "✅ All Tests Completed!"
echo "==================================${NC}"
