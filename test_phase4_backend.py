import requests
import json

url = "http://localhost:8000/chat"
payload = {"query": "What is the NAV of Tata Large Cap Fund?"}
headers = {"Content-Type": "application/json"}

print(f"Testing Phase 4 Backend at {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(f"Response: {response.json()['answer']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
