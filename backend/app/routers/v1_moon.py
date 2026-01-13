"""
V1 Moon Router
API v1 moon phase and ritual endpoints
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..chart_service import build_natal_chart
from ..engine.moon_phases import (
    calculate_moon_phase,
    get_moon_phase_summary,
    get_upcoming_moon_events,
)
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


class MoonRitualRequest(BaseModel):
    """Request model for personalized Moon ritual."""

    profile: Optional[ProfilePayload] = None


router = APIRouter(prefix="/moon", tags=["Moon"])


def _profile_to_dict(payload: ProfilePayload) -> dict:
    """Convert ProfilePayload to dictionary for engine functions."""
    return {
        "name": payload.name,
        "date_of_birth": payload.date_of_birth,
        "time_of_birth": payload.time_of_birth or "12:00",
        "location": payload.location or "Unknown",
        "latitude": payload.latitude or 40.7128,
        "longitude": payload.longitude or -74.006,
    }


@router.get("/phase")
def current_moon_phase():
    """Get current Moon phase information."""
    return calculate_moon_phase()


@router.get("/upcoming")
def upcoming_moon_events(days: int = Query(30, ge=1, le=90)):
    """Get upcoming New and Full Moons."""
    return {"events": get_upcoming_moon_events(days)}


@router.post("/moon-ritual")
def moon_ritual(req: MoonRitualRequest = None):
    """
    Get personalized Moon phase ritual recommendations.
    Includes current phase, ritual activities, crystals, colors, and affirmations.
    If profile provided, adds personalized natal and numerology insights.
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

    return get_moon_phase_summary(natal_chart, numerology)
