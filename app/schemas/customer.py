"""
CUSTOMER SCHEMAS - Data validation for customer API requests and responses

Schemas define input/output formats for customer-related API endpoints.
"""

# Import BaseModel for data validation
from pydantic import BaseModel, EmailStr


# Schema for creating a new customer (what client sends to API)
class CustomerCreate(BaseModel):
    """Validates data when creating a new customer"""
    name: str            # Customer's name (required)
    email: EmailStr      # Customer's email - must be valid email format


# Schema for returning customer data from API
class CustomerRead(BaseModel):
    """Validates data returned when retrieving customer information"""
    id: int              # Customer's unique ID from database
    name: str            # Customer's name
    email: str           # Customer's email address

    class Config:
        # Allows FastAPI to automatically convert SQLAlchemy database objects to this schema
        from_attributes = True