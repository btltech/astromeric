"""
API v2 - Profiles Endpoints
User profile management (create, read, update, delete).
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user, get_current_user_optional
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus
from ..validators import validate_date_of_birth, validate_name

router = APIRouter(prefix="/v2/profiles", tags=["Profiles"])


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
    time_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = "UTC"
    house_system: Optional[str] = "Placidus"


class UpdateProfileRequest(BaseModel):
    """Request to update a profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    time_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    house_system: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile data response."""
    id: int
    name: str
    date_of_birth: str
    time_of_birth: Optional[str]
    place_of_birth: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timezone: str
    house_system: str


def _db_profile_to_dict(profile: DBProfile) -> Dict:
    """Convert DB profile to dict."""
    return {
        "id": profile.id,
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth,
        "place_of_birth": profile.place_of_birth,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "timezone": profile.timezone or "UTC",
        "house_system": profile.house_system or "Placidus",
    }


@router.get("/", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_profiles(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get all profiles for the authenticated user.
    
    Returns empty list for unauthenticated users.
    """
    if current_user:
        profiles = [
            _db_profile_to_dict(p)
            for p in db.query(DBProfile)
            .filter(DBProfile.user_id == current_user.id)
            .all()
        ]
    else:
        profiles = []
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=profiles
    )


@router.post("/", response_model=ApiResponse[Dict[str, Any]])
async def create_profile(
    request: Request,
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new profile.
    
    ## Authentication
    Requires valid JWT token.
    """
    # Validate inputs
    validate_name(req.name)
    validate_date_of_birth(req.date_of_birth)
    
    profile = DBProfile(
        name=req.name,
        date_of_birth=req.date_of_birth,
        time_of_birth=req.time_of_birth,
        place_of_birth=req.place_of_birth,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.timezone or "UTC",
        house_system=req.house_system or "Placidus",
        user_id=current_user.id,
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=_db_profile_to_dict(profile)
    )


@router.get("/{profile_id}", response_model=ApiResponse[Dict[str, Any]])
async def get_profile(
    request: Request,
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific profile by ID."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=_db_profile_to_dict(profile)
    )


@router.put("/{profile_id}", response_model=ApiResponse[Dict[str, Any]])
async def update_profile(
    request: Request,
    profile_id: int,
    req: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing profile."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    # Update fields if provided
    if req.name is not None:
        validate_name(req.name)
        profile.name = req.name
    if req.time_of_birth is not None:
        profile.time_of_birth = req.time_of_birth
    if req.place_of_birth is not None:
        profile.place_of_birth = req.place_of_birth
    if req.latitude is not None:
        profile.latitude = req.latitude
    if req.longitude is not None:
        profile.longitude = req.longitude
    if req.timezone is not None:
        profile.timezone = req.timezone
    if req.house_system is not None:
        profile.house_system = req.house_system
    
    db.commit()
    db.refresh(profile)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=_db_profile_to_dict(profile)
    )


@router.delete("/{profile_id}", response_model=ApiResponse[Dict[str, Any]])
async def delete_profile(
    request: Request,
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a profile."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
    
    db.delete(profile)
    db.commit()
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"message": "Profile deleted", "id": profile_id}
    )
