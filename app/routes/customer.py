# Every 
"""
CUSTOMER ROUTES - Endpoints for managing customers

Provides endpoints to:
- Create new customers
- Retrieve all customers
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

# Import database session factory
from app.database.connection import SessionLocal

# Import database model and schema
from app.models.models import Customer, Invoice
from app.schemas.customer import CustomerCreate, CustomerRead
from app.utils.deps import get_current_user

# Create router instance for grouping customer endpoints
router = APIRouter()


# Dependency to get database session for each request
def get_db():
    """Opens a DB connection, yields it to the route, then closes it"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensure connection is closed even if error occurs


# Create a new customer
@router.post("/customers", response_model=CustomerRead)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new customer in the database
    
    Parameters:
    - customer: CustomerCreate schema with name and email
    - db: Database session (provided automatically)
    
    Returns: The newly created customer with ID
    """
    customer_name = customer.name.strip()
    customer_email = customer.email.strip().lower()

    # Prevent duplicate customer emails for the same user.
    existing_customer = db.query(Customer).filter(
        Customer.user_id == current_user.id,
        func.lower(Customer.email) == customer_email
    ).first()
    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer email already exists in your account"
        )

    # Generate per-user customer number (1, 2, 3...).
    max_customer_number = db.query(func.max(Customer.customer_number)).filter(
        Customer.user_id == current_user.id
    ).scalar()
    next_customer_number = (max_customer_number or 0) + 1

    # Create new Customer object from the input data
    new_customer = Customer(
        name=customer_name,
        email=customer_email,
        user_id=current_user.id,
        customer_number=next_customer_number
    )

    # Add to database session (marks as pending)
    db.add(new_customer)
    # Commit the changes (saves to database)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Customer email already exists in your account"
        )
    # Refresh to get auto-generated ID from database
    db.refresh(new_customer)

    # Return per-user display ID so frontend shows Customer #1, #2, etc.
    return CustomerRead(
        id=new_customer.customer_number,
        name=new_customer.name,
        email=new_customer.email
    )


# Get all customers
@router.get("/customers", response_model=list[CustomerRead])
def get_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve all customers from the database
    
    Returns: List of all customers with their details
    """
    # Query all Customer records from database
    customers = db.query(Customer).filter(
        Customer.user_id == current_user.id
    ).order_by(Customer.customer_number.asc(), Customer.id.asc()).all()

    # Return per-user display IDs to avoid showing global DB IDs.
    return [
        CustomerRead(
            id=customer.customer_number,
            name=customer.name,
            email=customer.email
        )
        for customer in customers
    ]


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a customer from the authenticated user's customer list.

    Customers with existing invoices are blocked to avoid orphaning invoice
    history. Delete the related invoices first if the customer is no longer
    needed.
    """
    customer = db.query(Customer).filter(
        Customer.customer_number == customer_id,
        Customer.user_id == current_user.id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing_invoice = db.query(Invoice.id).filter(
        Invoice.customer_id == customer.id,
        Invoice.user_id == current_user.id
    ).first()
    if existing_invoice:
        raise HTTPException(
            status_code=400,
            detail="Delete the customer's invoices before deleting this customer"
        )

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}
