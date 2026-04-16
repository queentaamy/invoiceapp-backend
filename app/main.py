# Import FastAPI
from fastapi import FastAPI

# Import database engine and Base class
from app.database.connection import engine, Base

# Import models so SQLAlchemy knows what tables to create
from app.models import models

# Create FastAPI app
app = FastAPI()

# Create database tables automatically
# This will create invoice.db and the tables inside it
Base.metadata.create_all(bind=engine)

# Root endpoint (just to test the API is working)
@app.get("/")
def root():
    return {"message": "InvoiceFlow API is running"}