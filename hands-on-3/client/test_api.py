import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    print("1. Health Check")
    r = requests.get(f"{API_URL}/")
    print(json.dumps(r.json(), indent=2))

def test_generate_data():
    print("\n2. Generate Sample Data")
    r = requests.post(f"{API_URL}/generate-sample-data")
    print(json.dumps(r.json(), indent=2))

def test_add_price():
    print("\n3. Add Price")
    data = {
        "date": "2026-02-18",
        "diesel": 33.50,
        "gasohol_95": 43.80,
        "gasohol_91": 41.50
    }
    r = requests.post(f"{API_URL}/prices", json=data)
    print(json.dumps(r.json(), indent=2))

def test_train():
    print("\n4. Train Model")
    data = {"fuel_type": "diesel", "retrain": True}
    r = requests.post(f"{API_URL}/train", json=data)
    print(json.dumps(r.json(), indent=2))

def test_predict():
    print("\n5. Predict Prices")
    data = {"fuel_type": "diesel", "horizon": 7}
    r = requests.post(f"{API_URL}/predict", json=data)
    result = r.json()
    print(f"Current: {result['current_price']}")
    print(f"Predictions: {len(result['predictions'])} days")
    for p in result['predictions'][:3]:
        print(f"  Day {p['day']}: {p['predicted_price']} ({p['lower_bound']}-{p['upper_bound']})")

def test_search():
    print("\n6. Search Similar Prices")
    r = requests.get(f"{API_URL}/search", params={"price": 32.5, "fuel_type": "diesel", "limit": 5})
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    test_health()
    test_generate_data()
    test_add_price()
    test_train()
    test_predict()
    test_search()
    print("\n✅ All tests completed!")
