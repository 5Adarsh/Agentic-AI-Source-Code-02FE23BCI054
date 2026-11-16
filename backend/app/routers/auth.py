"""
Auth router — login, refresh, logout endpoints.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, RefreshRequest, Token, UserOut
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_refresh_token,
)
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token, summary="Obtain JWT access and refresh tokens")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user: User | None = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account.")

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token, summary="Exchange a refresh token for new tokens")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_data = verify_refresh_token(payload.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token."
        )
    from uuid import UUID
    user: User | None = db.get(User, UUID(token_data.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    new_refresh = create_refresh_token({"sub": str(user.id), "role": user.role.value})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", summary="Logout (client-side token invalidation)")
def logout():
    """
    Stateless JWT — advise client to discard tokens.
    Phase 2: implement Redis token blocklist.
    """
    return {"detail": "Successfully logged out. Please discard your tokens."}


from app.dependencies import get_current_user

@router.get("/me", response_model=UserOut, summary="Get current authenticated user")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the current active authenticated user."""
    return current_user
