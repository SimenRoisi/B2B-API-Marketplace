from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
import requests
import pdfkit
from forex_python.converter import CurrencyRates
from phonenumbers import parse, is_valid_number
from decimal import Decimal

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
    response = requests.get(f"https://api.trumail.io/v2/lookups/json?email={request.email}")
    return response.json()

# 2. Currency Exchange API
currency_rates = CurrencyRates()

@app.get("/currency-exchange")
def get_exchange_rate(from_currency: str, to_currency: str, api_key: str = Depends(verify_api_key)):
    rate = currency_rates.get_rate(from_currency.upper(), to_currency.upper())
    if not rate:
        raise HTTPException(status_code=400, detail="Invalid currency pair")
    return {"exchange_rate": rate}

# 3. Invoice Generation API
class InvoiceRequest(BaseModel):
    sender: str
    recipient: str
    amount: Decimal
    description: str

@app.post("/generate-invoice")
def generate_invoice(request: InvoiceRequest, api_key: str = Depends(verify_api_key)):
    html = f"""
    <html>
        <body>
            <h2>Invoice</h2>
            <p><strong>From:</strong> {request.sender}</p>
            <p><strong>To:</strong> {request.recipient}</p>
            <p><strong>Amount:</strong> ${request.amount}</p>
            <p><strong>Description:</strong> {request.description}</p>
        </body>
    </html>
    """
    pdf = pdfkit.from_string(html, False)
    return {"pdf": pdf.hex()}  # Returning hex for simplicity

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

# 5. Tax Calculator API
TAX_RATES = {
    "US": 0.07,
    "UK": 0.20,
    "EU": 0.19,
    "CA": 0.13
}  # Example tax rates

class TaxCalculationRequest(BaseModel):
    country: str
    amount: Decimal

@app.post("/calculate-tax")
def calculate_tax(request: TaxCalculationRequest, api_key: str = Depends(verify_api_key)):
    tax_rate = TAX_RATES.get(request.country.upper())
    if tax_rate is None:
        raise HTTPException(status_code=400, detail="Country not supported")
    tax = request.amount * Decimal(tax_rate)
    return {"tax_amount": round(tax, 2), "total_amount": round(request.amount + tax, 2)}
