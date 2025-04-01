import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/validate-phone"

# Headers (API key)
headers = {"X-API-KEY": "test-key"}

# JSON body with phone number details
data = {
    "phone_number": "90947906",  # Change this to a real number for testing
    "country_code": "NO"
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Check response status before printing
if response.status_code == 200:
    print("\n🟢 Success! Phone Validation Response:\n")
    print(json.dumps(response.json(), indent=4, sort_keys=True))
else:
    print("\n🔴 Error:", response.status_code)
    print("\n⚠️ Response Message:\n", response.text)
