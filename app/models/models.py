# Import SQLAlchemy tools
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

# Import Base class
from app.database.connection import Base


# =========================
# USER MODEL
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # user email (used for login)
    email = Column(String, unique=True, index=True)

    # hashed password
    password = Column(String)

    # relationship to invoices
    invoices = relationship("Invoice", back_populates="owner")


# =========================
# CUSTOMER MODEL
# =========================
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # customer name
    name = Column(String, index=True)

    # customer email
    email = Column(String, unique=True, index=True)

    # relationship to invoices
    invoices = relationship("Invoice", back_populates="customer")


# =========================
# INVOICE MODEL
# =========================
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # unique invoice number
    invoice_number = Column(String, unique=True, index=True)

    # link to customer
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # link to user (owner of invoice)
    user_id = Column(Integer, ForeignKey("users.id"))

    # financial fields
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)

    # relationships
    customer = relationship("Customer", back_populates="invoices")
    owner = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete")


# =========================
# INVOICE ITEM MODEL
# =========================
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    # link to invoice
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    # item details
    item_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)

    # relationship
    invoice = relationship("Invoice", back_populates="items")