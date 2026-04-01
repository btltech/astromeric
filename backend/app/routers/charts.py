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
from datetime import datetime, timedelta
import re
from ..chart_service import build_natal_chart
from ..models import Profile as DBProfile
from ..models import SessionLocal, User
from ..products import build_compatibility
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/charts", tags=["Charts"])

_TZ_OFFSET_RE = re.compile(
    r"^(?:UTC|GMT)?\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?$", re.IGNORECASE
)


def _is_fixed_offset_tz(tz: str) -> bool:
    """
    Accept fixed-offset timezone identifiers commonly produced by clients.
    Examples: "GMT+0100", "GMT+01:00", "UTC-5", "+01:00", "-0530".
    """
    return _TZ_OFFSET_RE.match(tz.strip()) is not None


def _require_chart_inputs(profile: ProfilePayload) -> None:
    missing: list[str] = []
    if profile.latitude is None:
        missing.append("latitude")
    if profile.longitude is None:
        missing.append("longitude")
    if not profile.timezone:
        missing.append("timezone")
    if missing:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "MISSING_PROFILE_FIELDS",
                "message": "Charts require birth location + timezone. Birth time improves accuracy but is optional (defaults to 12:00).",
                "missing": missing,
            },
        )

    tz = (profile.timezone or "").strip()
    if tz not in ("UTC", "GMT"):
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(tz)
        except Exception:
            if _is_fixed_offset_tz(tz):
                # Allow fixed-offset tz strings; chart_service will interpret them as a fixed offset.
                return
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_TIMEZONE",
                    "message": f"Invalid timezone '{profile.timezone}'. Use a valid IANA timezone (e.g., 'America/New_York').",
                    "field": "timezone",
                },
            )


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
        "place_of_birth": getattr(payload, "place_of_birth", None),
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "timezone": payload.timezone,
        "house_system": getattr(payload, "house_system", None) or "Placidus",
    }


def _midpoint_degree(a: float, b: float) -> float:
    """Midpoint on a circle, preserving shortest arc."""
    diff = (b - a + 360) % 360
    if diff > 180:
        diff -= 360
    return (a + diff / 2) % 360


def _degree_to_sign(deg: float) -> Dict[str, Any]:
    sign_index = int(deg // 30)
    sign = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ][sign_index]
    return {"sign": sign, "degree": round(deg % 30, 4)}


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


class ProgressedChartRequest(BaseModel):
    profile: ProfilePayload
    target_date: Optional[str] = None  # yyyy-MM-dd


class CompositeChartRequest(BaseModel):
    person_a: ProfilePayload
    person_b: ProfilePayload


class CompositeChartData(BaseModel):
    planets: List[Dict[str, Any]]
    metadata: Dict[str, Any]


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
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        chart_data = cached_build_chart(profile, "natal", build_natal_chart)
    except Exception as _debug_exc:
        import traceback
        raise HTTPException(status_code=500, detail={"debug_error": str(_debug_exc), "tb": traceback.format_exc()[-500:]})
    birth_time_assumed = req.profile.time_of_birth is None
    data_quality = "full" if not birth_time_assumed else "date_and_place"
    logger.info(
        "Natal chart calculated",
        profile_name=profile.get("name"),
        birth_time_assumed=birth_time_assumed,
        data_quality=data_quality,
    )
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
                "birth_time_assumed": birth_time_assumed,
                "assumed_time_of_birth": "12:00" if birth_time_assumed else None,
                "data_quality": data_quality,
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
    
    _require_chart_inputs(req.person_a)
    _require_chart_inputs(req.person_b)
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


@router.post("/progressed", response_model=ApiResponse[NatalChartData])
async def get_progressed_chart(
    request: Request,
    req: ProgressedChartRequest,
):
    """
    Get a secondary progressed chart for a target date.
    """
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)

    # Parse dates
    birth_dt = datetime.fromisoformat(
        f"{profile['date_of_birth']}T{profile.get('time_of_birth', '12:00')}"
    )
    target_dt = datetime.utcnow()
    if req.target_date:
        target_dt = datetime.fromisoformat(f"{req.target_date}T00:00")

    # Secondary progression: 1 day after birth per year of life
    delta_years = (target_dt - birth_dt).days / 365.25
    progressed_dt = birth_dt + timedelta(days=delta_years)

    progressed_profile = dict(profile)
    progressed_profile["date_of_birth"] = progressed_dt.strftime("%Y-%m-%d")
    progressed_profile["time_of_birth"] = birth_dt.strftime("%H:%M")

    chart_data = build_natal_chart(progressed_profile)

    # Propagate truth-awareness from original profile
    birth_time_assumed = req.profile.time_of_birth is None
    time_confidence = req.profile.time_confidence or ("exact" if not birth_time_assumed else "unknown")
    if time_confidence == "exact":
        data_quality = "full"
    elif time_confidence == "approximate":
        data_quality = "date_and_place"
    else:
        data_quality = "date_and_place"

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart_data.get("planets", []),
            houses=chart_data.get("houses", []),
            aspects=chart_data.get("aspects", []),
            metadata={
                "name": profile["name"],
                "progressed_date": progressed_dt.strftime("%Y-%m-%d"),
                "target_date": target_dt.strftime("%Y-%m-%d"),
                "house_system": profile.get("house_system", "Placidus"),
                "birth_time_assumed": birth_time_assumed,
                "data_quality": data_quality,
                "assumed_time_of_birth": "12:00" if birth_time_assumed else None,
            },
        ),
    )


@router.post("/composite", response_model=ApiResponse[CompositeChartData])
async def get_composite_chart(
    request: Request,
    req: CompositeChartRequest,
):
    """
    Get a composite chart by midpointing planetary positions.
    """
    _require_chart_inputs(req.person_a)
    _require_chart_inputs(req.person_b)
    person_a = _profile_to_dict(req.person_a)
    person_b = _profile_to_dict(req.person_b)

    chart_a = build_natal_chart(person_a)
    chart_b = build_natal_chart(person_b)

    planets_a = {p["name"]: p for p in chart_a.get("planets", [])}
    planets_b = {p["name"]: p for p in chart_b.get("planets", [])}

    composite_planets = []
    for name, pa in planets_a.items():
        pb = planets_b.get(name)
        if not pb:
            continue
        mid = _midpoint_degree(pa.get("absolute_degree", 0), pb.get("absolute_degree", 0))
        sign_info = _degree_to_sign(mid)
        composite_planets.append(
            {
                "name": name,
                "absolute_degree": round(mid, 4),
                "sign": sign_info["sign"],
                "degree": sign_info["degree"],
            }
        )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=CompositeChartData(
            planets=composite_planets,
            metadata={
                "person_a": person_a["name"],
                "person_b": person_b["name"],
                "method": "midpoint",
            },
        ),
    )
