from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
import requests
import pdfkit
from forex_python.converter import CurrencyRates
from phonenumbers import parse, is_valid_number
from decimal import Decimal
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi.responses import Response

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-KEY")

# Mock API Key Storage (Replace with DB in production)
API_KEYS = {"test-key": "valid"}

# Dependency to verify API Key
def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# 1. Email Validation API
class EmailValidationRequest(BaseModel):
    email: EmailStr

@app.post("/validate-email")
def validate_email(request: EmailValidationRequest, api_key: str = Depends(verify_api_key)):
    emailable_api_key = "live_aab71924040f64e4937d"  # Replace with your actual API key
    response = requests.get(f"https://api.emailable.com/v1/verify?email={request.email}&api_key={emailable_api_key}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to validate email")

    return response.json()


# 2. Currency Exchange API
currency_rates = CurrencyRates()

import requests

EXCHANGE_API_KEY = "e44cb476a87835322e119885"  # Replace with your actual API key

@app.get("/currency-exchange")
def get_exchange_rate(from_currency: str, to_currency: str, api_key: str = Depends(verify_api_key)):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{from_currency}/{to_currency}"

    try:
        print(f"Fetching exchange rate for {from_currency} → {to_currency}")  # Debugging
        response = requests.get(url)
        
        print(f"Response Status Code: {response.status_code}")  # Debugging
        print(f"Response Content: {response.text}")  # Debugging

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"External API error: {response.text}")

        data = response.json()
        
        if "conversion_rate" not in data:
            raise HTTPException(status_code=400, detail="Invalid currency pair or missing data")

        return {"exchange_rate": data["conversion_rate"]}

    except Exception as e:
        print(f"❌ Exception occurred: {e}")  # Debugging
        raise HTTPException(status_code=500, detail=str(e))



# 3. Invoice Generation API
class InvoiceRequest(BaseModel):
    sender: str
    recipient: str
    amount: Decimal
    description: str

@app.post("/generate-invoice")
def generate_invoice(request: InvoiceRequest, api_key: str = Depends(verify_api_key)):
    try:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 800, "Invoice")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, f"From: {request.sender}")
        pdf.drawString(100, 730, f"To: {request.recipient}")
        pdf.drawString(100, 710, f"Amount: ${request.amount}")
        pdf.drawString(100, 690, f"Description: {request.description}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return Response(buffer.read(), media_type="application/pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Phone Number Validation API
class PhoneValidationRequest(BaseModel):
    phone_number: str
    country_code: str

@app.post("/validate-phone")
def validate_phone(request: PhoneValidationRequest, api_key: str = Depends(verify_api_key)):
    try:
        phone = parse(request.phone_number, request.country_code)
        is_valid = is_valid_number(phone)
        return {"valid": is_valid}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid phone number")

