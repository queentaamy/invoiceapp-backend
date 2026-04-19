from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.models import User
from app.schemas.user import UserCreate
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter()

# SIGNUP
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    # check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # create new user
    new_user = User(
        email=user.email,
        password=hash_password(user.password)  # hash password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# LOGIN
@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # check password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # create token
    token = create_access_token({"user_id": db_user.id})

    return {"access_token": token, "token_type": "bearer"}