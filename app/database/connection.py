"""
DATABASE CONNECTION - Configure SQLAlchemy and database connection

Sets up:
- SQLite or PostgreSQL database connection
- Session factory for database operations
- Base class for defining models
"""

import os
from pathlib import Path

# Import SQLAlchemy components for database operations
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# =============================
# DATABASE CONFIGURATION
# =============================

# Build a stable database path so reloads/restarts do not depend on the
# directory the server was launched from.
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BASE_DIR / "invoice.db"

# Allow overriding the database in deployments/tests, but default to the
# project-level SQLite file.
RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_SQLITE_PATH}"
)

# Accept common Postgres URL variants from hosting providers and .env files.
if RAW_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    SQLALCHEMY_DATABASE_URL = RAW_DATABASE_URL

# SQLite needs special thread handling, Postgres does not.
engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create database engine (manages connections to the database)
engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

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
    if not engine.dialect.name == "sqlite":
        return

    inspector = inspect(engine)

    with engine.begin() as connection:
        customer_columns = {column["name"] for column in inspector.get_columns("customers")}
        if "user_id" not in customer_columns:
            connection.execute(text("ALTER TABLE customers ADD COLUMN user_id INTEGER"))
        if "customer_number" not in customer_columns:
            connection.execute(text("ALTER TABLE customers ADD COLUMN customer_number INTEGER"))

        # Backfill per-user customer sequence for existing rows missing customer_number.
        connection.execute(text("""
            UPDATE customers AS c
            SET customer_number = (
                SELECT COUNT(*)
                FROM customers AS c2
                WHERE c2.user_id = c.user_id
                  AND c2.id <= c.id
            )
            WHERE c.user_id IS NOT NULL
              AND (c.customer_number IS NULL OR c.customer_number = 0)
        """))

        invoice_columns = {column["name"] for column in inspector.get_columns("invoices")}
        if "user_id" not in invoice_columns:
            connection.execute(text("ALTER TABLE invoices ADD COLUMN user_id INTEGER"))
