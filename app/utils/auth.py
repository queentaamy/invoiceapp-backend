"""
AUTHENTICATION UTILITIES - Handle password hashing and JWT token creation

Provides functions for:
- Hashing passwords with bcrypt before storing in database
- Verifying passwords during login
- Creating JWT tokens for authenticated requests
"""

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

# Load secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Fallback secret key if .env is missing (development only)
if not SECRET_KEY:
    SECRET_KEY = "dev-secret-key"  # TODO: Never use default in production!

# Algorithm for JWT encoding/decoding
ALGORITHM = "HS256"

# Configure bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    
    Args:
        password: Plain text password from user
    
    Returns:
        Hashed password string (can be safely stored in database)
    
    Security: Never store plain passwords! Always hash before saving.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a hashed password
    
    Args:
        plain_password: Plain text password from login request
        hashed_password: Hashed password stored in database
    
    Returns:
        True if passwords match, False otherwise
    
    Used during login to authenticate users
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT token for authenticated API requests
    
    Args:
        data: Dictionary containing user info (e.g., {"user_id": 1})
    
    Returns:
        JWT token string (client includes in Authorization header)
    
    Token expires in 1 hour - client must login again after expiration
    """
    # Copy the data to avoid modifying original
    to_encode = data.copy()

    # Set token expiration to 1 hour from now
    expire = datetime.utcnow() + timedelta(hours=1)
    # Add expiration time to token data
    to_encode.update({"exp": expire})

    # Encode data into JWT token using secret key
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)