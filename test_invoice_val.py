import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/generate-invoice"

# Headers (API key)
headers = {"X-API-KEY": "test-key"}

# JSON body with invoice details
data = {
    "sender": "Company A",
    "recipient": "Client B",
    "amount": 250.75,
    "description": "Consulting Services"
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Check response status before printing
if response.status_code == 200:
    print("\n🟢 Success! Invoice Generated!\n")

    # Save the PDF response as a file
    with open("invoice.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)

    print("📄 Invoice saved as 'invoice.pdf' ✅")

else:
    print("\n🔴 Error:", response.status_code)
    print("\n⚠️ Response Message:\n", response.text)
