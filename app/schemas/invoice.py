"""
INVOICE SCHEMAS - Data validation for invoice API requests and responses

Schemas define input/output formats for invoice-related endpoints.
"""

# Import BaseModel for validation
from pydantic import BaseModel

# Import List to handle multiple items in an invoice
from typing import List


# Schema for creating individual invoice items
class InvoiceItemCreate(BaseModel):
    """Validates data for a line item when creating an invoice"""
    item_name: str       # Name of product/service (e.g., "Web Design")
    quantity: int        # Number of units
    unit_price: float    # Price per unit


# Schema for creating a complete invoice
class InvoiceCreate(BaseModel):
    """Validates data when creating a new invoice"""
    customer_id: int                        # Which customer is this invoice for?
    items: List[InvoiceItemCreate]          # List of items on the invoice
    apply_tax: bool                         # Should 15% tax be applied?


# Schema for returning individual invoice items
class InvoiceItemRead(BaseModel):
    """Validates data returned for invoice items"""
    date: str            # Date 
    item_name: str       # Product/service name
    quantity: int        # Quantity ordered
    unit_price: float    # Price per unit
    total_price: float   # Calculated total (quantity × unit_price)

    class Config:
        # Converts SQLAlchemy objects to this schema format
        from_attributes = True


# Schema for returning complete invoice
class InvoiceRead(BaseModel):
    """Validates data returned when retrieving invoice information"""
    id: int                         # Unique invoice ID
    invoice_number: str             # Invoice reference number (e.g., "INV-001")
    customer_id: int                # Which customer this invoice is for
    subtotal: float                 # Total before tax
    tax: float                      # Tax amount
    total: float                    # Final total (subtotal + tax)
    items: List[InvoiceItemRead]    # All items on this invoice

    class Config:
        from_attributes = True