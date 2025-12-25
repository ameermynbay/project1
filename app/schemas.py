from datetime import datetime, date as DateType
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# ----- User Schemas -----


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters.",
    )


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
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Book title (1–255 characters).",
    )
    author: Optional[str] = Field(
        None,
        max_length=255,
        description="Author name (optional).",
    )
    total_pages: Optional[int] = Field(
        None,
        gt=0,
        le=10000,
        description="Total number of pages (if known, must be > 0).",
    )


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
    book_id: int = Field(..., description="ID of the book you are reading.")
    pages_read: int = Field(
        ...,
        gt=0,
        le=10000,
        description="Number of pages read in this session (must be > 0).",
    )
    date: DateType = Field(
        ...,
        description="Date of reading (YYYY-MM-DD).",
    )
    note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional note about this reading session.",
    )

class ReadingLogCreate(ReadingLogBase):
    """
    For creating a new reading log.
    """
    pass


class ReadingLogUpdate(BaseModel):
    book_id: Optional[int] = Field(
        None,
        description="Change the book ID (must be a book you own).",
    )
    pages_read: Optional[int] = Field(
        None,
        gt=0,
        le=10000,
        description="Update pages read (must be > 0).",
    )
    date: Optional[DateType] = Field(
        None,
        description="Update date of reading.",
    )
    note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Update note.",
    )

class ReadingLogOut(BaseModel):
    id: int
    book_id: int
    pages_read: int
    date: DateType
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (orm_mode=True in v1)
