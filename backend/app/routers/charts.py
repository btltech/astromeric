"""
API v2 - Chart Endpoints
Raw natal chart data, synastry, and chart visualization endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..cache import cached_build_chart
from ..chart_service import build_natal_chart
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
from ..products import build_compatibility
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/charts", tags=["Charts"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _profile_to_dict(payload: ProfilePayload) -> Dict:
    """Convert ProfilePayload to dict."""
    return {
        "name": payload.name,
        "date_of_birth": payload.date_of_birth,
        "time_of_birth": payload.time_of_birth or "12:00",
        "latitude": payload.latitude or 0.0,
        "longitude": payload.longitude or 0.0,
        "timezone": payload.timezone or "UTC",
        "house_system": getattr(payload, "house_system", "Placidus"),
    }


class NatalChartRequest(BaseModel):
    """Request for natal chart calculation."""
    profile: ProfilePayload
    lang: Optional[str] = "en"


class CompatibilityRequest(BaseModel):
    """Request for synastry/compatibility chart."""
    person_a: ProfilePayload
    person_b: ProfilePayload
    lang: Optional[str] = "en"


class PlanetPosition(BaseModel):
    """Planetary position data."""
    name: str
    longitude: float
    sign: str
    degree: float
    retrograde: bool = False


class HouseCusp(BaseModel):
    """House cusp data."""
    house: int
    longitude: float
    sign: str


class Aspect(BaseModel):
    """Aspect between planets."""
    planet1: str
    planet2: str
    aspect: str
    orb: float
    applying: bool = False


class NatalChartData(BaseModel):
    """Full natal chart response."""
    planets: List[Dict[str, Any]]
    houses: List[Dict[str, Any]]
    aspects: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class SynastryData(BaseModel):
    """Synastry chart response."""
    person_a: Dict[str, Any]
    person_b: Dict[str, Any]
    synastry_aspects: List[Dict[str, Any]]
    compatibility: Dict[str, Any]


@router.post("/natal", response_model=ApiResponse[NatalChartData])
async def get_natal_chart(
    request: Request,
    req: NatalChartRequest,
):
    """
    Get raw natal chart data for visualization.
    
    ## Response
    Returns planetary positions, house cusps, and aspects.
    Results are cached for 1 hour for performance.
    
    ## Use Cases
    - Chart wheel visualization
    - Custom chart analysis
    - Raw position data for calculations
    """
    profile = _profile_to_dict(req.profile)
    chart_data = cached_build_chart(profile, "natal", build_natal_chart)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart_data.get("planets", []),
            houses=chart_data.get("houses", []),
            aspects=chart_data.get("aspects", []),
            metadata={
                "name": profile["name"],
                "date_of_birth": profile["date_of_birth"],
                "time_of_birth": profile.get("time_of_birth"),
                "timezone": profile.get("timezone", "UTC"),
                "house_system": profile.get("house_system", "Placidus"),
            }
        )
    )


@router.post("/synastry", response_model=ApiResponse[SynastryData])
async def get_synastry_chart(
    request: Request,
    req: CompatibilityRequest,
):
    """
    Get synastry chart data for two people.
    
    ## Response
    Returns both natal charts plus inter-chart aspects and compatibility scores.
    
    ## Use Cases
    - Relationship chart visualization
    - Synastry aspect analysis
    - Compatibility assessment
    """
    from ..transit_alerts import find_transit_aspects
    
    person_a = _profile_to_dict(req.person_a)
    person_b = _profile_to_dict(req.person_b)

    # Use caching for individual charts
    chart_a = cached_build_chart(person_a, "natal", build_natal_chart)
    chart_b = cached_build_chart(person_b, "natal", build_natal_chart)

    # Find aspects between the two charts
    synastry_aspects = find_transit_aspects(chart_a, chart_b)

    # Get compatibility data
    compat = build_compatibility(person_a, person_b)

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=SynastryData(
            person_a={"name": person_a["name"], "chart": chart_a},
            person_b={"name": person_b["name"], "chart": chart_b},
            synastry_aspects=synastry_aspects,
            compatibility=compat
        )
    )
