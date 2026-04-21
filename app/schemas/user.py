"""
USER SCHEMAS - Data validation for user-related API requests and responses

Schemas define the structure of data that enters and leaves the API.
Pydantic validates that the data matches the expected format.
"""

from pydantic import BaseModel, EmailStr


# Used when user signs up or logs in
class UserCreate(BaseModel):
    """Schema for user registration/login - validates input data"""
    email: EmailStr      # Email must be in valid email format
    password: str        # Plain password from user


# Used when returning user data from the API
class UserRead(BaseModel):
    """Schema for returning user data - what API sends back to client"""
    id: int              # User's unique ID from database
    email: EmailStr      # User's email address

    class Config:
        # Allows FastAPI to convert SQLAlchemy database objects to JSON automatically
        from_attributes = True