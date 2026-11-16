"""
FastAPI dependencies: DB session, current user, role-based access control.
"""
from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.auth import verify_access_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode and validate the Bearer JWT, then return the active User ORM object.
    Raises HTTP 401 for invalid/expired tokens and HTTP 403 for inactive accounts.
    """
    token = credentials.credentials
    token_data = verify_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user: User | None = db.get(User, UUID(token_data.sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account.")
    return user


def role_required(*roles: UserRole):
    """
    Factory that returns a dependency enforcing role membership.

    Usage::

        @router.get("/admin-only")
        def admin_view(user=Depends(role_required(UserRole.admin))):
            ...
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role(s): {[r.value for r in roles]}.",
            )
        return current_user

    return _check


def get_admin_user(user: User = Depends(role_required(UserRole.admin))) -> User:
    return user


def get_coordinator_or_admin(
    user: User = Depends(
        role_required(UserRole.admin, UserRole.research_coordinator)
    ),
) -> User:
    return user
