# This file handles getting the current logged in user from the token

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import User

# same secret and algorithm used when creating token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# this extracts token from Authorization header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # get token string
        token = credentials.credentials

        # decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # get user id from token
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # get user from DB
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")