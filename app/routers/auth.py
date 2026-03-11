from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from datetime import datetime
from app.schemas import UserCreate, UserOut, LoginRequest, Token, RefreshRequest, TokenPair
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    hash_refresh_token,
    create_refresh_token,
    refresh_token_expiry
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# ----- Register -----



@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(user_in.password)

    user = models.User(
        email=user_in.email,
        password_hash=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ----- Login -----


@router.post("/login", response_model=TokenPair)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    # Create refresh token (raw) and store only hash
    refresh_token_raw = create_refresh_token()
    token_row = models.RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token_raw),
        expires_at=refresh_token_expiry(),
        revoked_at=None,
    )
    db.add(token_row)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_raw,
        "token_type": "bearer",
    }


# ----- Current user (for testing) -----


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user




# ------ Refresh ------

@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    token_hash = hash_refresh_token(body.refresh_token)

    token_row = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.token_hash == token_hash)
        .first()
    )

    if (
        token_row is None
        or token_row.revoked_at is not None
        or token_row.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db.query(models.User).filter(models.User.id == token_row.user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Rotate: revoke old token
    token_row.revoked_at = now

    # Create new refresh token row
    new_refresh_raw = create_refresh_token()
    new_row = models.RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_raw),
        expires_at=refresh_token_expiry(),
        revoked_at=None,
    )
    db.add(new_row)

    # New access token
    new_access = create_access_token(data={"sub": str(user.id)})

    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw,
        "token_type": "bearer",
    }



# ----- Logout -----

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    token_hash = hash_refresh_token(body.refresh_token)

    token_row = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.token_hash == token_hash)
        .first()
    )

    # Even if it's missing, return 204 (idempotent logout)
    if token_row and token_row.revoked_at is None:
        token_row.revoked_at = now
        db.commit()

    return