"""
API v2 - Moon Phase Endpoints
Moon phase calculations, rituals, and upcoming lunar events.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from ..chart_service import build_natal_chart
from ..engine.moon_phases import (
    calculate_moon_phase,
    get_moon_phase_summary,
    get_upcoming_moon_events,
)
from ..numerology_engine import build_numerology
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/moon", tags=["Moon"])


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


class MoonPhaseData(BaseModel):
    """Current moon phase information."""
    phase_name: str
    illumination: float
    phase_emoji: str
    days_until_next: int
    next_phase: str


class MoonEvent(BaseModel):
    """Upcoming moon event."""
    date: str
    phase: str
    type: str
    description: str


class MoonRitualData(BaseModel):
    """Moon ritual recommendations."""
    phase: Dict[str, Any]
    ritual: Dict[str, Any]
    crystals: List[str]
    colors: List[str]
    affirmations: List[str]
    natal_insights: Optional[Dict[str, Any]] = None
    numerology_insights: Optional[Dict[str, Any]] = None


class MoonRitualRequest(BaseModel):
    """Request for personalized moon ritual."""
    profile: Optional[ProfilePayload] = None


@router.get("/phase", response_model=ApiResponse[Dict[str, Any]])
async def current_moon_phase(request: Request):
    """
    Get current Moon phase information.
    
    ## Response
    Returns phase name, illumination percentage, and days until next phase.
    
    ## Use Cases
    - Display current moon status
    - Plan activities around lunar cycles
    - Track moon phases for rituals
    """
    phase_data = calculate_moon_phase()
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=phase_data
    )


@router.get("/upcoming", response_model=ApiResponse[Dict[str, Any]])
async def upcoming_moon_events(
    request: Request,
    days: int = Query(30, ge=1, le=90, description="Days to look ahead"),
):
    """
    Get upcoming New and Full Moons.
    
    ## Parameters
    - **days**: Number of days to look ahead (1-90)
    
    ## Response
    Returns list of upcoming lunar events with dates and descriptions.
    """
    events = get_upcoming_moon_events(days)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"events": events, "days_ahead": days}
    )


@router.post("/ritual", response_model=ApiResponse[Dict[str, Any]])
async def moon_ritual(
    request: Request,
    req: MoonRitualRequest = None,
):
    """
    Get personalized Moon phase ritual recommendations.
    
    ## Response
    Includes current phase, ritual activities, crystals, colors, and affirmations.
    If profile provided, adds personalized natal and numerology insights.
    
    ## Use Cases
    - Moon ritual planning
    - Personalized spiritual guidance
    - Timing activities with lunar cycles
    """
    natal_chart = None
    numerology = None

    if req and req.profile:
        profile = _profile_to_dict(req.profile)
        natal_chart = build_natal_chart(profile)
        numerology = build_numerology(
            profile["name"],
            profile["date_of_birth"],
            datetime.now(timezone.utc),
        )

    ritual_data = get_moon_phase_summary(natal_chart, numerology)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=ritual_data
    )
