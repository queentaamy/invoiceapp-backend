# Import column types and Base
from sqlalchemy import Column, Integer, String
from app.database.connection import Base

# This class represents a table in the database
class Customer(Base):

    # Name of the table in the database
    __tablename__ = "customers"

    # Primary key (unique ID for each customer)
    id = Column(Integer, primary_key=True, index=True)

    # Customer name (cannot be empty)
    name = Column(String, nullable=False)

    # Customer email (cannot be empty)
    email = Column(String, nullable=False)