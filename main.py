from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
import secrets
import requests
from decimal import Decimal
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db  # ✅ Import database session function
from database import APIUsage, User  # ✅ Import models

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-KEY")

# API Key Verification with Logging
def verify_api_key(api_key: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Log API Request
    usage_entry = APIUsage(api_key=api_key, endpoint=request.url.path)
    db.add(usage_entry)
    db.commit()

    return api_key

# User Registration Request Model
class UserRegistrationRequest(BaseModel):
    email: EmailStr

# User Registration Endpoint
@app.post("/register")
def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Generate a new API key
    api_key = secrets.token_hex(16)

    # Create new user in the database
    new_user = User(email=request.email, api_key=api_key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "api_key": new_user.api_key}

class UserLookupRequest(BaseModel):
    email: EmailStr

@app.post("/get-api-key")
def get_api_key(request: UserLookupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"api_key": user.api_key}

@app.delete("/delete-api-key")
def delete_api_key(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    
    return {"message": "API key deleted successfully"}

class ResetAPIKeyRequest(BaseModel):
    email: EmailStr

@app.put("/reset-api-key")
def reset_api_key(request: ResetAPIKeyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_api_key = secrets.token_hex(16)
    user.api_key = new_api_key
    db.commit()
    db.refresh(user)
    
    return {"message": "API key reset successfully", "new_api_key": new_api_key}

@app.get("/api-usage")
def get_api_usage(api_key: str, db: Session = Depends(get_db)):
    usage_count = db.query(APIUsage).filter(APIUsage.api_key == api_key).count()
    
    return {"api_key": api_key, "requests_made": usage_count}


# 1. Email Validation API
class EmailValidationRequest(BaseModel):
    email: EmailStr

@app.post("/validate-email")
def validate_email(request: EmailValidationRequest, api_key: str = Depends(verify_api_key)):
    emailable_api_key = "your-emailable-api-key"
    response = requests.get(f"https://api.emailable.com/v1/verify?email={request.email}&api_key={emailable_api_key}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to validate email")

    return response.json()

# 2. Currency Exchange API
EXCHANGE_API_KEY = "your-exchange-api-key"

@app.get("/currency-exchange")
def get_exchange_rate(from_currency: str, to_currency: str, api_key: str = Depends(verify_api_key)):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{from_currency}/{to_currency}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"External API error: {response.text}")

    data = response.json()
    if "conversion_rate" not in data:
        raise HTTPException(status_code=400, detail="Invalid currency pair")

    return {"exchange_rate": data["conversion_rate"]}

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
        from phonenumbers import parse, is_valid_number
        phone = parse(request.phone_number, request.country_code)
        is_valid = is_valid_number(phone)
        return {"valid": is_valid}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid phone number")
