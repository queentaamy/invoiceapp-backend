# Import required modules
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./invoice.db"

# Create engine (this connects to the database)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# 👇 THIS IS WHAT YOU ARE MISSING
# This function creates and closes DB session for each request
def get_db():
    db = SessionLocal()  # open connection
    try:
        yield db          # give it to route
    finally:
        db.close()        # close after request