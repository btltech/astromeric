"""
V1 API Router: Numerology
Provides numerology calculations and profile analysis.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
from ..numerology_engine import build_numerology


# Request models
class ProfilePayload(BaseModel):
    """Profile data for calculations."""

    name: str
    date_of_birth: str
    time_of_birth: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class NumerologyRequest(BaseModel):
    """Request model for numerology profile - supports session-only profiles."""

    profile: ProfilePayload


router = APIRouter()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/numerology", tags=["Numerology"])
def numerology_from_payload(req: NumerologyRequest):
    """Get numerology profile from profile data (no database lookup)."""
    return build_numerology(
        req.profile.name,
        req.profile.date_of_birth,
        datetime.now(timezone.utc),
    )


@router.get("/numerology/profile/{profile_id}", tags=["Numerology"])
def numerology_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get numerology profile for a saved profile (auth + ownership required)."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    return build_numerology(
        profile.name,
        profile.date_of_birth,
        datetime.now(timezone.utc),
    )
