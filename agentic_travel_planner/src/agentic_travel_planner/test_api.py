
import requests
import json

url = "http://localhost:8000/plan"

payload = {
    "source": "New Delhi, India",
    "destination": "Panaji, Goa, India",
    "start_date": "2026-03-10",
    "end_date": "2026-03-13",
    "num_travelers": 2,
    "budget": 1000,
    "interests": "clubs, Water sports, food, forts, Beaches",
    "group_category": "Boys only",
    "currency": 'USD'
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, timeout=60) 
    print("Response status:", response.status_code)
    print("Response body:", response.json())
except requests.exceptions.ReadTimeout:
    print("Request timed out (as expected for a long running task), but connection was successful.")
except Exception as e:
    print(f"An error occurred: {e}")
