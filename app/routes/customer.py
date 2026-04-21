"""
CUSTOMER ROUTES - Endpoints for managing customers

Provides endpoints to:
- Create new customers
- Retrieve all customers
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Import database session factory
from app.database.connection import SessionLocal

# Import database model and schema
from app.models.models import Customer
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
    # Create new Customer object from the input data
    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        user_id=current_user.id
    )

    # Add to database session (marks as pending)
    db.add(new_customer)
    # Commit the changes (saves to database)
    db.commit()
    # Refresh to get auto-generated ID from database
    db.refresh(new_customer)

    return new_customer


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
    customers = db.query(Customer).filter(Customer.user_id == current_user.id).all()

    return customers