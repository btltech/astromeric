"""
V1 API Router: Timing Advisor
Provides timing advice, best days for activities, and available activities list.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..chart_service import build_natal_chart
from ..engine.timing_advisor import (
    ACTIVITY_PROFILES,
    find_best_days,
    get_available_activities,
    get_timing_advice,
)
from ..models import SessionLocal
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


class TimingAdviceRequest(BaseModel):
    """Request model for timing advice."""

    activity: str = Field(
        ...,
        description="Activity type: business_meeting, travel, romance_date, signing_contracts, job_interview, starting_project, creative_work, medical_procedure, financial_decision, meditation_spiritual",
    )
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(
        40.7128, ge=-90, le=90, description="Location latitude for planetary hours"
    )
    longitude: float = Field(
        -74.006, ge=-180, le=180, description="Location longitude for planetary hours"
    )
    tz: str = Field("UTC", description="Timezone for calculations")


class BestDaysRequest(BaseModel):
    """Request model for finding best days."""

    activity: str = Field(..., description="Activity type")
    days_ahead: int = Field(7, ge=1, le=14, description="Days to look ahead")
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(40.7128, ge=-90, le=90)
    longitude: float = Field(-74.006, ge=-180, le=180)
    tz: str = Field("UTC", description="Timezone")


router = APIRouter()


def _profile_to_dict(profile: ProfilePayload) -> dict:
    """Convert ProfilePayload to dictionary for engine functions."""
    return {
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth or "12:00",
        "location": profile.location or "Unknown",
        "latitude": profile.latitude or 40.7128,
        "longitude": profile.longitude or -74.006,
    }


@router.post("/timing/advice", tags=["Timing"])
def get_timing_advice_endpoint(req: TimingAdviceRequest):
    """
    Get timing advice for an activity, including today's score and best upcoming days.
    Analyzes planetary hours, Moon phase, Moon sign, VOC Moon, and retrogrades.
    Returns score (0-100), rating, and detailed analysis with best hours.
    """
    if req.activity not in ACTIVITY_PROFILES:
        valid_activities = list(ACTIVITY_PROFILES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid activity. Valid options: {', '.join(valid_activities)}",
        )

    personal_day = None
    transit_chart = {}

    if req.profile:
        profile_dict = _profile_to_dict(req.profile)
        natal_chart = build_natal_chart(profile_dict)
        transit_chart = natal_chart

        # Get personal day from numerology
        numerology = build_numerology(
            profile_dict["name"],
            profile_dict["date_of_birth"],
            datetime.now(timezone.utc),
        )
        personal_day = numerology.get("personal_day")
    else:
        transit_chart = {"planets": []}

    return get_timing_advice(
        activity=req.activity,
        transit_chart=transit_chart,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.tz,
        personal_day=personal_day,
    )


@router.post("/timing/best-days", tags=["Timing"])
def find_best_days_endpoint(req: BestDaysRequest):
    """
    Find the best days for an activity in the upcoming period.
    Returns sorted list of days with their scores.
    """
    if req.activity not in ACTIVITY_PROFILES:
        valid_activities = list(ACTIVITY_PROFILES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid activity. Valid options: {', '.join(valid_activities)}",
        )

    personal_year = None
    transit_chart = {}

    if req.profile:
        profile_dict = _profile_to_dict(req.profile)
        transit_chart = build_natal_chart(profile_dict)

        numerology = build_numerology(
            profile_dict["name"],
            profile_dict["date_of_birth"],
            datetime.now(timezone.utc),
        )
        personal_year = numerology.get("personal_year")
    else:
        transit_chart = {"planets": []}

    return {
        "activity": req.activity,
        "activity_name": ACTIVITY_PROFILES[req.activity]["name"],
        "days_ahead": req.days_ahead,
        "best_days": find_best_days(
            activity=req.activity,
            transit_chart=transit_chart,
            latitude=req.latitude,
            longitude=req.longitude,
            timezone=req.tz,
            days_ahead=req.days_ahead,
            personal_day_cycle=personal_year,
        ),
    }


@router.get("/timing/activities", tags=["Timing"])
def list_timing_activities():
    """
    Get list of supported activities with their descriptions and favorable conditions.
    """
    return {"activities": get_available_activities()}
