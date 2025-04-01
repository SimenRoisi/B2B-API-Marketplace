import secrets  # For generating secure API keys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# PostgreSQL Connection String
DATABASE_URL = "postgresql://api_user:securepassword@localhost/b2b_api_marketplace"

# Create Database Engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Model
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True, default=lambda: secrets.token_hex(16))  # Auto-generate API Key
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# API Usage Model
class APIUsage(Base):
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, ForeignKey("users.api_key"), index=True)
    endpoint = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Create Tables
Base.metadata.create_all(bind=engine)

# Dependency to Get Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
