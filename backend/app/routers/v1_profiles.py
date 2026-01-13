"""
V1 Profiles Router
API v1 profile endpoints (CRUD operations for saved profiles)
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user, get_current_user_optional
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
from ..validators import validate_profile_data

router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CreateProfileRequest(BaseModel):
    """Request to create a new profile."""

    name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")
    time_of_birth: Optional[str] = Field(None)
    place_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = "UTC"
    house_system: Optional[str] = "Placidus"


def _db_profile_to_dict(p: DBProfile):
    """Convert DBProfile to dict."""
    return {
        "id": p.id,
        "name": p.name,
        "date_of_birth": p.date_of_birth,
        "time_of_birth": p.time_of_birth,
        "place_of_birth": p.place_of_birth,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "timezone": p.timezone,
        "house_system": p.house_system,
    }


@router.get("")
def get_profiles(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get all saved profiles for current user."""
    if current_user:
        return [
            _db_profile_to_dict(p)
            for p in db.query(DBProfile)
            .filter(DBProfile.user_id == current_user.id)
            .all()
        ]
    return []


@router.post("")
def create_profile(
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new profile (auth required)."""
    # Validate incoming data
    validated = validate_profile_data(
        {
            "name": req.name,
            "date_of_birth": req.date_of_birth,
            "time_of_birth": req.time_of_birth,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "timezone": req.timezone,
            "house_system": req.house_system,
        }
    )

    # Validate place string
    place_of_birth = (req.place_of_birth or "").strip() or None
    if place_of_birth and len(place_of_birth) > 200:
        raise HTTPException(status_code=400, detail="Place of birth is too long")

    db_profile = DBProfile(
        name=validated["name"],
        date_of_birth=validated["date_of_birth"],
        time_of_birth=validated["time_of_birth"],
        place_of_birth=place_of_birth,
        latitude=validated["latitude"],
        longitude=validated["longitude"],
        timezone=validated["timezone"],
        house_system=validated["house_system"],
        user_id=current_user.id,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return _db_profile_to_dict(db_profile)


@router.get("/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get a specific profile."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Allow viewing if owned by user or is public
    if profile.user_id and profile.user_id != (
        current_user.id if current_user else None
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    return _db_profile_to_dict(profile)


@router.put("/{profile_id}")
def update_profile(
    profile_id: int,
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing profile (auth required)."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this profile"
        )

    # Validate incoming data
    validated = validate_profile_data(
        {
            "name": req.name,
            "date_of_birth": req.date_of_birth,
            "time_of_birth": req.time_of_birth,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "timezone": req.timezone,
            "house_system": req.house_system,
        }
    )

    profile.name = validated["name"]
    profile.date_of_birth = validated["date_of_birth"]
    profile.time_of_birth = validated["time_of_birth"]
    profile.latitude = validated["latitude"]
    profile.longitude = validated["longitude"]
    profile.timezone = validated["timezone"]
    profile.house_system = validated["house_system"]
    profile.place_of_birth = (req.place_of_birth or "").strip() or None

    db.commit()
    db.refresh(profile)

    return _db_profile_to_dict(profile)


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a profile (auth required)."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this profile"
        )

    db.delete(profile)
    db.commit()

    return {"status": "ok"}
