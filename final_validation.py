import requests
import json

url = "http://localhost:8000/chat"
queries = [
    "What is the exit load for Tata Multicap Fund?",
    "Should I invest in Tata Flexi Cap?"
]

print("Starting Final RAG Validation...")
for q in queries:
    print(f"\nQuery: {q}")
    try:
        response = requests.post(url, json={"query": q}, timeout=30)
        if response.status_code == 200:
            print(f"Response: {response.json()['answer']}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
