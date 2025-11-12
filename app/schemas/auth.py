from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True  # para SQLAlchemy 2.x

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"