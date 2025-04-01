import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/currency-exchange?from_currency=USD&to_currency=EUR"

# Headers
headers = {"X-API-KEY": "test-key"}

# Make the GET request
response = requests.get(url, headers=headers)

# Print formatted response
print("\n🟢 Status Code:", response.status_code)
print("\n💱 Currency Exchange Response:\n")
print(json.dumps(response.json(), indent=4, sort_keys=True))
