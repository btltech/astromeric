"""
V1 Readings Router
API v1 reading endpoints (daily, weekly, monthly, forecasts, natal, compatibility)
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user, get_current_user_optional
from ..chart_service import build_natal_chart
from ..engine.year_ahead import build_year_ahead_forecast
from ..models import Profile as DBProfile
from ..models import SectionFeedback, SessionLocal, User
from ..products import build_compatibility, build_forecast, build_natal_profile
from ..schemas import ProfilePayload

router = APIRouter(tags=["Readings"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _profile_to_dict(profile: ProfilePayload):
    """Convert ProfilePayload to dict."""
    return {
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth or "12:00:00",
        "latitude": profile.latitude or 0.0,
        "longitude": profile.longitude or 0.0,
        "timezone": profile.timezone or "UTC",
    }


def _db_profile_to_dict(profile: DBProfile):
    """Convert DBProfile to dict."""
    return {
        "id": profile.id,
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth or "12:00:00",
        "place_of_birth": profile.place_of_birth,
        "latitude": profile.latitude or 0.0,
        "longitude": profile.longitude or 0.0,
        "timezone": profile.timezone or "UTC",
        "house_system": profile.house_system,
    }


# ========== REQUEST MODELS ==========


class DailyRequest(BaseModel):
    """Request for daily reading."""

    profile: ProfilePayload
    lang: str = "en"


class WeeklyRequest(BaseModel):
    """Request for weekly reading."""

    profile: ProfilePayload
    lang: str = "en"


class MonthlyRequest(BaseModel):
    """Request for monthly reading."""

    profile: ProfilePayload
    lang: str = "en"


class ForecastRequest(BaseModel):
    """Request for generic forecast."""

    profile: Optional[ProfilePayload] = None
    profile_id: Optional[int] = None
    scope: str = "daily"
    lang: str = "en"


class SectionFeedbackRequest(BaseModel):
    """Request for section feedback."""

    profile_id: Optional[int] = None
    scope: str
    section: str
    vote: str  # "up" or "down"


class NatalRequest(BaseModel):
    """Request for natal profile."""

    profile: ProfilePayload
    lang: str = "en"


class CompatibilityRequest(BaseModel):
    """Request for compatibility analysis."""

    person_a: ProfilePayload
    person_b: ProfilePayload
    lang: str = "en"


class YearAheadRequest(BaseModel):
    """Request for year-ahead forecast."""

    profile: ProfilePayload
    year: Optional[int] = Field(None, description="Year for forecast")


# ========== ENDPOINTS ==========


@router.post("/daily-reading")
def daily_reading(req: DailyRequest):
    """Get a daily astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="daily", lang=req.lang)


@router.post("/weekly-reading")
def weekly_reading(req: WeeklyRequest):
    """Get a weekly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="weekly", lang=req.lang)


@router.post("/monthly-reading")
def monthly_reading(req: MonthlyRequest):
    """Get a monthly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="monthly", lang=req.lang)


@router.post("/forecast")
def generic_forecast(
    req: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get a forecast for any scope (daily, weekly, monthly)."""
    if req.profile:
        profile = _profile_to_dict(req.profile)
    elif req.profile_id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        profile_obj = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this profile"
            )
        profile = _db_profile_to_dict(profile_obj)
    else:
        raise HTTPException(status_code=400, detail="Profile data is required")
    return build_forecast(profile, scope=req.scope, lang=req.lang)


@router.post("/feedback/section")
def submit_section_feedback(
    req: SectionFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Capture feedback for a reading section."""
    profile_id: Optional[int] = None
    if req.profile_id is not None:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        profile = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        profile_id = profile.id

    feedback_row = SectionFeedback(
        profile_id=profile_id,
        scope=req.scope,
        section=req.section,
        vote=req.vote,
    )
    db.add(feedback_row)
    db.commit()

    return {"status": "ok"}


@router.post("/natal-profile")
def natal_profile(req: NatalRequest):
    """Get a complete natal profile including chart and interpretations."""
    profile = _profile_to_dict(req.profile)
    return build_natal_profile(profile, lang=req.lang)


@router.post("/compatibility")
def compatibility(req: CompatibilityRequest):
    """Get compatibility analysis between two people."""
    a = _profile_to_dict(req.person_a)
    b = _profile_to_dict(req.person_b)
    return build_compatibility(a, b, lang=req.lang)


@router.post("/year-ahead")
def year_ahead_forecast(req: YearAheadRequest):
    """Get comprehensive year-ahead forecast."""
    profile = _profile_to_dict(req.profile)
    natal = build_natal_chart(profile)
    year = req.year or datetime.now().year

    return build_year_ahead_forecast(profile, natal, year)
