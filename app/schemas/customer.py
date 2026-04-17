# Import BaseModel for data validation
from pydantic import BaseModel, EmailStr

# Schema for creating a customer (input)
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr # Validates that the email is in correct format

# Schema for returning customer data (output)
class CustomerRead(BaseModel):
    id: int
    name: str
    email: str

    # Allows FastAPI to convert database objects to JSON
    class Config:
        from_attributes = True