# Import BaseModel for data validation
from pydantic import BaseModel

# Schema for creating a customer (input)
class CustomerCreate(BaseModel):
    name: str
    email: str

# Schema for returning customer data (output)
class CustomerRead(BaseModel):
    id: int
    name: str
    email: str

    # Allows FastAPI to convert database objects to JSON
    class Config:
        from_attributes = True