# Invoice-Flow
  A fullstack invoice management system for small businesses

# What does The system do?
  This is an invoice management backend system that allows users to create customers, generate invoices with multiple items, and automatically calculate totals. It uses FastAPI for the API layer, SQLAlchemy for database interaction, and SQLite for persistent storage.

# API Endpoints
  GET /customers → Retrieve all customers
  POST /customers → Create a new customer

  GET /invoices → Retrieve all invoices
  GET /invoices/{id} → Retrieve a single invoice
  POST /invoices → Create a new invoice

# Feature
- Customer management
- Invoice creation with multiple items
- Automatic subtotal, tax, and total calculation
- Data validation using Pydantic
- SQLite database with SQLAlchemy ORM
- RESTful API with FastAPI