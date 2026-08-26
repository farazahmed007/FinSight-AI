import requests
import json
import datetime
from dateutil.relativedelta import relativedelta

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def authenticate():
    return "dev-token-123"

token = authenticate()
headers = {"Authorization": f"Bearer {token}"}

print_section("1. BACKEND & FLASK IMPORT CHECK")
health = requests.get(f"{BASE_URL}/docs")
print(f"/docs status: {health.status_code}")

print_section("3. GOALS API & 4. GOAL CALCULATIONS & 6. GOAL STATUS")
# Create a valid goal
target_date = (datetime.date.today() + relativedelta(months=6)).strftime("%Y-%m-%d")
goal_payload = {
    "name": "Test Emergency Fund",
    "description": "Six months expenses",
    "target_amount": 10000.0,
    "current_amount": 2000.0,
    "target_date": target_date,
    "category": "Savings"
}
print(f"Creating Goal: {json.dumps(goal_payload, indent=2)}")
res = requests.post(f"{BASE_URL}/api/goals", json=goal_payload, headers=headers)
print(f"POST Status: {res.status_code}")
goal_data = res.json()
print(f"Goal Response:\n{json.dumps(goal_data, indent=2)}")

goal_id = goal_data.get("id")

# Get goal
print(f"\nFetching Goal ID {goal_id}:")
res = requests.get(f"{BASE_URL}/api/goals/{goal_id}", headers=headers)
print(json.dumps(res.json(), indent=2))

# Invalid target amount test
print("\nTesting Invalid Target Amount:")
invalid_payload = {**goal_payload, "target_amount": -100}
res = requests.post(f"{BASE_URL}/api/goals", json=invalid_payload, headers=headers)
print(f"Status: {res.status_code}, Response: {res.text}")

# Update Goal (Change current_amount to verify calculations change)
print("\nUpdating Goal current_amount to 8000.0 (Should change status to NEAR_TARGET or ON_TRACK):")
res = requests.put(f"{BASE_URL}/api/goals/{goal_id}", json={"current_amount": 8000.0}, headers=headers)
print(json.dumps(res.json(), indent=2))

# Summary
print("\nGoals Summary:")
res = requests.get(f"{BASE_URL}/api/goals/summary", headers=headers)
print(json.dumps(res.json(), indent=2))

print_section("8. RECOMMENDATION INTEGRATION")
# First, let's create an AT_RISK goal to trigger a recommendation
target_date_soon = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
risk_goal_payload = {
    "name": "Impossible Vacation",
    "target_amount": 50000.0,
    "current_amount": 1000.0,
    "target_date": target_date_soon,
    "category": "Travel"
}
res = requests.post(f"{BASE_URL}/api/goals", json=risk_goal_payload, headers=headers)
risk_goal_id = res.json().get("id")
print(f"Created At-Risk Goal: {risk_goal_id}")

print("\nFetching Recommendations (checking for Goal insights):")
res = requests.get(f"{BASE_URL}/api/recommendations", headers=headers)
print(json.dumps(res.json(), indent=2))

print_section("9. NLP / AI ASSISTANT")
queries = [
    "What are my financial goals?",
    "How much have I saved for my emergency fund?",
    "How much more do I need for my Impossible Vacation goal?",
    "How much do I need to save each month?",
    "Am I on track for my goal?",
    "When will I reach my emergency goal?"
]

for q in queries:
    print(f"\nQuery: '{q}'")
    res = requests.post(f"{BASE_URL}/api/query", json={"query": q}, headers=headers)
    print(json.dumps(res.json(), indent=2))

print_section("CLEANUP")
requests.delete(f"{BASE_URL}/api/goals/{goal_id}", headers=headers)
requests.delete(f"{BASE_URL}/api/goals/{risk_goal_id}", headers=headers)
print("Deleted test goals.")
