from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.schemas import BookCreate, BookUpdate, BookOut
from app.core.security import get_current_user

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


def _get_user_book_or_404(
    book_id: int,
    db: Session,
    current_user: models.User,
) -> models.Book:
    book = (
        db.query(models.Book)
        .filter(
            models.Book.id == book_id,
            models.Book.user_id == current_user.id,
        )
        .first()
    )
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book

@router.post(
    "",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = models.Book(
        user_id=current_user.id,
        title=book_in.title,
        author=book_in.author,
        total_pages=book_in.total_pages,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get(
    "",
    response_model=List[BookOut],
)
def list_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    List books for the current user.
    Basic pagination with skip/limit.
    """
    books = (
        db.query(models.Book)
        .filter(models.Book.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return books

@router.get(
    "/{book_id}",
    response_model=BookOut,
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = _get_user_book_or_404(book_id, db, current_user)
    return book


@router.put(
    "/{book_id}",
    response_model=BookOut,
)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = _get_user_book_or_404(book_id, db, current_user)

    # Apply updates only to provided fields
    if book_in.title is not None:
        book.title = book_in.title
    if book_in.author is not None:
        book.author = book_in.author
    if book_in.total_pages is not None:
        book.total_pages = book_in.total_pages

    db.commit()
    db.refresh(book)
    return book

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = _get_user_book_or_404(book_id, db, current_user)

    db.delete(book)
    db.commit()
    # 204: empty response body
    return


