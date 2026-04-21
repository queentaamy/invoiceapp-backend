"""
MAIN APPLICATION FILE

This file sets up the FastAPI application with all necessary configuration:
- Database connections
- CORS middleware for cross-origin requests
- API routes for authentication, customers, and invoices
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Import FastAPI framework
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database setup
from app.database.connection import engine, Base, ensure_customer_ownership_columns

# Import models so database tables are created on startup
from app.models import models

# Import route handlers
from app.routes.customer import router as customer_router
from app.routes.invoice import router as invoice_router
from app.routes.auth import router as auth_router


# ✅ STEP 1: CREATE app INSTANCE
app = FastAPI(title="InvoiceFlow API", description="Invoice management system")


# ✅ STEP 2: ADD MIDDLEWARE (CORS - allows requests from different origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ STEP 3: CREATE DATABASE TABLES (if they don't exist)
Base.metadata.create_all(bind=engine)

# ✅ STEP 3.5: PATCH EXISTING SQLITE TABLES FOR NEW MULTI-USER OWNERSHIP COLUMNS
ensure_customer_ownership_columns()


# ✅ STEP 4: INCLUDE ROUTES (register all API endpoints)
app.include_router(customer_router, tags=["Customers"])
app.include_router(invoice_router, tags=["Invoices"])
app.include_router(auth_router, tags=["Authentication"])


# Root endpoint - health check
@app.get("/", tags=["Health"])
def root():
    """Check if the API is running"""
    return {"message": "InvoiceFlow API is running"}