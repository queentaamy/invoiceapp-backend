# Import required SQLAlchemy tools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the database URL
# sqlite:///./invoice.db means:
# - use SQLite
# - create a file called invoice.db in the current folder
DATABASE_URL = "sqlite:///./invoice.db"

# Create the database engine
# connect_args is needed for SQLite to allow multiple threads (FastAPI needs this)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# This creates a session factory
# A session is what we use to interact with the database (read, write, update)
SessionLocal = sessionmaker(bind=engine)

# Base class that all our models will inherit from
# It helps SQLAlchemy know how to create tables
Base = declarative_base()