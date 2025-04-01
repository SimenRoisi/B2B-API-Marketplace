import requests
import json  # Import json module for formatting

# API endpoint
url = "http://127.0.0.1:8000/validate-email"

# Headers (including API key)
headers = {
    "X-API-KEY": "test-key"  # Replace with your actual API key if needed
}

# JSON body with the email to validate
data = {
    "email": "test@example.com"
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Print the response in a nicely formatted way
print("\n🟢 Status Code:", response.status_code)
print("\n📨 Response JSON:\n")
print(json.dumps(response.json(), indent=4, sort_keys=True))  # Pretty-print JSON
