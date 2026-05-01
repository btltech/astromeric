"""
API v2 - Chart Endpoints
Raw natal chart data, synastry, and chart visualization endpoints.
"""

import re
import traceback
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..cache import cached_build_chart
from ..chart_service import (
    build_lunar_return_chart,
    build_natal_chart,
    build_progressed_chart,
    build_relocation_chart,
    build_solar_arc_chart,
)
from ..exceptions import StructuredLogger
from ..models import SessionLocal
from ..products import build_compatibility
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/charts", tags=["Charts"])
logger = StructuredLogger(__name__)

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
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
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
    points: List[Dict[str, Any]] = []
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
    request_id = getattr(request.state, "request_id", None)
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        chart_data = cached_build_chart(profile, "natal", build_natal_chart)
    except Exception as _debug_exc:
        tb = traceback.format_exc()
        logger.error(
            "Natal chart failed",
            request_id=request_id,
            error_type=type(_debug_exc).__name__,
            error=str(_debug_exc),
            traceback=tb[-4000:],
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "NATAL_CHART_ERROR",
                "message": "Failed to calculate natal chart",
            },
        )
    birth_time_assumed = req.profile.time_of_birth is None
    data_quality = "full" if not birth_time_assumed else "date_and_place"
    logger.info(
        "Natal chart calculated",
        request_id=request_id,
        birth_time_assumed=birth_time_assumed,
        data_quality=data_quality,
    )
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart_data.get("planets", []),
            points=chart_data.get("points", []),
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
            },
        ),
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
            compatibility=compat,
        ),
    )


@router.post("/progressed", response_model=ApiResponse[NatalChartData])
async def get_progressed_chart(
    request: Request,
    req: ProgressedChartRequest,
):
    """
    Get a secondary progressed chart for a target date.

    Secondary progressions use the symbolic key of 1 day after birth = 1 year
    of life, anchored on the natal birth time and location.
    """
    request_id = getattr(request.state, "request_id", None)
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)

    try:
        chart_data = build_progressed_chart(profile, target_date=req.target_date)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(
            "Progressed chart failed",
            request_id=request_id,
            error_type=type(exc).__name__,
            error=str(exc),
            traceback=tb[-4000:],
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROGRESSED_CHART_ERROR",
                "message": "Failed to calculate progressed chart",
            },
        )

    meta = chart_data.get("metadata", {})
    birth_time_assumed = req.profile.time_of_birth is None

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart_data.get("planets", []),
            points=chart_data.get("points", []),
            houses=chart_data.get("houses", []),
            aspects=chart_data.get("aspects", []),
            metadata={
                **meta,
                "name": profile["name"],
                "birth_time_assumed": birth_time_assumed,
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
        mid = _midpoint_degree(
            pa.get("absolute_degree", 0), pb.get("absolute_degree", 0)
        )
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


# ============================================================================
# PHASE 2: SOLAR ARC, RELOCATION, LUNAR RETURN
# ============================================================================


class SolarArcRequest(BaseModel):
    profile: ProfilePayload
    target_date: Optional[str] = None  # yyyy-MM-dd


class RelocationRequest(BaseModel):
    profile: ProfilePayload
    new_latitude: float
    new_longitude: float
    new_timezone: Optional[str] = None


class LunarReturnRequest(BaseModel):
    profile: ProfilePayload
    target_date: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_tz: Optional[str] = None


@router.post("/solar-arc", response_model=ApiResponse[NatalChartData])
async def get_solar_arc_chart(
    request: Request,
    req: SolarArcRequest,
) -> ApiResponse[NatalChartData]:
    """
    Solar arc directions for the given profile.
    Returns directed planet positions and cross-aspects (directed vs natal).
    """
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        chart = build_solar_arc_chart(profile, target_date=req.target_date)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart.get("planets", []),
            points=chart.get("points", []),
            houses=chart.get("houses", []),
            aspects=chart.get("aspects", []),
            metadata=chart.get("metadata", {}),
        ),
    )


@router.post("/relocation", response_model=ApiResponse[NatalChartData])
async def get_relocation_chart(
    request: Request,
    req: RelocationRequest,
) -> ApiResponse[NatalChartData]:
    """
    Relocation chart: same UTC birth moment, different geographic coordinates.
    Planets are identical to natal; houses, ASC, and MC recalculate.
    """
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        chart = build_relocation_chart(
            profile,
            new_latitude=req.new_latitude,
            new_longitude=req.new_longitude,
            new_timezone=req.new_timezone,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart.get("planets", []),
            points=chart.get("points", []),
            houses=chart.get("houses", []),
            aspects=chart.get("aspects", []),
            metadata=chart.get("metadata", {}),
        ),
    )


@router.post("/lunar-return", response_model=ApiResponse[NatalChartData])
async def get_lunar_return_chart(
    request: Request,
    req: LunarReturnRequest,
) -> ApiResponse[NatalChartData]:
    """
    Lunar Return chart: cast for the next moment the Moon returns to its natal longitude.
    """
    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        chart = build_lunar_return_chart(
            profile,
            target_date=req.target_date,
            location_lat=req.location_lat,
            location_lon=req.location_lon,
            location_tz=req.location_tz,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=NatalChartData(
            planets=chart.get("planets", []),
            points=chart.get("points", []),
            houses=chart.get("houses", []),
            aspects=chart.get("aspects", []),
            metadata=chart.get("metadata", {}),
        ),
    )


# ---------------------------------------------------------------------------
# Phase 3 endpoints: Profections, Declinations, Fixed Stars
# ---------------------------------------------------------------------------


class ProfectionsRequest(BaseModel):
    profile: ProfilePayload
    ref_date: Optional[str] = None  # ISO date string; defaults to today


class DeclinationsRequest(BaseModel):
    profile: ProfilePayload


class FixedStarsRequest(BaseModel):
    planets: List[Dict[str, Any]]  # list of {name, absolute_degree}
    orb: Optional[float] = 1.0


@router.post("/profections")
async def get_profections(
    request: Request,
    req: ProfectionsRequest,
) -> ApiResponse[Dict[str, Any]]:
    """
    Annual & Monthly Profections (Hellenistic timing technique).
    Returns the active house, Time Lord, and thematic interpretation.
    """
    from ..engine.advanced_techniques import calculate_profections

    profile = _profile_to_dict(req.profile)
    try:
        result = calculate_profections(
            dob=profile["date_of_birth"],
            ref_date=req.ref_date,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(status=ResponseStatus.SUCCESS, data=result)


@router.post("/declinations")
async def get_declinations(
    request: Request,
    req: DeclinationsRequest,
) -> ApiResponse[Dict[str, Any]]:
    """
    Planetary declinations and parallel / contra-parallel aspects.
    """
    from ..engine.advanced_techniques import calculate_declinations

    _require_chart_inputs(req.profile)
    profile = _profile_to_dict(req.profile)
    try:
        result = calculate_declinations(profile=profile)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(status=ResponseStatus.SUCCESS, data=result)


@router.post("/fixed-stars")
async def get_fixed_stars(
    request: Request,
    req: FixedStarsRequest,
) -> ApiResponse[List[Dict[str, Any]]]:
    """
    Fixed Star conjunctions within the requested orb (default 1°).
    Accepts a pre-computed planet list (name + absolute_degree).
    """
    from ..engine.advanced_techniques import find_fixed_star_conjunctions

    try:
        result = find_fixed_star_conjunctions(
            planets=req.planets,
            orb=req.orb if req.orb is not None else 1.0,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(status=ResponseStatus.SUCCESS, data=result)
