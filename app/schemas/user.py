from pydantic import BaseModel, EmailStr

# Used when creating account
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Used when returning user data
class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True