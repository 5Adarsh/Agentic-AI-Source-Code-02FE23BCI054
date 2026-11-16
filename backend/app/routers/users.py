"""
Users router — admin-only CRUD for user accounts.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.utils.auth import hash_password
from app.utils.pagination import paginate

router = APIRouter()


@router.get("/", response_model=List[UserOut], summary="List all users (admin)")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="Create user (admin)")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut, summary="Get user by ID (admin)")
def get_user(user_id: UUID, db: Session = Depends(get_db), _admin=Depends(get_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserOut, summary="Update user (admin)")
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    update_data = payload.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for key, val in update_data.items():
        setattr(user, key, val)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (admin)")
def delete_user(user_id: UUID, db: Session = Depends(get_db), _admin=Depends(get_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    db.delete(user)
    db.commit()
