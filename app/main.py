# Import FastAPI
from fastapi import FastAPI

# Import database engine and Base class
from app.database.connection import engine, Base

# Import models so SQLAlchemy knows what tables to create
from app.models import models

# Import customer routes
from app.routes.customer import router as customer_router

# Create FastAPI app
app = FastAPI()

# Create database tables automatically
# This will create invoice.db and the tables inside it
Base.metadata.create_all(bind=engine)

# Attach routes to the app
app.include_router(customer_router)

# Root endpoint (just to test the API is working)
@app.get("/")
def root():
    return {"message": "InvoiceFlow API is running"}