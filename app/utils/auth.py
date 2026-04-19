# Handles password hashing and token creation

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash password before saving
def hash_password(password: str):
    return pwd_context.hash(password)

# verify password during login
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)