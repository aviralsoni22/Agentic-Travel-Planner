
import requests
import json

url = "http://localhost:8000/plan"

payload = {
    "source": "New Delhi, India",
    "destination": "Panaji, Goa, India",
    "start_date": "2026-01-10",
    "end_date": "2026-01-13",
    "trip_duration": 3,
    "num_travelers": 2,
    "budget": 600,
    "interests": "clubs, Water sports, food, forts, Beaches",
    "group_category": "Boys only"
}

try:
    print(f"Sending request to {url}...")
    # Timeout set to very short because we just want to see if it connects, 
    # we don't necessarily want to wait for the full crew execution which might take minutes.
    # However, if it connects and hangs, that's a good sign the crew is running.
    # If we want to fully verify, we need to wait.
    response = requests.post(url, json=payload, timeout=10) 
    print("Response status:", response.status_code)
    print("Response body:", response.json())
except requests.exceptions.ReadTimeout:
    print("Request timed out (as expected for a long running task), but connection was successful.")
except Exception as e:
    print(f"An error occurred: {e}")
