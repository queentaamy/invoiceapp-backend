"""
DATABASE MODELS - Define the structure of database tables

These classes represent tables in the SQLite database.
Each class creates a table with specified columns and relationships.
"""

# Import SQLAlchemy tools for database operations
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

# Import Base class (parent class for all models)
from app.database.connection import Base


# =========================
# USER MODEL - Represents registered users/accounts
# =========================
class User(Base):
    """User account model for storing user credentials and invoices"""
    __tablename__ = "users"

    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)

    # User email address (used for login) - must be unique
    email = Column(String, unique=True, index=True)

    # 
    name = Column(String)

    # Hashed password (never store plain text passwords!)
    password = Column(String)

    # Relationship to invoices - user can have multiple invoices
    # 'back_populates' creates a two-way relationship
    invoices = relationship("Invoice", back_populates="owner")

    # Relationship to customers - user can own multiple customers
    customers = relationship("Customer", back_populates="owner")


# =========================
# CUSTOMER MODEL - Represents clients/customers who receive invoices
# =========================
class Customer(Base):
    """Customer model for storing customer information"""
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("user_id", "email", name="uq_customers_user_email"),
    )

    # Primary key - unique identifier for each customer
    id = Column(Integer, primary_key=True, index=True)

    # Customer's business or personal name
    name = Column(String, index=True)

    # Customer's email address (unique per user)
    email = Column(String, index=True)

    # Per-user customer sequence number (1, 2, 3...) used for display
    customer_number = Column(Integer, index=True)

    # Foreign key linking customer to the user who created it
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship to invoices - customer can have multiple invoices
    invoices = relationship("Invoice", back_populates="customer")

    # Relationship to the user who owns this customer
    owner = relationship("User", back_populates="customers")


# =========================
# INVOICE MODEL - Represents invoices created by users for customers
# =========================
class Invoice(Base):
    """Invoice model for storing invoice data and financial information"""
    __tablename__ = "invoices"

    # Primary key - unique identifier for each invoice
    id = Column(Integer, primary_key=True, index=True)

    # Unique invoice number (e.g., "INV-001", "INV-002") for reference
    invoice_number = Column(String, unique=True, index=True)

    # Foreign key linking to Customer - which customer is this invoice for?
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # Foreign key linking to User - who created this invoice?
    user_id = Column(Integer, ForeignKey("users.id"))

    # Financial fields
    subtotal = Column(Float)  # Total before tax
    tax = Column(Float)       # Tax amount (15% if applied)
    total = Column(Float)     # Final total (subtotal + tax)

    # Relationships to other models
    # Links to the Customer this invoice is for
    customer = relationship("Customer", back_populates="invoices")
    # Links to the User (owner) who created this invoice
    owner = relationship("User", back_populates="invoices")
    # Links to all invoice items - cascade delete removes items when invoice is deleted
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete")


# =========================
# INVOICE ITEM MODEL - Represents individual line items on an invoice
# =========================
class InvoiceItem(Base):
    """InvoiceItem model for storing individual products/services on an invoice"""
    __tablename__ = "invoice_items"

    # Primary key - unique identifier for each item
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to Invoice - which invoice does this item belong to?
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    # Item details
    item_name = Column(String)        # Name of the product or service (e.g., "Web Development", "Design")
    quantity = Column(Integer)        # How many units of this item
    unit_price = Column(Float)        # Price per unit
    total_price = Column(Float)       # Calculated as quantity × unit_price

    # Relationship to Invoice - link back to the parent invoice
    invoice = relationship("Invoice", back_populates="items")
