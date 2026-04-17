# Import column types and Base
from sqlalchemy import Column, Integer, String
from app.database.connection import Base

# This class represents a table in the database
class Customer(Base):

    # Name of the table in the database
    __tablename__ = "customers"

    # Primary key (unique ID for each customer)
    id = Column(Integer, primary_key=True, index=True)

    # Customer name (cannot be empty)
    name = Column(String, nullable=False)

    # Customer email (cannot be empty)
    email = Column(String, nullable=False)

# Import additional types
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import relationship


# Invoice table
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # Example: INV-001
    invoice_number = Column(String, nullable=False)

    # Link to customer
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # Financial fields
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)

    # Relationship (connects invoice to customer)
    customer = relationship("Customer")


# Invoice items table
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    # Link to invoice
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    item_name = Column(String, nullable=False)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)

    # Relationship
    invoice = relationship("Invoice")