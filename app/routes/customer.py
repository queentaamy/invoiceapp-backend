from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Import database session
from app.database.connection import SessionLocal

# Import model and schema
from app.models.models import Customer
from app.schemas.customer import CustomerCreate, CustomerRead

# Create router
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create customer
@router.post("/customers", response_model=CustomerRead)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):

    new_customer = Customer(
        name=customer.name,
        email=customer.email
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


# Get all customers
@router.get("/customers", response_model=list[CustomerRead])
def get_customers(db: Session = Depends(get_db)):

    customers = db.query(Customer).all()

    return customers