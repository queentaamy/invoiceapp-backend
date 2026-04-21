"""
DEPENDENCIES - Utility functions used by route handlers

Provides dependency injection for:
- Extracting and validating JWT tokens from requests
- Verifying user authentication

Used as Depends(get_current_user) in protected endpoints
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import User
from app.utils.auth import SECRET_KEY

# Secret key and algorithm must match what's used when creating tokens
ALGORITHM = "HS256"

# Security scheme - automatically extracts Bearer token from Authorization header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate JWT token, return authenticated user
    
    This is a dependency used in protected routes.
    FastAPI automatically calls this before executing the route handler.
    
    Usage in routes:
        @router.get("/protected")
        def protected_route(current_user = Depends(get_current_user)):
            return {"user_id": current_user.id}
    
    Args:
        credentials: Authorization header with Bearer token (extracted automatically)
        db: Database session for looking up user
    
    Returns:
        User object if token is valid
    
    Raises:
        401 error if token is invalid or user doesn't exist
    """
    try:
        # Extract token string from Authorization header (format: "Bearer <token>")
        token = credentials.credentials

        # Decode JWT token using secret key and verify signature
        # This also validates that token hasn't expired
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user_id from token payload
        user_id = payload.get("user_id")

        # If no user_id in token, token is invalid
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Look up user in database using user_id from token
        user = db.query(User).filter(User.id == user_id).first()

        # If user doesn't exist, token references deleted user
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        # Return the authenticated user object to route handler
        return user

    # Catch JWT errors (invalid signature, expired token, etc.)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")