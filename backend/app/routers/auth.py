"""
API v2 - Auth Endpoints
Standardized authentication endpoints with JWT tokens.
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
    get_user_by_email,
)
from ..models import SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/auth", tags=["Auth"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserInfo(BaseModel):
    """User information response."""

    id: str
    email: str
    is_paid: bool


class TokenResponse(BaseModel):
    """Token response with user info."""

    access_token: str
    token_type: str
    user: UserInfo


@router.post("/register", response_model=ApiResponse[TokenResponse])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    ## Rate Limit
    3 requests per minute to prevent spam registrations.

    ## Response
    Returns JWT token and user info on successful registration.
    """
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

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(id=user.id, email=user.email, is_paid=user.is_paid),
        ),
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    ## Rate Limit
    5 requests per minute to prevent brute force attacks.
    """
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

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(id=user.id, email=user.email, is_paid=user.is_paid),
        ),
    )


@router.get("/me", response_model=ApiResponse[UserInfo])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=UserInfo(
            id=current_user.id, email=current_user.email, is_paid=current_user.is_paid
        ),
    )


@router.post("/activate-premium", response_model=ApiResponse[Dict[str, Any]])
def activate_premium(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Activate premium subscription for admin users.

    Only users listed in ADMIN_EMAILS environment variable can use this endpoint.
    """
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    if not admin_emails or current_user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == current_user.id).first()
    user.is_paid = True
    db.commit()
    db.refresh(user)

    return ApiResponse(
        status=ResponseStatus.SUCCESS, data={"success": True, "is_paid": user.is_paid}
    )
