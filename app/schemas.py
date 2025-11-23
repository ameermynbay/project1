from datetime import datetime
from pydantic import BaseModel, EmailStr


# ----- User Schemas -----


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2; in v1 this is orm_mode = True


# ----- Auth Schemas -----


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
