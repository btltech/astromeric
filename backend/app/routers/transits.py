"""
API v2 - Transit Endpoints
Daily transit alerts and astronomical events.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user, get_current_user_optional
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
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
            raise HTTPException(status_code=403, detail="Not authorized to view this profile")
        
        profile = _db_profile_to_dict(profile_obj)
    else:
        profile = _profile_to_dict(req.profile)

    transits = check_daily_transits(profile)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=transits
    )


@router.post("/subscribe", response_model=ApiResponse[Dict[str, Any]])
async def subscribe_transit_alerts(
    request: Request,
    profile_id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Subscribe to daily transit alert emails.
    
    ## Note
    Currently not implemented - returns 501 status.
    """
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your profile")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transit alert subscriptions are not implemented yet",
    )
