from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.schemas import ReadingLogCreate, ReadingLogUpdate, ReadingLogOut
from app.core.security import get_current_user
from sqlalchemy import func


router = APIRouter(
    prefix="/reading-logs",
    tags=["reading-logs"],
)

@router.get(
    "/summary",
)
def get_reading_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    book_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """
    Return simple stats: total pages read (optionally filtered).
    """
    query = db.query(func.sum(models.ReadingLog.pages_read)).filter(
        models.ReadingLog.user_id == current_user.id
    )

    if book_id is not None:
        query = query.filter(models.ReadingLog.book_id == book_id)
    if date_from is not None:
        query = query.filter(models.ReadingLog.date >= date_from)
    if date_to is not None:
        query = query.filter(models.ReadingLog.date <= date_to)

    total_pages = query.scalar() or 0

    return {"total_pages_read": int(total_pages)}

def _get_user_log_or_404(
    log_id: int,
    db: Session,
    current_user: models.User,
) -> models.ReadingLog:
    log = (
        db.query(models.ReadingLog)
        .filter(
            models.ReadingLog.id == log_id,
            models.ReadingLog.user_id == current_user.id,
        )
        .first()
    )
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading log not found",
        )
    return log


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
    response_model=ReadingLogOut,
    status_code=status.HTTP_201_CREATED,
)
def create_reading_log(
    log_in: ReadingLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Ensure the book belongs to the current user
    _get_user_book_or_404(log_in.book_id, db, current_user)

    log = models.ReadingLog(
        user_id=current_user.id,
        book_id=log_in.book_id,
        pages_read=log_in.pages_read,
        date=log_in.date,
        note=log_in.note,
    )

    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get(
    "",
    response_model=List[ReadingLogOut],
)
def list_reading_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    book_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    List reading logs for current user.
    Optional filters: book_id, date range.
    """
    query = db.query(models.ReadingLog).filter(
        models.ReadingLog.user_id == current_user.id
    )

    if book_id is not None:
        query = query.filter(models.ReadingLog.book_id == book_id)

    if date_from is not None:
        query = query.filter(models.ReadingLog.date >= date_from)

    if date_to is not None:
        query = query.filter(models.ReadingLog.date <= date_to)

    logs = query.order_by(models.ReadingLog.date.desc()) \
                .offset(skip) \
                .limit(limit) \
                .all()

    return logs

@router.get(
    "/{log_id}",
    response_model=ReadingLogOut,
)
def get_reading_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    log = _get_user_log_or_404(log_id, db, current_user)
    return log

@router.put(
    "/{log_id}",
    response_model=ReadingLogOut,
)
def update_reading_log(
    log_id: int,
    log_in: ReadingLogUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    log = _get_user_log_or_404(log_id, db, current_user)

    if log_in.book_id is not None:
        # Ensure new book (if provided) belongs to the current user
        _get_user_book_or_404(log_in.book_id, db, current_user)
        log.book_id = log_in.book_id

    if log_in.pages_read is not None:
        log.pages_read = log_in.pages_read

    if log_in.date is not None:
        log.date = log_in.date

    if log_in.note is not None:
        log.note = log_in.note

    db.commit()
    db.refresh(log)
    return log


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reading_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    log = _get_user_log_or_404(log_id, db, current_user)

    db.delete(log)
    db.commit()
    return





