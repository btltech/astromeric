"""
main.py
--------
FastAPI entrypoint - application setup and router registration.

All endpoint logic has been moved to dedicated routers in the /routers directory.
This file handles only:
- App configuration
- Middleware setup
- Router registration
- Exception handlers
- Startup events

Deployment notes:
- Swiss Ephemeris files must live at /app/ephemeris (or set EPHEMERIS_PATH).
- Railway start: uvicorn backend.app.main:api --host 0.0.0.0 --port $PORT
- Redis: Install Redis in your deploy environment, set REDIS_URL
- JWT_SECRET_KEY: Set a secure secret key for JWT tokens
"""

from __future__ import annotations

import logging
import os
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import SECURITY_HEADERS
from .middleware import rate_limit_middleware, security_headers_middleware
from .validators import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# APPLICATION SETUP
# =============================================================================

api = FastAPI(
    title="AstroNumerology API",
    version="4.0.0",
    description="""## AstroNumerology API
    
A comprehensive astrology and numerology API that provides:
- **Natal Charts**: Calculate planetary positions, houses, and aspects
- **Forecasts**: Daily, weekly, and monthly readings
- **Compatibility**: Synastry analysis between two people
- **Numerology**: Life path, expression, and personal year calculations
- **AI Explanations**: Gemini-powered interpretations
- **Moon Phases**: Lunar cycle tracking and rituals
- **Timing Advisor**: Best times for activities
- **Relationship Timeline**: Love and relationship guidance

### Authentication
Most endpoints work without authentication. Create an account for personalized features.

### Rate Limits
Global limit: 100 requests per minute per IP.

### API Versions
- **/v2/**: Current standardized API with consistent response format
- Legacy endpoints: Maintained for backward compatibility
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Alias for uvicorn import compatibility
app = api


# =============================================================================
# MIDDLEWARE
# =============================================================================


@api.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request."""
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Rate limiting middleware (60 req/min with burst support)
api.middleware("http")(rate_limit_middleware)

# Security headers middleware
api.middleware("http")(security_headers_middleware)

# CORS configuration
allow_origins_env = os.getenv("ALLOW_ORIGINS", "")
if allow_origins_env:
    allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]
else:
    allow_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

allow_origin_regex = os.getenv(
    "ALLOW_ORIGIN_REGEX",
    r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|.*\.astronumeric\.pages\.dev|.*\.astromeric\.pages\.dev|astronumeric\.pages\.dev|astromeric\.pages\.dev|.*\.astronumeric\.com|.*\.astromeric\.com|astronumeric\.com|www\.astronumeric\.com|www\.astromeric\.com)(:\d+)?",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins else ["*"],
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


@api.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors with user-friendly messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.to_dict(),
            "message": exc.message,
        },
    )


@api.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler with detailed logging."""
    import traceback

    # Let FastAPI handle HTTPException with its own handler (preserves detail field)
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)

    error_detail = f"{type(exc).__name__}: {str(exc)}"
    logger.error(f"[{request.method} {request.url.path}]: {error_detail}")
    logger.debug(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred. Please try again later."},
    )


# =============================================================================
# STARTUP EVENTS
# =============================================================================


@api.on_event("startup")
async def startup_event():
    """Run tasks on startup."""
    from .transit_alerts import check_global_events

    try:
        check_global_events()
        logger.info("Startup event check completed successfully")
    except Exception as e:
        logger.error(f"Startup event check failed: {e}")


# =============================================================================
# HEALTH CHECK (simple endpoint kept in main for load balancer checks)
# =============================================================================


@api.get("/health", tags=["System"])
async def health_check():
    """Simple health check supporting GET and HEAD."""
    return {"status": "ok"}


# =============================================================================
# ROUTER REGISTRATION
# =============================================================================


def register_routers():
    """Register all API routers — each imported individually so one failure never blocks the rest."""
    import importlib
    import traceback

    _router_names = [
        "auth", "profiles", "natal", "forecasts", "compatibility",
        "numerology", "charts", "daily_features", "moon", "timing",
        "relationships", "journal", "habits", "year_ahead", "transits",
        "notifications", "friends", "ai", "cosmic_guide", "learning",
        "feedback", "system",
    ]

    loaded = 0
    for name in _router_names:
        try:
            mod = importlib.import_module(f".routers.{name}", package=__name__.rsplit(".", 1)[0])
            api.include_router(mod.router)
            loaded += 1
        except Exception as e:
            logger.error(f"ROUTER LOAD FAILED [{name}]: {type(e).__name__}: {e} | {traceback.format_exc()[-300:]}")

    logger.info(f"Registered {loaded}/{len(_router_names)} v2 routers")

    # V2 Additional routers (sky, alerts)
    try:
        from .routers import alerts as v2_alerts
        from .routers import sky as v2_sky

        api.include_router(v2_sky.router)
        api.include_router(v2_alerts.router)

        logger.info("Registered v2 sky and alerts routers")
    except ImportError as e:
        logger.warning(f"Could not import sky/alerts routers: {str(e)}")


# Register all routers
register_routers()


# =============================================================================
# LEGACY ALIASES
# =============================================================================

# NOTE: The v2 API uses a standardized {status, data} wrapper.
# The following legacy endpoints intentionally return *unwrapped* JSON for
# backward compatibility with older clients/tests.

from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel

from .auth import get_current_user

@api.post("/daily-features", tags=["Legacy"])
async def legacy_daily_features(request: Request, body: dict):
    """Alias for /v2/daily/reading to support existing frontend."""
    from .routers.daily_features import get_daily_reading
    # Extract profile if available, else None
    profile = body.get("profile")
    return await get_daily_reading(request, profile)

@api.post("/forecast/mood", tags=["Legacy"])
async def legacy_mood_forecast(request: Request, body: dict):
    """Alias for /v2/daily/reading to support existing mood calls."""
    from .routers.daily_features import get_daily_reading
    profile = body.get("profile")
    return await get_daily_reading(request, profile)


# -----------------------------------------------------------------------------
# Legacy: Natal + Compatibility (pre-v2)
# -----------------------------------------------------------------------------


class LegacyLocation(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None


class LegacyProfile(BaseModel):
    name: str
    date_of_birth: str
    time_of_birth: Optional[str] = None
    location: Optional[LegacyLocation] = None


class LegacyNatalProfileRequest(BaseModel):
    profile: LegacyProfile
    lang: str = "en"


class LegacyCompatibilityRequest(BaseModel):
    person_a: LegacyProfile
    person_b: LegacyProfile
    lang: str = "en"


def _legacy_profile_to_flat(profile: LegacyProfile) -> Dict[str, Any]:
    loc = profile.location
    latitude = getattr(loc, "latitude", None) if loc else None
    longitude = getattr(loc, "longitude", None) if loc else None
    timezone = getattr(loc, "timezone", None) if loc else None
    return {
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth or "12:00:00",
        # Legacy clients often omitted location; fall back to 0,0 UTC for continuity.
        "latitude": 0.0 if latitude is None else latitude,
        "longitude": 0.0 if longitude is None else longitude,
        "timezone": "UTC" if not timezone else timezone,
    }


@api.post("/natal-profile", tags=["Legacy"])
async def legacy_natal_profile(req: LegacyNatalProfileRequest):
    """Legacy alias for natal profile (unwrapped)."""
    from .products.natal_profile import build_natal_profile

    profile_dict = _legacy_profile_to_flat(req.profile)
    return build_natal_profile(profile_dict, lang=req.lang)


@api.post("/compatibility", tags=["Legacy"])
async def legacy_compatibility(req: LegacyCompatibilityRequest):
    """Legacy alias for romantic compatibility (unwrapped)."""
    from .products.compatibility import build_compatibility

    a = _legacy_profile_to_flat(req.person_a)
    b = _legacy_profile_to_flat(req.person_b)
    return build_compatibility(a, b, lang=req.lang)


# -----------------------------------------------------------------------------
# Legacy: Habits (pre-v2)
# -----------------------------------------------------------------------------


class LegacyCreateHabitBody(BaseModel):
    name: str
    category: str


class LegacyLogHabitBody(BaseModel):
    habit_id: int
    notes: str = ""


class LegacyStreakBody(BaseModel):
    completions: List[Dict[str, Any]]


class LegacyTodayHabitsBody(BaseModel):
    habits: List[Dict[str, Any]]
    completions_today: Optional[List[int]] = None


@api.get("/habits/categories", tags=["Legacy"])
async def legacy_habit_categories():
    from .engine.habit_tracker import HABIT_CATEGORIES

    categories = [{"id": key, **info} for key, info in HABIT_CATEGORIES.items()]
    return {"categories": categories}


@api.get("/habits/lunar-guidance", tags=["Legacy"])
async def legacy_habit_lunar_guidance():
    from .engine.habit_tracker import LUNAR_HABIT_GUIDANCE

    phases = [{"phase": key, **info} for key, info in LUNAR_HABIT_GUIDANCE.items()]
    return {"phases": phases}


@api.get("/habits/lunar-guidance/{phase}", tags=["Legacy"])
async def legacy_habit_phase_guidance(phase: str):
    from .engine.habit_tracker import LUNAR_HABIT_GUIDANCE

    if phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(status_code=400, detail="Invalid phase")
    return {"phase": phase, **LUNAR_HABIT_GUIDANCE[phase]}


@api.post("/habits/alignment", tags=["Legacy"])
async def legacy_habit_alignment(category: str, moon_phase: str):
    from .engine.habit_tracker import HABIT_CATEGORIES, LUNAR_HABIT_GUIDANCE, calculate_lunar_alignment_score

    if category not in HABIT_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(status_code=400, detail="Invalid moon_phase")
    return calculate_lunar_alignment_score(category, moon_phase)


@api.post("/habits/recommendations", tags=["Legacy"])
async def legacy_habit_recommendations(moon_phase: str):
    from .engine.habit_tracker import LUNAR_HABIT_GUIDANCE, get_lunar_habit_recommendations

    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(status_code=400, detail="Invalid moon_phase")
    return get_lunar_habit_recommendations(moon_phase)


@api.post("/habits/create", tags=["Legacy"])
async def legacy_habit_create(body: LegacyCreateHabitBody):
    from .engine.habit_tracker import HABIT_CATEGORIES, create_habit

    if body.category not in HABIT_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    habit = create_habit(body.name, body.category)
    return {"success": True, "habit": habit}


@api.post("/habits/log", tags=["Legacy"])
async def legacy_habit_log(body: LegacyLogHabitBody, moon_phase: str):
    from .engine.habit_tracker import log_habit_completion

    completion = log_habit_completion(body.habit_id, moon_phase=moon_phase, notes=body.notes)
    return {"success": True, "completion": completion}


@api.post("/habits/streak", tags=["Legacy"])
async def legacy_habit_streak(body: LegacyStreakBody, frequency: str = "daily"):
    from .engine.habit_tracker import get_habit_streak

    return get_habit_streak(body.completions, frequency=frequency)


@api.post("/habits/today", tags=["Legacy"])
async def legacy_habit_today(body: LegacyTodayHabitsBody, moon_phase: str):
    from .engine.habit_tracker import get_today_habit_forecast

    return get_today_habit_forecast(body.habits, moon_phase, completions_today=body.completions_today)


# -----------------------------------------------------------------------------
# Legacy: Journal (pre-v2)
# -----------------------------------------------------------------------------


@api.get("/journal/prompts", tags=["Legacy"])
async def legacy_journal_prompts(
    scope: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    themes: Optional[str] = None,
):
    from .engine.journal import get_journal_prompts

    theme_list = themes.split(",") if themes else None
    prompts = get_journal_prompts(scope, theme_list)
    return {"scope": scope, "prompts": prompts}


# Auth-required legacy journal endpoints: present for compatibility.
# When unauthenticated, these will correctly return 401/403 rather than 404.


@api.get("/journal/readings/{profile_id}", tags=["Legacy"])
async def legacy_journal_readings(
    profile_id: int,
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/readings/{profile_id}")


@api.get("/journal/reading/{reading_id}", tags=["Legacy"])
async def legacy_journal_reading(
    reading_id: int,
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/reading/{reading_id}")


@api.get("/journal/stats/{profile_id}", tags=["Legacy"])
async def legacy_journal_stats(
    profile_id: int,
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/stats/{profile_id}")


@api.get("/journal/patterns/{profile_id}", tags=["Legacy"])
async def legacy_journal_patterns(
    profile_id: int,
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/patterns/{profile_id}")


@api.post("/journal/entry", tags=["Legacy"])
async def legacy_journal_entry(
    body: Dict[str, Any],
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/entry")


@api.post("/journal/outcome", tags=["Legacy"])
async def legacy_journal_outcome(
    body: Dict[str, Any],
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=410, detail="Use /v2/journal/outcome")


# -----------------------------------------------------------------------------
# Legacy: Relationships (pre-v2)
# -----------------------------------------------------------------------------


VALID_SIGNS = {
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
}


class LegacyRelationshipTimelineBody(BaseModel):
    sun_sign: str
    partner_sign: Optional[str] = None
    months_ahead: int = 6


class LegacyRelationshipTimingBody(BaseModel):
    sun_sign: str
    partner_sign: Optional[str] = None
    date: Optional[str] = None


@api.post("/relationship/timeline", tags=["Legacy"])
async def legacy_relationship_timeline(body: LegacyRelationshipTimelineBody):
    from datetime import datetime, timezone
    from .engine.relationship_timeline import build_relationship_timeline

    if body.sun_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid sign")
    if body.partner_sign and body.partner_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid partner_sign")

    return build_relationship_timeline(
        sun_sign=body.sun_sign,
        partner_sign=body.partner_sign,
        start_date=datetime.now(timezone.utc),
        months_ahead=body.months_ahead,
    )


@api.post("/relationship/timing", tags=["Legacy"])
async def legacy_relationship_timing(body: LegacyRelationshipTimingBody):
    from datetime import datetime, timezone
    from .engine.relationship_timeline import analyze_relationship_timing

    if body.sun_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid sign")
    if body.partner_sign and body.partner_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid partner_sign")

    if body.date:
        try:
            check_date = datetime.fromisoformat(body.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        check_date = datetime.now(timezone.utc)

    return analyze_relationship_timing(check_date, body.sun_sign, body.partner_sign)


@api.get("/relationship/best-days/{sun_sign}", tags=["Legacy"])
async def legacy_relationship_best_days(sun_sign: str, days_ahead: int = 30):
    from datetime import datetime, timezone
    from .engine.relationship_timeline import get_best_relationship_days

    if sun_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid sign")

    best_days = get_best_relationship_days(datetime.now(timezone.utc), sun_sign, days_ahead)
    return {
        "sun_sign": sun_sign,
        "days_ahead": days_ahead,
        "best_days": best_days[:10],
    }


@api.get("/relationship/events", tags=["Legacy"])
async def legacy_relationship_events(days_ahead: int = 90, sun_sign: Optional[str] = None):
    from datetime import datetime, timezone
    from .engine.relationship_timeline import get_upcoming_relationship_dates

    if sun_sign and sun_sign not in VALID_SIGNS:
        raise HTTPException(status_code=400, detail="Invalid sign")

    events = get_upcoming_relationship_dates(datetime.now(timezone.utc), days_ahead, sun_sign)
    return {
        "days_ahead": days_ahead,
        "sun_sign": sun_sign,
        "events": events,
    }


@api.get("/relationship/venus-status", tags=["Legacy"])
async def legacy_relationship_venus_status():
    from datetime import datetime, timezone
    from .engine.relationship_timeline import get_mars_transit, get_venus_transit, is_venus_retrograde

    now = datetime.now(timezone.utc)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "venus": get_venus_transit(now),
        "mars": get_mars_transit(now),
        "venus_retrograde": is_venus_retrograde(now),
    }


@api.get("/relationship/phases", tags=["Legacy"])
async def legacy_relationship_phases():
    from .engine.relationship_timeline import get_relationship_phases

    return get_relationship_phases()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(api, host="0.0.0.0", port=port)
