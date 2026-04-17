# Import BaseModel for validation
from pydantic import BaseModel

# Import List to handle multiple items
from typing import List


# Schema for creating an invoice item
class InvoiceItemCreate(BaseModel):
    item_name: str
    quantity: int
    unit_price: float


# Schema for creating an invoice
class InvoiceCreate(BaseModel):
    customer_id: int
    items: List[InvoiceItemCreate]
    apply_tax: bool


# Schema for returning invoice item
class InvoiceItemRead(BaseModel):
    item_name: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True


# Schema for returning invoice
class InvoiceRead(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    subtotal: float
    tax: float
    total: float

    class Config:
        from_attributes = True