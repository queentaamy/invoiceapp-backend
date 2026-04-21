"""
INVOICE ROUTES - Endpoints for managing invoices

Provides endpoints to:
- Create new invoices with line items
- View user's invoices
- Get specific invoice details
- Update invoice information
- Delete invoices

Note: All endpoints require authentication (JWT token)
"""

# Import APIRouter to group invoice routes
from fastapi import APIRouter, Depends, HTTPException

# Import Session to interact with the database
from sqlalchemy.orm import Session
from sqlalchemy import func

# Import database session factory
from app.database.connection import SessionLocal

# Import database models
from app.models.models import Invoice, InvoiceItem, Customer

# Import schemas for validation and response
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceItemRead

# Import dependency for checking authentication (JWT token)
from app.utils.deps import get_current_user

# Create router instance for grouping invoice endpoints
router = APIRouter()


def _format_display_invoice_number(raw_invoice_number: str) -> str:
    """Convert stored value like U2-INV-001 to display value INV-001."""
    if raw_invoice_number.startswith("U") and "-INV-" in raw_invoice_number:
        return f"INV-{raw_invoice_number.split('-INV-')[-1]}"
    return raw_invoice_number


def _to_invoice_read(invoice: Invoice) -> InvoiceRead:
    """Map ORM invoice to API response using per-user display identifiers."""
    display_customer_id = invoice.customer.customer_number if invoice.customer else invoice.customer_id

    return InvoiceRead(
        id=invoice.id,
        invoice_number=_format_display_invoice_number(invoice.invoice_number),
        customer_id=display_customer_id,
        subtotal=invoice.subtotal,
        tax=invoice.tax,
        total=invoice.total,
        due_date=invoice.due_date,
        created_at=invoice.created_at,
        is_paid=invoice.is_paid,
        items=[
            InvoiceItemRead(
                item_name=item.item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in invoice.items
        ],
    )


# Function to get database connection for each request
def get_db():
    """Opens a DB connection, yields it to the route, then closes it"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensure connection is closed even if error occurs


# Test route to verify invoice endpoints are working
@router.get("/invoices/test")
def test_invoice_route():
    """Health check - verify invoice routes are working"""
    return {"message": "Invoice route working"}


# =========================
# CREATE INVOICE
# =========================
@router.post("/invoices", response_model=InvoiceRead)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Requires user to be logged in
):
    """
    Create a new invoice with line items
    
    Process:
    1. Verify customer exists
    2. Calculate subtotal from all line items
    3. Apply 15% tax if requested
    4. Generate unique invoice number
    5. Save invoice and all items to database
    
    Args:
        data: InvoiceCreate with customer_id, items, and apply_tax flag
        db: Database session
        current_user: Authenticated user (from JWT token)
    
    Returns: Created invoice with all details
    Raises: 404 if customer not found
    """
    # Verify the customer exists (can't create invoice for non-existent customer)
    customer = db.query(Customer).filter(
        Customer.customer_number == data.customer_id,
        Customer.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate subtotal by summing all line items
    subtotal = sum(item.quantity * item.unit_price for item in data.items)

    # Calculate tax (15% if apply_tax is True, otherwise 0)
    tax = subtotal * 0.15 if data.apply_tax else 0

    # Calculate final total
    total = subtotal + tax

    # Generate per-user invoice sequence and a globally unique stored invoice number.
    invoice_count = db.query(func.count(Invoice.id)).filter(
        Invoice.user_id == current_user.id
    ).scalar()
    invoice_sequence = (invoice_count or 0) + 1
    invoice_number = f"U{current_user.id}-INV-{invoice_sequence:03}"

    # Create invoice object linked to current user
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=customer.id,
        user_id=current_user.id,  # Important: Link to user for multi-user support
        subtotal=subtotal,
        tax=tax,
        total=total,
        due_date=data.due_date,
    )

    # Save invoice to database
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)  # Get auto-generated ID from database

    # Save all line items for this invoice
    for item in data.items:
        db_item = InvoiceItem(
            invoice_id=new_invoice.id,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(db_item)

    # Save all items at once
    db.commit()

    db.refresh(new_invoice)

    return _to_invoice_read(new_invoice)


# =========================
# GET ALL INVOICES (USER ONLY)
# =========================
@router.get("/invoices", response_model=list[InvoiceRead])
def get_invoices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve all invoices created by the authenticated user
    
    Returns: List of invoices (filtered by current user)
    
    Security: Users can only see their own invoices
    """
    # Query only invoices belonging to the logged-in user
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).order_by(Invoice.created_at.desc(), Invoice.id.desc()).all()

    return [_to_invoice_read(invoice) for invoice in invoices]


# =========================
# GET SINGLE INVOICE
# =========================
@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve a specific invoice by ID
    
    Args:
        invoice_id: ID of the invoice to retrieve
        db: Database session
        current_user: Authenticated user
    
    Returns: Invoice details with all line items
    Raises: 404 if invoice not found or belongs to different user
    
    Security: Users can only view their own invoices
    """
    # Query invoice by ID, ensuring it belongs to current user
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id  # Security: prevent access to other user's invoices
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return _to_invoice_read(invoice)


# =========================
# DELETE INVOICE
# =========================
@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an invoice and all its line items
    
    Process:
    1. Find invoice by ID (verify ownership)
    2. Delete all line items for this invoice
    3. Delete the invoice itself
    
    Args:
        invoice_id: ID of invoice to delete
        db: Database session
        current_user: Authenticated user
    
    Returns: Success message
    Raises: 404 if invoice not found or belongs to different user
    
    Security: Users can only delete their own invoices
    """
    # Query invoice by ID, ensuring it belongs to current user
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Delete all line items associated with this invoice
    # Cascade delete would handle this, but explicit is clearer
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

    # Delete the invoice itself
    db.delete(invoice)
    # Commit both deletions together
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
    """
    Update an existing invoice and its line items
    
    Process:
    1. Find invoice by ID (verify ownership)
    2. Recalculate totals based on new items
    3. Replace all line items with new ones
    4. Update invoice financial fields
    
    Args:
        invoice_id: ID of invoice to update
        data: InvoiceCreate with new customer, items, and tax setting
        db: Database session
        current_user: Authenticated user
    
    Returns: Updated invoice with new details
    Raises: 404 if invoice not found or belongs to different user
    
    Security: Users can only update their own invoices
    """
    # Query invoice by ID, ensuring it belongs to current user
    invoice: Invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    customer = db.query(Customer).filter(
        Customer.customer_number == data.customer_id,
        Customer.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Recalculate all financial totals based on new items
    subtotal = sum(item.quantity * item.unit_price for item in data.items)
    tax = subtotal * 0.15 if data.apply_tax else 0
    total = subtotal + tax

    # Update invoice with new financial data
    invoice.customer_id = customer.id
    invoice.subtotal = subtotal
    invoice.tax = tax
    invoice.total = total
    invoice.due_date = data.due_date

    # Delete all old line items
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

    # Add all new line items
    for item in data.items:
        db_item = InvoiceItem(
            invoice_id=invoice.id,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(db_item)

    # Commit all changes together
    db.commit()
    # Refresh to ensure we have latest data from database
    db.refresh(invoice)

    return _to_invoice_read(invoice)


# =========================
# MARK INVOICE AS PAID
# =========================
@router.patch("/invoices/{invoice_id}/paid", response_model=InvoiceRead)
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark an invoice as paid for the authenticated user.
    """
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.is_paid = True
    db.commit()
    db.refresh(invoice)

    return _to_invoice_read(invoice)
