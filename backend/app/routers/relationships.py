"""
API v2 - Relationship Endpoints
Relationship timing, Venus transits, and romantic date planning.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..engine.relationship_timeline import (
    analyze_relationship_timing,
    build_relationship_timeline,
    get_best_relationship_days,
    get_mars_transit,
    get_relationship_phases,
    get_upcoming_relationship_dates,
    get_venus_transit,
    is_venus_retrograde,
)
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/relationships", tags=["Relationships"])

VALID_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


class RelationshipTimelineRequest(BaseModel):
    """Request for relationship timeline."""
    sun_sign: str = Field(..., pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    partner_sign: Optional[str] = Field(default=None, pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    months_ahead: int = Field(default=6, ge=1, le=12)


class RelationshipTimingRequest(BaseModel):
    """Request for relationship timing analysis."""
    sun_sign: str = Field(..., pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    partner_sign: Optional[str] = Field(default=None, pattern="^(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)$")
    date: Optional[str] = Field(default=None, description="Date to analyze (YYYY-MM-DD)")


@router.post("/timeline", response_model=ApiResponse[Dict[str, Any]])
async def get_relationship_timeline(
    request: Request,
    req: RelationshipTimelineRequest,
):
    """
    Get a comprehensive relationship timeline.
    
    ## Response
    Returns key dates, events, and best days for love and relationships.
    
    ## Use Cases
    - Plan romantic dates
    - Understand relationship cycles
    - Navigate Venus transits
    """
    timeline = build_relationship_timeline(
        sun_sign=req.sun_sign,
        partner_sign=req.partner_sign,
        start_date=datetime.now(timezone.utc),
        months_ahead=req.months_ahead,
    )
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=timeline
    )


@router.post("/timing", response_model=ApiResponse[Dict[str, Any]])
async def get_relationship_timing(
    request: Request,
    req: RelationshipTimingRequest,
):
    """
    Analyze relationship timing for a specific date.
    
    ## Response
    Returns Venus/Mars transits, retrograde status, and timing score.
    """
    if req.date:
        try:
            check_date = datetime.fromisoformat(req.date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        check_date = datetime.now(timezone.utc)

    analysis = analyze_relationship_timing(check_date, req.sun_sign, req.partner_sign)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=analysis
    )


@router.get("/best-days/{sun_sign}", response_model=ApiResponse[Dict[str, Any]])
async def get_best_days_for_love(
    request: Request,
    sun_sign: str,
    days_ahead: int = Query(default=30, ge=7, le=90),
):
    """
    Find the best days for relationship activities.
    
    ## Response
    Returns days sorted by relationship score (top 10).
    """
    if sun_sign not in VALID_SIGNS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sign. Must be one of: {VALID_SIGNS}"
        )

    best_days = get_best_relationship_days(
        start_date=datetime.now(timezone.utc),
        sun_sign=sun_sign,
        days_ahead=days_ahead
    )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "sun_sign": sun_sign,
            "days_ahead": days_ahead,
            "best_days": best_days[:10],
            "top_day": best_days[0] if best_days else None,
        }
    )


@router.get("/events", response_model=ApiResponse[Dict[str, Any]])
async def get_relationship_events(
    request: Request,
    days_ahead: int = Query(default=90, ge=30, le=365),
    sun_sign: Optional[str] = Query(default=None),
):
    """
    Get upcoming relationship-focused astrological events.
    
    ## Response
    Includes Venus/Mars transits, retrogrades, and eclipses.
    """
    events = get_upcoming_relationship_dates(
        start_date=datetime.now(timezone.utc),
        days_ahead=days_ahead,
        sun_sign=sun_sign
    )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "days_ahead": days_ahead,
            "sun_sign": sun_sign,
            "total_events": len(events),
            "events": events,
        }
    )


@router.get("/venus-status", response_model=ApiResponse[Dict[str, Any]])
async def get_venus_status(request: Request):
    """
    Get current Venus transit and retrograde status.
    
    Essential for relationship timing.
    """
    now = datetime.now(timezone.utc)
    venus = get_venus_transit(now)
    mars = get_mars_transit(now)
    retrograde = is_venus_retrograde(now)

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={
            "date": now.strftime("%Y-%m-%d"),
            "venus": venus,
            "mars": mars,
            "venus_retrograde": retrograde,
        }
    )


@router.get("/phases", response_model=ApiResponse[Dict[str, Any]])
async def get_phases(request: Request):
    """
    Get information about relationship phases and astrological houses.
    """
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=get_relationship_phases()
    )
