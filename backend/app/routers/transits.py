"""
API v2 - Transit Endpoints
Daily transit alerts and astronomical events.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..models import Profile as DBProfile
from ..models import SessionLocal, TransitSubscription, User
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/transits", tags=["Transits"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _profile_to_dict(payload: ProfilePayload) -> Dict:
    """Convert ProfilePayload to dict."""
    return {
        "name": payload.name,
        "date_of_birth": payload.date_of_birth,
        "time_of_birth": payload.time_of_birth or "12:00",
        "latitude": payload.latitude or 0.0,
        "longitude": payload.longitude or 0.0,
        "timezone": payload.timezone or "UTC",
    }


def _db_profile_to_dict(profile: DBProfile) -> Dict:
    """Convert DB profile to dict."""
    return {
        "id": profile.id,
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth,
        "place_of_birth": profile.place_of_birth,
        "latitude": profile.latitude or 0.0,
        "longitude": profile.longitude or 0.0,
        "timezone": profile.timezone or "UTC",
        "house_system": profile.house_system or "Placidus",
    }


class TransitRequest(BaseModel):
    """Request for transit data."""

    profile: ProfilePayload


class TransitSubscriptionRequest(BaseModel):
    """Request to subscribe to transit alerts."""

    email: str
    profile_id: Optional[int] = None
    profile: Optional[ProfilePayload] = None


def _resolve_subscription_profile(
    *,
    request: TransitSubscriptionRequest,
    db: Session,
    current_user: Optional[User],
) -> DBProfile:
    if request.profile_id is not None:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        profile = db.query(DBProfile).filter(DBProfile.id == request.profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your profile")
        return profile

    if request.profile is None:
        raise HTTPException(
            status_code=400, detail="profile_id or profile payload is required"
        )

    payload = request.profile
    query = db.query(DBProfile).filter(
        DBProfile.user_id == (current_user.id if current_user else None),
        DBProfile.name == payload.name,
        DBProfile.date_of_birth == payload.date_of_birth,
        DBProfile.time_of_birth == payload.time_of_birth,
        DBProfile.place_of_birth == payload.place_of_birth,
        DBProfile.latitude == payload.latitude,
        DBProfile.longitude == payload.longitude,
        DBProfile.timezone == (payload.timezone or "UTC"),
        DBProfile.house_system == (payload.house_system or "Placidus"),
    )
    existing_profile = query.first()
    if existing_profile:
        return existing_profile

    profile = DBProfile(
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        time_of_birth=payload.time_of_birth,
        time_confidence=payload.time_confidence
        or ("exact" if payload.time_of_birth else "unknown"),
        place_of_birth=payload.place_of_birth,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone=payload.timezone or "UTC",
        house_system=payload.house_system or "Placidus",
        user_id=current_user.id if current_user else None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/daily", response_model=ApiResponse[Dict[str, Any]])
async def get_daily_transits(
    request: Request,
    req: TransitRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get today's transit aspects for a profile.

    ## Authentication
    Required when using a stored profile_id.
    """
    from ..transit_alerts import check_daily_transits

    if hasattr(req.profile, "id") and req.profile.id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        profile_obj = db.query(DBProfile).filter(DBProfile.id == req.profile.id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to view this profile"
            )

        profile = _db_profile_to_dict(profile_obj)
    else:
        profile = _profile_to_dict(req.profile)

    transits = check_daily_transits(profile)

    return ApiResponse(status=ResponseStatus.SUCCESS, data=transits)


@router.post("/upcoming-exact", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_upcoming_exact_transits(
    request: Request,
    req: TransitRequest,
    days_ahead: int = 7,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get upcoming exact transit-to-natal aspects for the next N days.

    Uses ad-hoc profile payloads for local-first clients and ownership checks for
    stored profile references, matching the daily transit contract.
    """
    from ..transit_alerts import find_future_exact_transits

    if hasattr(req.profile, "id") and req.profile.id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        profile_obj = db.query(DBProfile).filter(DBProfile.id == req.profile.id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to view this profile"
            )

        profile = _db_profile_to_dict(profile_obj)
    else:
        profile = _profile_to_dict(req.profile)

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=find_future_exact_transits(profile=profile, days_ahead=days_ahead),
    )


@router.post("/subscribe", response_model=ApiResponse[Dict[str, Any]])
async def subscribe_transit_alerts(
    request: Request,
    req: TransitSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Subscribe to daily transit alert emails.

    Supports either an authenticated stored profile or a local-first inline
    profile payload. Inline payloads are materialized into a server profile row
    so subscriptions can work without breaking the current schema.
    """
    profile = _resolve_subscription_profile(
        request=req, db=db, current_user=current_user
    )

    sub = (
        db.query(TransitSubscription)
        .filter(
            TransitSubscription.profile_id == profile.id,
            TransitSubscription.email == req.email,
        )
        .first()
    )
    if not sub:
        sub = TransitSubscription(profile_id=profile.id, email=req.email)
        db.add(sub)
        db.commit()

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"profile_id": profile.id, "email": req.email, "subscribed": True},
    )
