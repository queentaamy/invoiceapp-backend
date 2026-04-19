# Import APIRouter to group invoice routes
from fastapi import APIRouter, Depends, HTTPException

# Import Session to interact with the database
from sqlalchemy.orm import Session

# Import database session
from app.database.connection import SessionLocal

# Import database models
from app.models.models import Invoice, InvoiceItem, Customer

# Import schemas for validation and response
from app.schemas.invoice import InvoiceCreate, InvoiceRead

# import dependency (for auth)
from app.utils.deps import get_current_user

# Create router instance
router = APIRouter()


# Function to get database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test route
@router.get("/invoices/test")
def test_invoice_route():
    return {"message": "Invoice route working"}


# =========================
# CREATE INVOICE
# =========================
@router.post("/invoices")
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # requires login
):

    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate subtotal
    subtotal = sum(item.quantity * item.unit_price for item in data.items)

    # Calculate tax
    tax = subtotal * 0.15 if data.apply_tax else 0

    # Calculate total
    total = subtotal + tax

    # Generate invoice number
    invoice_count = db.query(Invoice).count()
    invoice_number = f"INV-{invoice_count + 1:03}"

    # Create invoice (NOW LINKED TO USER)
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=data.customer_id,
        user_id=current_user.id,  # 👈 IMPORTANT
        subtotal=subtotal,
        tax=tax,
        total=total
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    # Save items
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


# =========================
# GET ALL INVOICES (USER ONLY)
# =========================
@router.get("/invoices", response_model=list[InvoiceRead])
def get_invoices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Only fetch invoices belonging to logged in user
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()

    return invoices


# =========================
# GET SINGLE INVOICE
# =========================
@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id  # 👈 restrict access
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


# =========================
# DELETE INVOICE
# =========================
@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Delete related items
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

    # Delete invoice
    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted successfully"}


# =========================
# UPDATE INVOICE
# =========================
@router.put("/invoices/{invoice_id}", response_model=InvoiceRead)
def update_invoice(
    invoice_id: int,
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    invoice: Invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Recalculate totals
    subtotal = sum(item.quantity * item.unit_price for item in data.items)
    tax = subtotal * 0.15 if data.apply_tax else 0
    total = subtotal + tax

    # Update invoice
    invoice.customer_id = data.customer_id
    invoice.subtotal = subtotal
    invoice.tax = tax
    invoice.total = total

    # Delete old items
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

    # Add new items
    for item in data.items:
        db_item = InvoiceItem(
            invoice_id=invoice.id,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(db_item)

    db.commit()
    db.refresh(invoice)

    return invoice 