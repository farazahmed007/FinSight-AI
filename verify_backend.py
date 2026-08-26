import requests
import json
import sys

BASE_URL = 'http://localhost:5000/api'
TOKEN = 'dev-token-123'
HEADERS = {'Authorization': f'Bearer {TOKEN}'}

results = {"passed": 0, "failed": 0, "errors": []}

def check(name, condition, error_msg=""):
    if condition:
        print(f"PASS: {name}")
        results["passed"] += 1
    else:
        print(f"FAIL: {name} - {error_msg}")
        results["failed"] += 1
        results["errors"].append(f"{name}: {error_msg}")

try:
    # 1. Health
    res = requests.get(f"{BASE_URL}/health")
    check("Health check (no auth)", res.status_code == 200 and res.json().get('status') == 'healthy', f"Status: {res.status_code}, Body: {res.text}")

    # 2. Auth missing
    res = requests.get(f"{BASE_URL}/transactions")
    check("Auth missing returns 401", res.status_code == 401, f"Status: {res.status_code}")

    # 3. Invalid auth token
    res = requests.get(f"{BASE_URL}/transactions", headers={'Authorization': 'Bearer invalid'})
    check("Invalid token returns 401", res.status_code == 401, f"Status: {res.status_code}")

    # 4. Malformed auth header
    res = requests.get(f"{BASE_URL}/transactions", headers={'Authorization': 'invalid'})
    check("Malformed header returns 401", res.status_code == 401, f"Status: {res.status_code}")

    # 5. Transactions
    res = requests.get(f"{BASE_URL}/transactions", headers=HEADERS)
    check("Get transactions", res.status_code == 200 and isinstance(res.json(), list), f"Status: {res.status_code}, Body: {res.text[:100]}")

    # 6. Analytics summary
    res = requests.get(f"{BASE_URL}/analytics/summary", headers=HEADERS)
    check("Analytics summary", res.status_code == 200 and 'net_savings' in res.json(), f"Status: {res.status_code}, Body: {res.text[:100]}")

    # 7. Analytics categories
    res = requests.get(f"{BASE_URL}/analytics/categories?days=30", headers=HEADERS)
    check("Analytics categories", res.status_code == 200 and isinstance(res.json(), dict), f"Status: {res.status_code}")

    # 8. Analytics monthly
    res = requests.get(f"{BASE_URL}/analytics/monthly", headers=HEADERS)
    check("Analytics monthly", res.status_code == 200 and isinstance(res.json(), list), f"Status: {res.status_code}")

    # 9. Forecast (food)
    res = requests.get(f"{BASE_URL}/forecast/food", headers=HEADERS)
    check("Forecast (food)", res.status_code == 200 and 'forecast_values' in res.json(), f"Status: {res.status_code}")
    print("Example Forecast (food):", json.dumps(res.json(), indent=2)[:500])

    # 10. Forecast invalid category fallback
    res = requests.get(f"{BASE_URL}/forecast/invalid_cat", headers=HEADERS)
    check("Forecast (invalid_cat)", res.status_code == 200 and 'forecast_values' in res.json(), f"Status: {res.status_code}")
    
    # 11. Recommendations
    res = requests.get(f"{BASE_URL}/recommendations", headers=HEADERS)
    check("Recommendations", res.status_code == 200 and isinstance(res.json(), list), f"Status: {res.status_code}")

    # 12. NLP queries
    queries = [
        ("How much will I spend on food next month?", "FORECAST_REQUEST", "food"),
        ("How much did I spend on food last month?", "SPENDING_SUMMARY", "food"),
        ("How can I save money on subscriptions?", "RECOMMENDATION", "subscriptions"),
        ("forecast", "FORECAST_REQUEST", None),
        ("recently how much on food", "SPENDING_SUMMARY", "food"),
        ("how much will I spend on transport next month?", "FORECAST_REQUEST", "transport"),
    ]

    for q, exp_intent, exp_cat in queries:
        res = requests.post(f"{BASE_URL}/query", headers=HEADERS, json={'query': q})
        data = res.json()
        check(f"NLP Query: '{q}'", 
              res.status_code == 200 and data.get('intent') == exp_intent and (exp_cat is None or data.get('category') == exp_cat),
              f"Status: {res.status_code}, Exp: {exp_intent}/{exp_cat}, Got: {data.get('intent')}/{data.get('category')}")
              
    # 13. Invalid/Malformed input
    res = requests.post(f"{BASE_URL}/query", headers=HEADERS, json={})
    check("NLP Query: malformed input", res.status_code == 400, f"Status: {res.status_code}")

except Exception as e:
    print(f"Exception during tests: {e}")
    sys.exit(1)

print("\n--- Summary ---")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
if results['failed'] > 0:
    for e in results['errors']:
        print(e)
    sys.exit(1)
