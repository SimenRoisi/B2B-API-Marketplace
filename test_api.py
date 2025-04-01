import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Email for testing (Replace with an actual registered email)
TEST_EMAIL = "simen1408@hotmail.com"

### 1️⃣ Retrieve API Key ###
def get_api_key():
    url = f"{BASE_URL}/get-api-key"
    response = requests.post(url, json={"email": TEST_EMAIL})
    print("\n📡 Retrieving API Key...")
    print("🔵 Status Code:", response.status_code)
    print("🔑 Response:", response.json())
    return response.json().get("api_key", None)

### 2️⃣ Reset API Key ###
def reset_api_key():
    url = f"{BASE_URL}/reset-api-key"
    response = requests.put(url, json={"email": TEST_EMAIL})
    print("\n🔄 Resetting API Key...")
    print("🔵 Status Code:", response.status_code)
    print("🆕 Response:", response.json())
    return response.json().get("new_api_key", None)

### 3️⃣ Check API Usage ###
def check_api_usage(api_key):
    url = f"{BASE_URL}/api-usage?api_key={api_key}"
    response = requests.get(url)
    print("\n📊 Checking API Usage...")
    print("🔵 Status Code:", response.status_code)
    print("📈 Response:", response.json())

### 4️⃣ Delete API Key ###
def delete_api_key():
    url = f"{BASE_URL}/delete-api-key?email={TEST_EMAIL}"
    response = requests.delete(url)
    print("\n🗑️ Deleting API Key...")
    print("🔵 Status Code:", response.status_code)
    print("🚫 Response:", response.json())

# Execute Tests
api_key = get_api_key()
if api_key:
    check_api_usage(api_key)
    new_api_key = reset_api_key()
    if new_api_key:
        check_api_usage(new_api_key)
    delete_api_key()
