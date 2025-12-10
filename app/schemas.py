from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional

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



# ----- Book Schemas -----


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    total_pages: Optional[int] = None


class BookCreate(BookBase):
    """
    For now, same fields as BookBase.
    Later you can customize (e.g., make author required).
    """
    pass


class BookUpdate(BaseModel):
    """
    All fields optional, for partial updates.
    """
    title: Optional[str] = None
    author: Optional[str] = None
    total_pages: Optional[int] = None


class BookOut(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2; orm_mode=True in v1


# ----- Reading Log Schemas -----


class ReadingLogBase(BaseModel):
    book_id: int
    pages_read: int
    date: date
    note: Optional[str] = None


class ReadingLogCreate(ReadingLogBase):
    """
    For creating a new reading log.
    """
    pass


class ReadingLogUpdate(BaseModel):
    """
    For updating an existing reading log.
    All fields optional (partial update).
    """
    book_id: Optional[int] = None
    pages_read: Optional[int] = None
    date: Optional[date] = None
    note: Optional[str] = None


class ReadingLogOut(BaseModel):
    id: int
    book_id: int
    pages_read: int
    date: date
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (orm_mode=True in v1)
