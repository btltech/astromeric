"""
V1 Auth Router
API v1 authentication endpoints (register, login, user management)
"""

import os
from datetime import timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserCreate,
    UserLogin,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_current_user_optional,
    get_user_by_email,
)
from ..migration_service import migrate_anon_readings, sync_anon_profile_to_account
from ..models import SessionLocal, User

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MigrateReadingsRequest(BaseModel):
    """Request to migrate anonymous readings to account."""

    readings: List[Dict[str, Any]]
    profile: Optional[Dict[str, Any]] = None


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = create_user(db, user_data)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "is_paid": user.is_paid},
    }


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a token."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "is_paid": user.is_paid},
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_paid": current_user.is_paid,
    }


@router.post("/activate-premium")
def activate_premium(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Activate premium for site owner only."""
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    if not admin_emails or current_user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Re-fetch the user from this session to ensure it's attached
    user = db.query(User).filter(User.id == current_user.id).first()
    user.is_paid = True
    db.commit()
    db.refresh(user)
    return {"success": True, "is_paid": user.is_paid}


@router.post("/migrate-anon-readings")
def migrate_anonymous_readings(
    req: MigrateReadingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Migrate anonymous readings from localStorage to authenticated user account.

    Called after user signs up with localStorage anon readings.
    """
    # Re-fetch user to ensure it's in this session
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optionally create a profile from the anonymous profile data
    profile_id = None
    if req.profile:
        profile = sync_anon_profile_to_account(db, user, req.profile)
        if profile:
            profile_id = profile.id

    # Migrate the readings
    result = migrate_anon_readings(db, user, req.readings, profile_id)

    return {
        "status": "success",
        "migrations": result,
        "profile_created": profile_id is not None,
    }
