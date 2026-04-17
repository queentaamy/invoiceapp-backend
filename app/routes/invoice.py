# Import APIRouter to group invoice routes
from fastapi import APIRouter, Depends

# Import Session to interact with the database
from sqlalchemy.orm import Session

# Import database session
from app.database.connection import SessionLocal

# Import database models
from app.models.models import Invoice, InvoiceItem

# Import schemas for validation and response
from app.schemas.invoice import InvoiceCreate, InvoiceRead


# Create router instance
router = APIRouter()


# Function to get database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test route to confirm invoice routes are working
@router.get("/invoices/test")
def test_invoice_route():
    return {"message": "Invoice route working"}


# Create a new invoice
@router.post("/invoices", response_model=InvoiceRead)
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):

    # Calculate subtotal
    subtotal = 0
    for item in data.items:
        subtotal += item.quantity * item.unit_price

    # Calculate tax if applied
    tax = subtotal * 0.15 if data.apply_tax else 0

    # Calculate total
    total = subtotal + tax

    # Generate invoice number
    invoice_count = db.query(Invoice).count()
    invoice_number = f"INV-{invoice_count + 1:03}"

    # Create invoice record
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=data.customer_id,
        subtotal=subtotal,
        tax=tax,
        total=total
    )

    # Save invoice
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    # Save invoice items
    for item in data.items:
        db_item = InvoiceItem(
            invoice_id=new_invoice.id,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(db_item)

    db.commit()

    return new_invoice


# Get all invoices
@router.get("/invoices", response_model=list[InvoiceRead])
def get_invoices(db: Session = Depends(get_db)):

    # Fetch all invoices
    invoices = db.query(Invoice).all()

    return invoices