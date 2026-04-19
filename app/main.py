# Import FastAPI
from fastapi import FastAPI

# Import database setup
from app.database.connection import engine, Base

# Import models so tables are created
from app.models import models

# Import routes
from app.routes.customer import router as customer_router
from app.routes.invoice import router as invoice_router
from app.routes.auth import router as auth_router

# 👇 CREATE app FIRST
app = FastAPI()

# 👇 THEN create tables
Base.metadata.create_all(bind=engine)

# 👇 THEN include routes
app.include_router(customer_router)
app.include_router(invoice_router)
app.include_router(auth_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "InvoiceFlow API is running"}