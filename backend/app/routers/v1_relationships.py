"""
V1 API Router: Relationships
Provides relationship timeline analysis, timing advice, and Venus transit information.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from ..engine.relationship_timeline import (
    build_relationship_timeline,
    analyze_relationship_timing,
    get_best_relationship_days,
    get_upcoming_relationship_dates,
    get_venus_transit,
    get_mars_transit,
    is_venus_retrograde,
    get_relationship_phases,
)

# Request models
class RelationshipTimelineRequest(BaseModel):
    """Request for relationship timeline."""
    sun_sign: str = Field(..., pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    partner_sign: Optional[str] = Field(default=None, pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    months_ahead: int = Field(default=6, ge=1, le=12)


class RelationshipTimingRequest(BaseModel):
    """Request for single day relationship timing analysis."""
    sun_sign: str = Field(..., pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    partner_sign: Optional[str] = Field(default=None, pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    date: Optional[str] = Field(default=None, description="Date to analyze (YYYY-MM-DD)")


router = APIRouter()


@router.post("/relationship/timeline", tags=["Relationships"])
def get_relationship_timeline(req: RelationshipTimelineRequest):
    """
    Get a comprehensive relationship timeline with key dates, events,
    and best days for love and relationships.
    """
    timeline = build_relationship_timeline(
        sun_sign=req.sun_sign,
        partner_sign=req.partner_sign,
        start_date=datetime.now(timezone.utc),
        months_ahead=req.months_ahead
    )
    return timeline


@router.post("/relationship/timing", tags=["Relationships"])
def get_relationship_timing(req: RelationshipTimingRequest):
    """
    Analyze relationship timing for a specific date.
    Returns Venus/Mars transits, retrograde status, and timing score.
    """
    if req.date:
        try:
            check_date = datetime.fromisoformat(req.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        check_date = datetime.now(timezone.utc)
    
    analysis = analyze_relationship_timing(check_date, req.sun_sign, req.partner_sign)
    return analysis


@router.get("/relationship/best-days/{sun_sign}", tags=["Relationships"])
def get_best_days_for_love(
    sun_sign: str,
    days_ahead: int = Query(default=30, ge=7, le=90)
):
    """
    Find the best days for relationship activities in the coming period.
    Returns days sorted by relationship score.
    """
    valid_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                   "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    if sun_sign not in valid_signs:
        raise HTTPException(status_code=400, detail=f"Invalid sign. Must be one of: {valid_signs}")
    
    best_days = get_best_relationship_days(
        start_date=datetime.now(timezone.utc),
        sun_sign=sun_sign,
        days_ahead=days_ahead
    )
    
    return {
        "sun_sign": sun_sign,
        "days_ahead": days_ahead,
        "best_days": best_days[:10],
        "top_day": best_days[0] if best_days else None
    }


@router.get("/relationship/events", tags=["Relationships"])
def get_relationship_events(
    days_ahead: int = Query(default=90, ge=30, le=365),
    sun_sign: Optional[str] = Query(default=None, description="Sun sign for personalized events")
):
    """
    Get upcoming relationship-focused astrological events.
    Includes Venus/Mars transits, retrogrades, and eclipses.
    """
    events = get_upcoming_relationship_dates(
        start_date=datetime.now(timezone.utc),
        days_ahead=days_ahead,
        sun_sign=sun_sign
    )
    
    return {
        "days_ahead": days_ahead,
        "sun_sign": sun_sign,
        "total_events": len(events),
        "events": events
    }


@router.get("/relationship/venus-status", tags=["Relationships"])
def get_venus_status():
    """
    Get current Venus transit and retrograde status.
    Essential for relationship timing.
    """
    now = datetime.now(timezone.utc)
    venus = get_venus_transit(now)
    mars = get_mars_transit(now)
    retrograde = is_venus_retrograde(now)
    
    return {
        "date": now.strftime("%Y-%m-%d"),
        "venus": venus,
        "mars": mars,
        "venus_retrograde": retrograde
    }


@router.get("/relationship/phases", tags=["Relationships"])
def get_phases():
    """
    Get information about relationship phases and their astrological houses.
    """
    return get_relationship_phases()
