"""
API v2 - Auth Endpoints
Standardized authentication endpoints with JWT tokens.
"""

import os
import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from jose import jwt as jose_jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserCreate,
    UserLogin,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_user_by_email,
)
from ..models import (
    DeviceToken,
    Favourite,
    Preference,
    Profile,
    Reading,
    SectionFeedback,
    SessionLocal,
    TransitSubscription,
    User,
)
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/auth", tags=["Auth"])


# ============================================================================
# RESPONSE MODELS (must be defined before use in route decorators)
# ============================================================================


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


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apple Sign-In configuration
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
APPLE_BUNDLE_ID = os.getenv("APPLE_BUNDLE_ID", "com.astromeric.app")

# Cache for Apple's public keys
_apple_keys_cache: Optional[Dict] = None


async def get_apple_public_keys() -> Dict:
    """Fetch Apple's public keys for token verification."""
    global _apple_keys_cache

    if _apple_keys_cache is not None:
        return _apple_keys_cache

    async with httpx.AsyncClient() as client:
        response = await client.get(APPLE_KEYS_URL)
        response.raise_for_status()
        _apple_keys_cache = response.json()
        return _apple_keys_cache


def verify_apple_token(identity_token: str, keys: Dict) -> Optional[Dict]:
    """Verify Apple identity token and return claims."""
    try:
        # Get the key ID from the token header
        unverified_header = jose_jwt.get_unverified_header(identity_token)
        kid = unverified_header.get("kid")

        if not kid:
            return None

        # Find the matching key
        key = None
        for k in keys.get("keys", []):
            if k.get("kid") == kid:
                key = k
                break

        if not key:
            return None

        # Verify and decode the token
        from jose import jwk

        public_key = jwk.construct(key)

        claims = jose_jwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=APPLE_BUNDLE_ID,
            issuer=APPLE_ISSUER,
        )

        return claims
    except JWTError as e:
        print(f"Apple token verification failed: {e}")
        return None
    except Exception as e:
        print(f"Apple token verification error: {e}")
        return None


class AppleAuthRequest(BaseModel):
    """Apple Sign-In request."""

    identity_token: str
    user_identifier: str
    email: Optional[str] = None
    full_name: Optional[str] = None


@router.post("/apple", response_model=ApiResponse[TokenResponse])
async def apple_sign_in(request: AppleAuthRequest, db: Session = Depends(get_db)):
    """
    Sign in with Apple.

    Accepts the identity token from ASAuthorizationAppleIDCredential,
    verifies it against Apple's public keys, and returns a JWT.

    ## Request Body
    - `identity_token`: The identity token from Apple (required)
    - `user_identifier`: The Apple user identifier (required)
    - `email`: User's email (optional, only provided on first sign-in)
    - `full_name`: User's full name (optional, only provided on first sign-in)

    ## Response
    Returns JWT token and user info on successful authentication.
    """
    # Get Apple's public keys
    try:
        apple_keys = await get_apple_public_keys()
    except Exception as e:
        print(f"Failed to fetch Apple keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify Apple credentials at this time",
        )

    # Verify the identity token
    claims = verify_apple_token(request.identity_token, apple_keys)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple identity token",
        )

    # Extract user info from token claims
    apple_user_id = claims.get("sub")
    token_email = claims.get("email")

    # Use email from token, falling back to request
    email = token_email or request.email

    if not apple_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing user identifier",
        )

    # Look up user by Apple ID (stored in external_id field) or email
    user = db.query(User).filter(User.external_id == apple_user_id).first()

    if not user and email:
        # Try to find by email
        user = get_user_by_email(db, email)
        if user:
            # Link Apple ID to existing account
            user.external_id = apple_user_id
            user.auth_provider = "apple"
            db.commit()

    if not user:
        # Create new user
        if not email:
            # Generate a placeholder email if Apple didn't provide one
            email = f"{apple_user_id[:8]}@privaterelay.appleid.com"

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password="",  # No password for Apple users
            external_id=apple_user_id,
            auth_provider="apple",
            full_name=request.full_name,
            is_active=True,
            is_paid=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create JWT token
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


@router.delete("/account", response_model=ApiResponse[Dict[str, Any]])
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Permanently delete the current user's account and associated server data.

    This endpoint exists to satisfy App Store account-deletion requirements for apps
    that support account creation.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile_ids = [
        p.id for p in db.query(Profile).filter(Profile.user_id == user.id).all()
    ]

    try:
        if profile_ids:
            db.query(Favourite).filter(Favourite.profile_id.in_(profile_ids)).delete(
                synchronize_session=False
            )
            db.query(Preference).filter(Preference.profile_id.in_(profile_ids)).delete(
                synchronize_session=False
            )
            db.query(TransitSubscription).filter(
                TransitSubscription.profile_id.in_(profile_ids)
            ).delete(synchronize_session=False)
            db.query(SectionFeedback).filter(
                SectionFeedback.profile_id.in_(profile_ids)
            ).delete(synchronize_session=False)

            # Readings must be removed after favourites (FK to readings).
            db.query(Reading).filter(Reading.profile_id.in_(profile_ids)).delete(
                synchronize_session=False
            )
            db.query(Profile).filter(Profile.id.in_(profile_ids)).delete(
                synchronize_session=False
            )

        db.query(DeviceToken).filter(DeviceToken.user_id == user.id).delete(
            synchronize_session=False
        )
        db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete account: {type(e).__name__}",
        )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"success": True, "message": "Account deleted"},
    )


class ChangePasswordRequest(BaseModel):
    """Request to change password when logged in."""

    current_password: str
    new_password: str


@router.post("/change-password", response_model=ApiResponse[Dict[str, Any]])
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change password for the currently logged-in user.

    Requires current password for verification.
    """
    from ..auth import get_password_hash, verify_password

    # Verify current password
    user = db.query(User).filter(User.id == current_user.id).first()
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=400, detail="New password must be at least 8 characters"
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"success": True, "message": "Password changed successfully"},
    )


# ========== PASSWORD RESET ENDPOINTS ==========


class ForgotPasswordRequest(BaseModel):
    """Request to send password reset email."""

    email: str


class ResetPasswordRequest(BaseModel):
    """Request to reset password with token."""

    token: str
    new_password: str


@router.post("/forgot-password", response_model=ApiResponse[Dict[str, Any]])
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset email.

    Sends an email with a reset link if the email exists.
    Always returns success to prevent email enumeration.
    """
    from ..email_service import generate_reset_token, send_password_reset_email

    user = get_user_by_email(db, request.email)

    # Always return success to prevent email enumeration attacks
    if user:
        token = generate_reset_token(request.email)
        send_password_reset_email(request.email, token)

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "success": True,
            "message": "If an account with that email exists, we've sent a password reset link.",
        },
    )


@router.post("/reset-password", response_model=ApiResponse[Dict[str, Any]])
def reset_password_with_token(
    request: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """
    Reset password using a token from the reset email.
    """
    from ..auth import get_password_hash
    from ..email_service import consume_reset_token

    # Verify and consume the token
    email = consume_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token. Please request a new password reset.",
        )

    # Find the user
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "success": True,
            "message": "Password reset successfully. You can now log in.",
        },
    )
