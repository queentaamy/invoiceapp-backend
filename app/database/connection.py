"""
DATABASE CONNECTION - Configure SQLAlchemy and database connection

Sets up:
- SQLite database connection
- Session factory for database operations
- Base class for defining models
"""

# Import SQLAlchemy components for database operations
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# =============================
# DATABASE CONFIGURATION
# =============================

# SQLite database URL pointing to invoice.db file
# Format: sqlite:///./filename means local file in current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./invoice.db"

# Create database engine (manages connections to the database)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # check_same_thread=False: SQLite by default doesn't allow threading,
    # we disable it to allow FastAPI's async requests
    connect_args={"check_same_thread": False}
)

# Create session factory - used to create database sessions
# - autocommit=False: Changes require explicit commit()
# - autoflush=False: Changes aren't auto-sent, we control when to flush
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models (ORM classes inherit from this)
Base = declarative_base()


# =============================
# DATABASE SESSION DEPENDENCY
# =============================

def get_db():
    """
    Database session dependency for FastAPI routes
    
    Creates a new database connection for each request,
    yields it to the route handler, then closes it after.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    This ensures proper resource management:
    1. Connection opens when request starts
    2. Route handler receives the session
    3. Connection closes when request ends (even if error occurs)
    """
    # Open a new database connection
    db = SessionLocal()
    try:
        # Yield session to the route handler
        yield db
    finally:
        # Always close connection, even if an error occurred
        db.close()


def ensure_customer_ownership_columns():
    """
    Add missing ownership columns to existing SQLite tables.

    SQLite does not update old tables when models change, so this keeps the
    database compatible with the current multi-user data model.
    """
    inspector = inspect(engine)

    with engine.begin() as connection:
        customer_columns = {column["name"] for column in inspector.get_columns("customers")}
        if "user_id" not in customer_columns:
            connection.execute(text("ALTER TABLE customers ADD COLUMN user_id INTEGER"))

        invoice_columns = {column["name"] for column in inspector.get_columns("invoices")}
        if "user_id" not in invoice_columns:
            connection.execute(text("ALTER TABLE invoices ADD COLUMN user_id INTEGER"))