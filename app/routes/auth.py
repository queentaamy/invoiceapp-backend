"""
AUTHENTICATION ROUTES - Handle user signup and login

Provides endpoints for:
- User registration (signup) with password hashing
- User login with JWT token generation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import User
from app.schemas.user import UserCreate
from app.utils.auth import hash_password, verify_password, create_access_token

# Create router for grouping auth endpoints
router = APIRouter()


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    1. Check if email already exists
    2. Hash the password for security
    3. Save new user to database
    
    Returns: Success message if account created
    Raises: 400 error if email already registered
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create new user with hashed password (never store plain passwords!)
    new_user = User(
        email=user.email,
        password=hash_password(user.password)  # Hash using bcrypt
    )

    # Save to database and commit changes
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the user ID from database

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticate user and issue JWT token
    
    1. Find user by email
    2. Verify password matches
    3. Generate JWT token for future requests
    
    Returns: JWT token to use in Authorization header
    Raises: 400 error if credentials invalid
    """
    # Find user in database by email
    db_user = db.query(User).filter(User.email == user.email).first()

    # If user doesn't exist, don't reveal that (security best practice)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify the provided password matches the stored hashed password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token with user ID (token expires in 1 hour)
    token = create_access_token({"user_id": db_user.id})

    return {
        "access_token": token,
        "token_type": "bearer"  # Client includes this in Authorization header
    }