"""
API v2 - Timing Advisor Endpoints
Best times for activities based on planetary hours and transits.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..chart_service import build_natal_chart
from ..engine.timing_advisor import (
    ACTIVITY_PROFILES,
    find_best_days,
    get_available_activities,
    get_timing_advice,
)
from ..numerology_engine import build_numerology
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/timing", tags=["Timing"])


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


class TimingAdviceRequest(BaseModel):
    """Request for timing advice."""
    activity: str = Field(
        ...,
        description="Activity type: business_meeting, travel, romance_date, signing_contracts, job_interview, starting_project, creative_work, medical_procedure, financial_decision, meditation_spiritual"
    )
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(40.7128, ge=-90, le=90)
    longitude: float = Field(-74.006, ge=-180, le=180)
    tz: str = Field("UTC", description="Timezone for calculations")


class BestDaysRequest(BaseModel):
    """Request for finding best days."""
    activity: str = Field(..., description="Activity type")
    days_ahead: int = Field(7, ge=1, le=14)
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(40.7128, ge=-90, le=90)
    longitude: float = Field(-74.006, ge=-180, le=180)
    tz: str = Field("UTC")


class TimingScore(BaseModel):
    """Timing score response."""
    score: int
    rating: str
    analysis: Dict[str, Any]
    best_hours: List[Dict[str, Any]]


class BestDay(BaseModel):
    """Best day entry."""
    date: str
    score: int
    rating: str
    highlights: List[str]


@router.post("/advice", response_model=ApiResponse[Dict[str, Any]])
async def get_timing_advice_endpoint(
    request: Request,
    req: TimingAdviceRequest,
):
    """
    Get timing advice for an activity.
    
    ## Parameters
    - **activity**: Type of activity (see activity types)
    - **profile**: Optional birth profile for personalization
    - **latitude/longitude**: Location for planetary hours
    - **tz**: Timezone
    
    ## Response
    Returns score (0-100), rating, and detailed analysis with best hours.
    
    ## Activity Types
    - business_meeting, travel, romance_date
    - signing_contracts, job_interview, starting_project
    - creative_work, medical_procedure, financial_decision
    - meditation_spiritual
    """
    if req.activity not in ACTIVITY_PROFILES:
        valid_activities = list(ACTIVITY_PROFILES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid activity. Valid options: {', '.join(valid_activities)}"
        )

    personal_day = None
    transit_chart = {}

    if req.profile:
        profile_dict = _profile_to_dict(req.profile)
        natal_chart = build_natal_chart(profile_dict)
        transit_chart = natal_chart

        numerology = build_numerology(
            profile_dict["name"],
            profile_dict["date_of_birth"],
            datetime.now(timezone.utc),
        )
        personal_day = numerology.get("personal_day")
    else:
        transit_chart = {"planets": []}

    advice = get_timing_advice(
        activity=req.activity,
        transit_chart=transit_chart,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.tz,
        personal_day=personal_day,
    )
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=advice
    )


@router.post("/best-days", response_model=ApiResponse[Dict[str, Any]])
async def find_best_days_endpoint(
    request: Request,
    req: BestDaysRequest,
):
    """
    Find the best days for an activity in the upcoming period.
    
    ## Response
    Returns sorted list of days with their scores.
    """
    if req.activity not in ACTIVITY_PROFILES:
        valid_activities = list(ACTIVITY_PROFILES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid activity. Valid options: {', '.join(valid_activities)}"
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

    best_days = find_best_days(
        activity=req.activity,
        transit_chart=transit_chart,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.tz,
        days_ahead=req.days_ahead,
        personal_day_cycle=personal_year,
    )
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "activity": req.activity,
            "activity_name": ACTIVITY_PROFILES[req.activity]["name"],
            "days_ahead": req.days_ahead,
            "best_days": best_days,
        }
    )


@router.get("/activities", response_model=ApiResponse[Dict[str, Any]])
async def list_timing_activities(request: Request):
    """
    Get list of supported activities with descriptions.
    
    ## Response
    Returns all available activity types with their favorable conditions.
    """
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"activities": get_available_activities()}
    )
