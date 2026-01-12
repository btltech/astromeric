"""
main.py
--------
FastAPI entrypoint exposing product endpoints powered by the shared engines.

Endpoints:
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /daily-reading
- POST /weekly-reading
- POST /monthly-reading
- POST /forecast (generic scope)
- POST /natal-profile
- POST /compatibility
- GET /learn/zodiac - with pagination support
- GET /learn/numerology - with pagination support

Deployment notes:
- Swiss Ephemeris files must live at /app/ephemeris (or set EPHEMERIS_PATH).
- Railway start: uvicorn backend.app.main:api --host 0.0.0.0 --port $PORT
- Redis: Install Redis in your deploy environment, set REDIS_URL (e.g., redis://localhost:6379)
- Cache TTL: Set FUSION_CACHE_TTL (seconds, default 86400 = 24 hours)
- JWT_SECRET_KEY: Set a secure secret key for JWT tokens
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from .middleware import rate_limit_middleware, security_headers_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from .cache import get_chart_cache, cached_build_chart
from .validators import (
    ValidationError,
    validate_date_of_birth,
    validate_latitude,
    validate_longitude,
    validate_name,
    validate_profile_data,
    validate_time_of_birth,
    validate_timezone,
)

from .auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserCreate,
    UserLogin,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_current_user_optional,
    get_user_by_email,
)
from .ai_service import explain_with_gemini, fallback_summary
from .chart_service import EPHEMERIS_PATH, HAS_FLATLIB, build_natal_chart
from .engine.glossary import NUMEROLOGY_GLOSSARY, ZODIAC_GLOSSARY
from .engine.year_ahead import build_year_ahead_forecast
from .engine.moon_phases import get_moon_phase_summary, calculate_moon_phase, get_upcoming_moon_events
from .engine.timing_advisor import (
    calculate_timing_score,
    find_best_days,
    get_timing_advice,
    get_available_activities,
    ACTIVITY_PROFILES,
)
from .engine.journal import (
    add_journal_entry,
    record_outcome,
    calculate_accuracy_stats,
    get_reading_insights,
    analyze_prediction_patterns,
    get_journal_prompts,
    create_accountability_report,
    format_reading_for_journal,
)
from .engine.relationship_timeline import (
    get_venus_transit,
    get_mars_transit,
    is_venus_retrograde,
    get_upcoming_relationship_dates,
    analyze_relationship_timing,
    get_best_relationship_days,
    build_relationship_timeline,
    get_relationship_phases,
)
from .engine.habit_tracker import (
    LUNAR_HABIT_GUIDANCE,
    HABIT_CATEGORIES,
    get_moon_phase_name,
    create_habit,
    log_habit_completion,
    calculate_lunar_alignment_score,
    get_habit_streak,
    get_lunar_habit_recommendations,
    calculate_habit_analytics,
    get_today_habit_forecast,
    get_lunar_cycle_report,
)
from .models import Profile as DBProfile
from .models import Reading as DBReading
from .models import SectionFeedback
from .models import SessionLocal, User
from .numerology_engine import build_numerology
from .products import build_compatibility, build_forecast, build_natal_profile

api = FastAPI(
    title="AstroNumerology API", 
    version="3.3.0",
    description="""## AstroNumerology API
    
A comprehensive astrology and numerology API that provides:
- **Natal Charts**: Calculate planetary positions, houses, and aspects
- **Forecasts**: Daily, weekly, and monthly readings
- **Compatibility**: Synastry analysis between two people
- **Numerology**: Life path, expression, and personal year calculations
- **AI Explanations**: Gemini-powered interpretations

### Authentication
Most endpoints work without authentication. Create an account for personalized features.

### Rate Limits
Global limit: 100 requests per minute per IP.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)
app = api  # alias for uvicorn import style

# Add custom rate limiting middleware (60 req/min with burst support)
app.middleware("http")(rate_limit_middleware)

# Add security headers middleware
app.middleware("http")(security_headers_middleware)

# Allow configurable CORS via env; default open for dev
allow_origins_env = os.getenv("ALLOW_ORIGINS", "")
if allow_origins_env:
    allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]
else:
    allow_origins = []

# Always allow localhost, local network IPs, and known frontend origins.
# You can override/extend this in production via ALLOW_ORIGIN_REGEX.
allow_origin_regex = os.getenv(
    "ALLOW_ORIGIN_REGEX",
    r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|.*\.astronumeric\.pages\.dev|.*\.astromeric\.pages\.dev|astronumeric\.pages\.dev|astromeric\.pages\.dev|astronumeric\.com|www\.astronumeric\.com)(:\d+)?",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== EXCEPTION HANDLERS ==========


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
    error_detail = f"{type(exc).__name__}: {str(exc)}"
    # Log full error details server-side only
    logger.error(f"[{request.method} {request.url.path}]: {error_detail}")
    logger.debug(traceback.format_exc())
    # Return generic message to client (don't leak internal details)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred. Please try again later."},
    )


# ========== PYDANTIC MODELS ==========


class Location(BaseModel):
    """Geographic location for birth chart calculation."""
    latitude: float = Field(0.0, ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(0.0, ge=-180, le=180, description="Longitude (-180 to 180)")
    timezone: str = Field("UTC", description="IANA timezone (e.g., America/New_York)")

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        return validate_latitude(v)

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v):
        return validate_longitude(v)


class ProfilePayload(BaseModel):
    """Birth profile data for astrological calculations."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the person")
    date_of_birth: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}", description="Date in YYYY-MM-DD format")
    time_of_birth: Optional[str] = Field(None, description="Time in HH:MM format (24-hour)")
    location: Optional[Location] = Field(None, description="Birth location")
    house_system: Optional[str] = Field("Placidus", description="House system (Placidus, Whole, Equal, Koch)")

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        return validate_date_of_birth(v)

    @field_validator("time_of_birth")
    @classmethod
    def validate_tob(cls, v):
        if v is None:
            return None
        return validate_time_of_birth(v)

    @field_validator("name")
    @classmethod
    def validate_profile_name(cls, v):
        return validate_name(v)


class DailyRequest(BaseModel):
    profile: ProfilePayload
    lang: Optional[str] = "en"


class WeeklyRequest(BaseModel):
    profile: ProfilePayload
    lang: Optional[str] = "en"


class MonthlyRequest(BaseModel):
    profile: ProfilePayload
    lang: Optional[str] = "en"


class ForecastRequest(BaseModel):
    profile: Optional[ProfilePayload] = None
    profile_id: Optional[int] = None
    scope: str = Field("daily", pattern=r"^(daily|weekly|monthly)$")
    lang: Optional[str] = "en"


class NatalRequest(BaseModel):
    profile: ProfilePayload
    lang: Optional[str] = "en"


class CompatibilityRequest(BaseModel):
    person_a: ProfilePayload
    person_b: ProfilePayload
    lang: Optional[str] = "en"


class CreateProfileRequest(BaseModel):
    name: str
    date_of_birth: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")
    time_of_birth: Optional[str] = None
    place_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = "UTC"
    house_system: Optional[str] = "Placidus"


class AIExplainSection(BaseModel):
    title: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class AIExplainRequest(BaseModel):
    scope: str
    headline: Optional[str] = None
    theme: Optional[str] = None
    sections: list[AIExplainSection] = Field(default_factory=list)
    numerology_summary: Optional[str] = None


class AIExplainResponse(BaseModel):
    summary: str
    provider: str


class SectionFeedbackRequest(BaseModel):
    scope: str
    section: str
    vote: str = Field(..., pattern=r"^(up|down)$")
    profile_id: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== AUTH ENDPOINTS ==========


@api.post("/auth/register", response_model=Token)
@rate_limit(requests_per_minute=3)  # Prevent spam registrations
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = create_user(db, user_data)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "is_paid": user.is_paid},
    }


@api.post("/auth/login", response_model=Token)
@rate_limit(requests_per_minute=5)  # Prevent brute force attacks
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a token."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "is_paid": user.is_paid},
    }


@api.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {"id": current_user.id, "email": current_user.email, "is_paid": current_user.is_paid}


@api.post("/auth/activate-premium")
def activate_premium(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Activate premium for site owner only."""
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    if not admin_emails or current_user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Re-fetch the user from this session to ensure it's attached
    user = db.query(User).filter(User.id == current_user.id).first()
    user.is_paid = True
    db.commit()
    db.refresh(user)
    return {"success": True, "is_paid": user.is_paid}


# ========== AI ENDPOINTS ==========


@api.post("/ai/explain", response_model=AIExplainResponse)
def explain_reading(
    payload: AIExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Explain reading with AI - requires paid subscription."""
    if not current_user.is_paid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI insights require a premium subscription. Upgrade to unlock this feature.",
        )
    
    sections = [section.model_dump() for section in payload.sections]
    summary = explain_with_gemini(
        payload.scope,
        payload.headline,
        payload.theme,
        sections,
        payload.numerology_summary,
    )
    provider = "gemini-flash"
    if not summary:
        provider = "fallback"
        summary = fallback_summary(
            payload.headline, sections, payload.numerology_summary
        )
    return {"summary": summary, "provider": provider}


# ========== HELPER FUNCTIONS ==========


def _profile_to_dict(payload: ProfilePayload) -> Dict:
    loc = payload.location.model_dump() if payload.location else {}
    return {
        "name": payload.name,
        "date_of_birth": payload.date_of_birth,
        "time_of_birth": payload.time_of_birth,
        "latitude": loc.get("latitude", 0.0),
        "longitude": loc.get("longitude", 0.0),
        "timezone": loc.get("timezone", "UTC"),
        "house_system": payload.house_system or "Placidus",
    }


def _profile_from_id(profile_id: int, db: Session) -> Dict:
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _db_profile_to_dict(profile)


def _db_profile_to_dict(profile: DBProfile) -> Dict:
    return {
        "id": profile.id,
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "time_of_birth": profile.time_of_birth,
        "place_of_birth": profile.place_of_birth,
        "latitude": profile.latitude if profile.latitude is not None else 0.0,
        "longitude": profile.longitude if profile.longitude is not None else 0.0,
        "timezone": profile.timezone or "UTC",
        "house_system": profile.house_system or "Placidus",
    }


@api.get("/profiles")
def get_profiles(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get all saved profiles."""
    if current_user:
        return [
            _db_profile_to_dict(p)
            for p in db.query(DBProfile).filter(DBProfile.user_id == current_user.id).all()
        ]
    return []


@api.post("/profiles")
def create_profile(
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new profile (auth required)."""
    # Validate incoming data with existing validators for consistency
    validated = validate_profile_data(
        {
            "name": req.name,
            "date_of_birth": req.date_of_birth,
            "time_of_birth": req.time_of_birth,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "timezone": req.timezone,
            "house_system": req.house_system,
        }
    )

    # Lightly validate optional place string to avoid junk input
    place_of_birth = (req.place_of_birth or "").strip() or None
    if place_of_birth and len(place_of_birth) > 200:
        raise HTTPException(status_code=400, detail="Place of birth is too long")

    db_profile = DBProfile(
        name=validated["name"],
        date_of_birth=validated["date_of_birth"],
        time_of_birth=validated["time_of_birth"],
        place_of_birth=place_of_birth,
        latitude=validated["latitude"],
        longitude=validated["longitude"],
        timezone=validated["timezone"],
        house_system=validated["house_system"],
        user_id=current_user.id,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return _db_profile_to_dict(db_profile)


@api.post("/daily-reading", tags=["Readings"])
def daily_reading(req: DailyRequest):
    """Get a daily astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="daily", lang=req.lang)


@api.post("/weekly-reading", tags=["Readings"])
def weekly_reading(req: WeeklyRequest):
    """Get a weekly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="weekly", lang=req.lang)


@api.post("/monthly-reading", tags=["Readings"])
def monthly_reading(req: MonthlyRequest):
    """Get a monthly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="monthly", lang=req.lang)


@api.post("/forecast", tags=["Readings"])
def generic_forecast(
    req: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get a forecast for any scope (daily, weekly, monthly)."""
    if req.profile:
        profile = _profile_to_dict(req.profile)
    elif req.profile_id:
        # Require authentication when using a stored profile and verify ownership
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        profile_obj = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_obj.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this profile")
        profile = _db_profile_to_dict(profile_obj)
    else:
        raise HTTPException(status_code=400, detail="Profile data is required")
    return build_forecast(profile, scope=req.scope, lang=req.lang)


@api.post("/feedback/section", tags=["Feedback"])
def submit_section_feedback(
    req: SectionFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Capture thumbs up/down for a reading section. Requires auth when tied to a saved profile."""
    profile_id: Optional[int] = None
    if req.profile_id is not None:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        profile = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to rate this profile")
        profile_id = profile.id

    feedback_row = SectionFeedback(
        profile_id=profile_id,
        scope=req.scope,
        section=req.section,
        vote=req.vote,
    )
    db.add(feedback_row)
    db.commit()

    return {"status": "ok"}


@api.post("/natal-profile", tags=["Readings"])
def natal_profile(req: NatalRequest):
    """Get a complete natal profile including chart and interpretations."""
    profile = _profile_to_dict(req.profile)
    return build_natal_profile(profile, lang=req.lang)


@api.post("/compatibility", tags=["Readings"])
def compatibility(req: CompatibilityRequest):
    """Get compatibility analysis between two people."""
    a = _profile_to_dict(req.person_a)
    b = _profile_to_dict(req.person_b)
    return build_compatibility(a, b, lang=req.lang)


# ========== YEAR-AHEAD FORECAST ==========


class YearAheadRequest(BaseModel):
    """Request model for year-ahead forecast."""
    profile: ProfilePayload
    year: Optional[int] = Field(None, description="Year for forecast (defaults to current year)")


@api.post("/year-ahead", tags=["Readings"])
def year_ahead_forecast(req: YearAheadRequest):
    """
    Get comprehensive year-ahead forecast including:
    - Personal Year number and themes
    - Solar Return date
    - Monthly breakdowns
    - Eclipse impacts
    - Major planetary ingresses
    """
    profile = _profile_to_dict(req.profile)
    natal = build_natal_chart(profile)
    year = req.year or datetime.now().year
    
    return build_year_ahead_forecast(profile, natal, year)


# ========== MOON PHASES & RITUALS ==========


@api.get("/moon-phase", tags=["Moon"])
def current_moon_phase():
    """
    Get current Moon phase information.
    Returns phase name, illumination, days until next phase.
    """
    return calculate_moon_phase()


@api.get("/moon-upcoming", tags=["Moon"])
def upcoming_moon_events(days: int = Query(30, ge=1, le=90, description="Days to look ahead")):
    """
    Get upcoming New and Full Moons.
    """
    return {"events": get_upcoming_moon_events(days)}


class MoonRitualRequest(BaseModel):
    """Request model for personalized Moon ritual."""
    profile: Optional[ProfilePayload] = None


@api.post("/moon-ritual", tags=["Moon"])
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


# ========== TIMING ADVISOR ==========


class TimingAdviceRequest(BaseModel):
    """Request model for timing advice."""
    activity: str = Field(..., description="Activity type: business_meeting, travel, romance_date, signing_contracts, job_interview, starting_project, creative_work, medical_procedure, financial_decision, meditation_spiritual")
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(40.7128, ge=-90, le=90, description="Location latitude for planetary hours")
    longitude: float = Field(-74.006, ge=-180, le=180, description="Location longitude for planetary hours")
    tz: str = Field("UTC", description="Timezone for calculations")


@api.post("/timing/advice", tags=["Timing"])
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
            detail=f"Invalid activity. Valid options: {', '.join(valid_activities)}"
        )
    
    # Build transit chart for current time
    from datetime import datetime as dt
    
    personal_day = None
    transit_chart = {}
    
    if req.profile:
        profile_dict = _profile_to_dict(req.profile)
        natal_chart = build_natal_chart(profile_dict)
        transit_chart = natal_chart  # Use natal as proxy (timing functions use planet positions)
        
        # Get personal day from numerology
        numerology = build_numerology(
            profile_dict["name"],
            profile_dict["date_of_birth"],
            datetime.now(timezone.utc),
        )
        personal_day = numerology.get("personal_day")
    else:
        # Build a minimal transit chart for current time
        transit_chart = {
            "planets": [],  # Will be populated by detect_retrogrades if needed
        }
    
    return get_timing_advice(
        activity=req.activity,
        transit_chart=transit_chart,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.tz,
        personal_day=personal_day,
    )


class BestDaysRequest(BaseModel):
    """Request model for finding best days."""
    activity: str = Field(..., description="Activity type")
    days_ahead: int = Field(7, ge=1, le=14, description="Days to look ahead")
    profile: Optional[ProfilePayload] = None
    latitude: float = Field(40.7128, ge=-90, le=90)
    longitude: float = Field(-74.006, ge=-180, le=180)
    tz: str = Field("UTC", description="Timezone")


@api.post("/timing/best-days", tags=["Timing"])
def find_best_days_endpoint(req: BestDaysRequest):
    """
    Find the best days for an activity in the upcoming period.
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
        )
    }


@api.get("/timing/activities", tags=["Timing"])
def list_timing_activities():
    """
    Get list of supported activities with their descriptions and favorable conditions.
    """
    return {
        "activities": get_available_activities()
    }


# =============================================================================
# Journal & Accountability Endpoints
# =============================================================================

class JournalEntryRequest(BaseModel):
    """Request to add or update a journal entry for a reading."""
    reading_id: int
    entry: str = Field(..., min_length=1, max_length=5000)


class OutcomeRequest(BaseModel):
    """Request to record prediction outcome."""
    reading_id: int
    outcome: str = Field(..., pattern="^(yes|no|partial|neutral)$")
    notes: Optional[str] = None


class AccountabilityReportRequest(BaseModel):
    """Request for accountability report."""
    profile_id: int
    period: str = Field(default="month", pattern="^(week|month|year)$")


@api.post("/journal/entry", tags=["Journal"])
def add_journal_entry_endpoint(
    req: JournalEntryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add or update a journal entry for a reading.
    Requires authentication.
    """
    # Get the reading
    reading = db.query(DBReading).filter(DBReading.id == req.reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    # Verify user owns this reading via profile
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this reading")
    
    # Update the journal entry
    reading.journal = req.entry
    db.commit()
    
    entry_data = add_journal_entry(req.reading_id, req.entry)
    
    return {
        "success": True,
        "message": "Journal entry saved",
        "entry": entry_data
    }


@api.post("/journal/outcome", tags=["Journal"])
def record_outcome_endpoint(
    req: OutcomeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record whether a prediction came true.
    Requires authentication.
    """
    # Get the reading
    reading = db.query(DBReading).filter(DBReading.id == req.reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    # Verify user owns this reading
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this reading")
    
    # Update feedback
    reading.feedback = req.outcome
    db.commit()
    
    outcome_data = record_outcome(req.reading_id, req.outcome, notes=req.notes or "")
    
    return {
        "success": True,
        "message": "Outcome recorded",
        "outcome": outcome_data
    }


@api.get("/journal/readings/{profile_id}", tags=["Journal"])
def get_journal_readings(
    profile_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get readings for journaling view with feedback and journal status.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    # Get readings with pagination
    readings = (
        db.query(DBReading)
        .filter(DBReading.profile_id == profile_id)
        .order_by(DBReading.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    total = db.query(DBReading).filter(DBReading.profile_id == profile_id).count()
    
    return {
        "profile_id": profile_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "readings": [
            format_reading_for_journal({
                "id": r.id,
                "scope": r.scope,
                "date": r.date,
                "content": r.content,
                "feedback": r.feedback,
                "journal": r.journal or ""
            })
            for r in readings
        ]
    }


@api.get("/journal/reading/{reading_id}", tags=["Journal"])
def get_single_reading_journal(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single reading with full journal and content.
    Requires authentication.
    """
    reading = db.query(DBReading).filter(DBReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    # Verify user owns this reading
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this reading")
    
    import json
    content = reading.content
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {"raw": content}
    
    return {
        "id": reading.id,
        "scope": reading.scope,
        "date": reading.date,
        "content": content,
        "feedback": reading.feedback,
        "journal": reading.journal or "",
        "created_at": reading.created_at.isoformat() if reading.created_at else None
    }


@api.get("/journal/stats/{profile_id}", tags=["Journal"])
def get_journal_stats(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get accuracy statistics for a profile's readings.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    # Get all readings for stats
    readings = db.query(DBReading).filter(DBReading.profile_id == profile_id).all()
    
    readings_data = [
        {
            "id": r.id,
            "scope": r.scope,
            "date": r.date,
            "feedback": r.feedback,
            "journal": r.journal or ""
        }
        for r in readings
    ]
    
    stats = calculate_accuracy_stats(readings_data)
    insights = get_reading_insights(readings_data)
    
    return {
        "profile_id": profile_id,
        "stats": stats,
        "insights": insights
    }


@api.get("/journal/patterns/{profile_id}", tags=["Journal"])
def get_reading_patterns(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze prediction patterns over time.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    readings = db.query(DBReading).filter(DBReading.profile_id == profile_id).all()
    
    readings_data = [
        {
            "id": r.id,
            "scope": r.scope,
            "date": r.date,
            "feedback": r.feedback
        }
        for r in readings
    ]
    
    patterns = analyze_prediction_patterns(readings_data)
    
    return {
        "profile_id": profile_id,
        "patterns": patterns
    }


@api.post("/journal/report", tags=["Journal"])
def get_accountability_report(
    req: AccountabilityReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive accountability report.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    # Calculate date range based on period
    now = datetime.now(timezone.utc)
    if req.period == "week":
        start_date = now - timedelta(days=7)
    elif req.period == "month":
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Get readings in range
    readings = (
        db.query(DBReading)
        .filter(
            DBReading.profile_id == req.profile_id,
            DBReading.date >= start_date.isoformat()
        )
        .all()
    )
    
    readings_data = [
        {
            "id": r.id,
            "scope": r.scope,
            "date": r.date,
            "feedback": r.feedback,
            "journal": r.journal or "",
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in readings
    ]
    
    report = create_accountability_report(readings_data, req.period)
    
    return {
        "profile_id": req.profile_id,
        "report": report
    }


@api.get("/journal/prompts", tags=["Journal"])
def get_prompts(
    scope: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    themes: Optional[str] = Query(default=None, description="Comma-separated themes")
):
    """
    Get journal prompts for reflection.
    No authentication required.
    """
    theme_list = themes.split(",") if themes else None
    prompts = get_journal_prompts(scope, theme_list)
    
    return {
        "scope": scope,
        "prompts": prompts
    }


# =============================================================================
# Relationship Timeline Endpoints
# =============================================================================

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


@api.post("/relationship/timeline", tags=["Relationships"])
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


@api.post("/relationship/timing", tags=["Relationships"])
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


@api.get("/relationship/best-days/{sun_sign}", tags=["Relationships"])
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
        "best_days": best_days[:10],  # Top 10
        "top_day": best_days[0] if best_days else None
    }


@api.get("/relationship/events", tags=["Relationships"])
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


@api.get("/relationship/venus-status", tags=["Relationships"])
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


@api.get("/relationship/phases", tags=["Relationships"])
def get_phases():
    """
    Get information about relationship phases and their astrological houses.
    """
    return get_relationship_phases()


# =============================================================================
# Habit Tracker with Lunar Cycles Endpoints
# =============================================================================

class HabitCreateRequest(BaseModel):
    """Request to create a new habit."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., description="Habit category key")
    frequency: str = Field(default="daily", pattern="^(daily|weekly|lunar_cycle)$")
    target_count: int = Field(default=1, ge=1, le=10)
    description: Optional[str] = Field(default="", max_length=500)


class HabitLogRequest(BaseModel):
    """Request to log a habit completion."""
    habit_id: int
    notes: Optional[str] = Field(default="", max_length=500)


class HabitAnalyticsRequest(BaseModel):
    """Request for habit analytics."""
    habit_id: int
    period_days: int = Field(default=30, ge=7, le=365)


class HabitForecastRequest(BaseModel):
    """Request for today's habit forecast."""
    habits: List[Dict[str, Any]]
    completions_today: Optional[List[int]] = None
    
    model_config = {"extra": "allow"}


class StreakRequest(BaseModel):
    """Request for streak calculation."""
    completions: List[Dict[str, Any]]
    
    model_config = {"extra": "allow"}


# Rebuild models to resolve forward references from __future__ annotations
HabitForecastRequest.model_rebuild()
StreakRequest.model_rebuild()


@api.get("/habits/categories", tags=["Habits"])
def get_habit_categories():
    """
    Get all available habit categories with their descriptions
    and lunar phase recommendations.
    """
    categories = []
    for key, cat in HABIT_CATEGORIES.items():
        categories.append({
            "id": key,
            "name": cat["name"],
            "emoji": cat["emoji"],
            "description": cat["description"],
            "best_phases": cat["best_phases"],
            "avoid_phases": cat["avoid_phases"]
        })
    return {"categories": categories}


@api.get("/habits/lunar-guidance", tags=["Habits"])
def get_lunar_guidance():
    """
    Get habit guidance for all moon phases.
    """
    phases = []
    for key, phase in LUNAR_HABIT_GUIDANCE.items():
        phases.append({
            "id": key,
            "name": phase["phase_name"],
            "emoji": phase["emoji"],
            "theme": phase["theme"],
            "best_for": phase["best_for"],
            "avoid": phase["avoid"],
            "energy": phase["energy"],
            "ideal_habits": phase["ideal_habits"]
        })
    return {"phases": phases}


@api.get("/habits/lunar-guidance/{phase}", tags=["Habits"])
def get_phase_guidance(phase: str):
    """
    Get habit guidance for a specific moon phase.
    """
    valid_phases = list(LUNAR_HABIT_GUIDANCE.keys())
    if phase not in valid_phases:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {valid_phases}"
        )
    
    phase_info = LUNAR_HABIT_GUIDANCE[phase]
    return {
        "phase": phase,
        "phase_name": phase_info["phase_name"],
        "emoji": phase_info["emoji"],
        "theme": phase_info["theme"],
        "energy": phase_info["energy"],
        "best_for": phase_info["best_for"],
        "avoid": phase_info["avoid"],
        "ideal_habits": phase_info["ideal_habits"],
        "power_modifier": phase_info["power_score_modifier"]
    }


@api.post("/habits/alignment", tags=["Habits"])
def check_habit_alignment(
    category: str = Query(..., description="Habit category key"),
    moon_phase: str = Query(..., description="Moon phase key")
):
    """
    Check how well a habit category aligns with a moon phase.
    Returns alignment score and guidance.
    """
    if category not in HABIT_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(HABIT_CATEGORIES.keys())}"
        )
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return calculate_lunar_alignment_score(category, moon_phase)


@api.post("/habits/recommendations", tags=["Habits"])
def get_recommendations(
    moon_phase: str = Query(..., description="Current moon phase key"),
    existing_habits: Optional[List[Dict[str, Any]]] = None
):
    """
    Get habit recommendations based on the current moon phase.
    Optionally provide existing habits for personalized suggestions.
    """
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return get_lunar_habit_recommendations(moon_phase, existing_habits)


@api.post("/habits/create", tags=["Habits"])
def create_new_habit(req: HabitCreateRequest):
    """
    Create a new habit definition.
    Returns the habit object (not persisted - for session use).
    """
    if req.category not in HABIT_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(HABIT_CATEGORIES.keys())}"
        )
    
    habit = create_habit(
        name=req.name,
        category=req.category,
        frequency=req.frequency,
        target_count=req.target_count,
        description=req.description
    )
    
    return {"success": True, "habit": habit}


@api.post("/habits/log", tags=["Habits"])
def log_completion(
    req: HabitLogRequest,
    moon_phase: Optional[str] = Query(default=None, description="Current moon phase")
):
    """
    Log a habit completion.
    Returns the completion record.
    """
    completion = log_habit_completion(
        habit_id=req.habit_id,
        moon_phase=moon_phase,
        notes=req.notes
    )
    
    return {"success": True, "completion": completion}


@api.post("/habits/streak", tags=["Habits"])
def calculate_streak(
    req: StreakRequest,
    frequency: str = Query(default="daily", pattern="^(daily|weekly|lunar_cycle)$")
):
    """
    Calculate habit streak from a list of completions.
    """
    return get_habit_streak(req.completions, frequency)


@api.post("/habits/analytics", tags=["Habits"])
def get_analytics(
    habit: Dict[str, Any],
    completions: List[Dict[str, Any]],
    period_days: int = Query(default=30, ge=7, le=365)
):
    """
    Get detailed analytics for a habit over a period.
    """
    return calculate_habit_analytics(habit, completions, period_days)


@api.post("/habits/today", tags=["Habits"])
def get_today_forecast(
    req: HabitForecastRequest,
    moon_phase: str = Query(..., description="Current moon phase key")
):
    """
    Get today's habit forecast with lunar alignment for each habit.
    """
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return get_today_habit_forecast(
        habits=req.habits,
        moon_phase=moon_phase,
        completions_today=req.completions_today
    )


@api.post("/habits/lunar-report", tags=["Habits"])
def get_lunar_report(
    habits: List[Dict[str, Any]],
    completions: List[Dict[str, Any]],
    cycle_days: int = Query(default=29, ge=14, le=45)
):
    """
    Generate a lunar cycle report for habits.
    Analyzes performance over a complete moon cycle.
    """
    return get_lunar_cycle_report(habits, completions, cycle_days)


class NumerologyRequest(BaseModel):
    """Request model for numerology profile - supports session-only profiles."""
    profile: ProfilePayload


@api.post("/numerology", tags=["Numerology"])
def numerology_from_payload(req: NumerologyRequest):
    """Get numerology profile from profile data (no database lookup)."""
    return build_numerology(
        req.profile.name,
        req.profile.date_of_birth,
        datetime.now(timezone.utc),
    )


@api.get("/numerology/profile/{profile_id}", tags=["Numerology"])
def numerology_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get numerology profile for a saved profile (auth + ownership required)."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    return build_numerology(
        profile.name,
        profile.date_of_birth,
        datetime.now(timezone.utc),
    )


@api.get("/learn/zodiac")
def learn_zodiac(
    limit: int = Query(default=None, ge=1, le=50, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """Get zodiac glossary with optional pagination."""
    items = list(ZODIAC_GLOSSARY.items())
    total = len(items)

    if limit is not None:
        # Return paginated response
        paginated_items = items[offset : offset + limit]
        return {
            "items": [{"key": k, "data": v} for k, v in paginated_items],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    # Return full glossary for backward compatibility
    return ZODIAC_GLOSSARY


@api.get("/learn/numerology")
def learn_numerology(
    limit: int = Query(default=None, ge=1, le=50, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
):
    """Get numerology glossary with optional pagination."""
    items = list(NUMEROLOGY_GLOSSARY.items())
    total = len(items)

    if limit is not None:
        # Return paginated response
        paginated_items = items[offset : offset + limit]
        return {
            "items": [{"key": k, "data": v} for k, v in paginated_items],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    # Return full glossary for backward compatibility
    return NUMEROLOGY_GLOSSARY


# ========== GEOCODING ENDPOINTS ==========


@api.get("/geocode/search")
def geocode_search(
    q: str = Query(..., min_length=2, description="City name to search")
):
    """Search for cities and return location data with timezone."""
    from .geocode_service import geocode_sync

    try:
        results = geocode_sync(q, limit=5)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")


@api.get("/geocode/timezone")
def get_timezone(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Get timezone for coordinates."""
    from .geocode_service import get_iana_timezone

    tz = get_iana_timezone(lat, lon)
    return {"latitude": lat, "longitude": lon, "timezone": tz}


# ========== PDF EXPORT ENDPOINTS ==========


@api.post("/export/natal-pdf")
def export_natal_pdf(req: NatalRequest):
    """Generate a downloadable PDF natal chart report."""
    from fastapi.responses import StreamingResponse

    from .pdf_service import HAS_REPORTLAB, generate_natal_pdf

    if not HAS_REPORTLAB:
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available. Install reportlab: pip install reportlab",
        )

    profile = _profile_to_dict(req.profile)
    natal_data = build_natal_profile(profile)
    numerology_data = build_numerology(
        profile["name"],
        profile["date_of_birth"],
        datetime.now(timezone.utc),
    )

    pdf_bytes = generate_natal_pdf(profile, natal_data, numerology_data)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=natal_report_{profile['name'].replace(' ', '_')}.pdf"
        },
    )


@api.post("/export/compatibility-pdf")
def export_compatibility_pdf(req: CompatibilityRequest):
    """Generate a downloadable PDF compatibility report."""
    from fastapi.responses import StreamingResponse

    from .pdf_service import HAS_REPORTLAB, generate_compatibility_pdf

    if not HAS_REPORTLAB:
        raise HTTPException(status_code=501, detail="PDF generation not available")

    person_a = _profile_to_dict(req.person_a)
    person_b = _profile_to_dict(req.person_b)
    compat_data = build_compatibility(person_a, person_b)

    pdf_bytes = generate_compatibility_pdf(person_a, person_b, compat_data)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=compatibility_report.pdf"
        },
    )


# ========== TRANSIT ALERTS ENDPOINTS ==========


@api.get("/transits/daily/{profile_id}")
def get_daily_transits(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's transit aspects for a profile (auth + ownership required)."""
    from .transit_alerts import check_daily_transits

    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    profile_dict = _db_profile_to_dict(profile)
    return check_daily_transits(profile_dict)


@api.post("/transits/daily")
def get_daily_transits_post(
    req: NatalRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get today's transit aspects for a profile payload.
    Requires auth + ownership when a stored profile_id is referenced; allows ad-hoc payloads without auth.
    """
    from .transit_alerts import check_daily_transits

    profile: Dict
    if hasattr(req.profile, "id") and req.profile.id:  # defensive: if future schema adds id
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        profile_obj = db.query(DBProfile).filter(DBProfile.id == req.profile.id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_obj.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this profile")
        profile = _db_profile_to_dict(profile_obj)
    else:
        profile = _profile_to_dict(req.profile)

    return check_daily_transits(profile)


@api.post("/transits/subscribe")
def subscribe_transit_alerts(
    profile_id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subscribe to daily transit alert emails for a profile.
    Currently stubbed: validates ownership and returns a not-implemented notice.
    """
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your profile")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transit alert subscriptions are not implemented yet",
    )


# ========== CHART DATA ENDPOINTS ==========


@api.post("/chart/natal", tags=["Charts"])
def get_natal_chart(req: NatalRequest):
    """
    Get raw natal chart data for visualization.
    
    Returns planetary positions, house cusps, and aspects.
    Results are cached for 1 hour for performance.
    """
    from .chart_service import build_natal_chart

    profile = _profile_to_dict(req.profile)
    return cached_build_chart(profile, "natal", build_natal_chart)


@api.post("/chart/synastry", tags=["Charts"])
def get_synastry_chart(req: CompatibilityRequest):
    """
    Get synastry chart data for two people.
    
    Returns both natal charts plus aspects between them.
    """
    from .chart_service import build_natal_chart
    from .transit_alerts import find_transit_aspects

    person_a = _profile_to_dict(req.person_a)
    person_b = _profile_to_dict(req.person_b)

    # Use caching for individual charts
    chart_a = cached_build_chart(person_a, "natal", build_natal_chart)
    chart_b = cached_build_chart(person_b, "natal", build_natal_chart)

    # Find aspects between the two charts
    synastry_aspects = find_transit_aspects(chart_a, chart_b)

    # Get compatibility data
    compat = build_compatibility(person_a, person_b)

    return {
        "person_a": {"name": person_a["name"], "chart": chart_a},
        "person_b": {"name": person_b["name"], "chart": chart_b},
        "synastry_aspects": synastry_aspects,
        "compatibility": compat,
    }


# ========== DAILY FEATURES ENDPOINTS ==========


class DailyFeaturesRequest(BaseModel):
    """Request for daily cosmic features."""
    birth_date: str
    sun_sign: Optional[str] = None


@api.post("/daily-features")
def get_daily_features_endpoint(req: DailyFeaturesRequest):
    """Get daily lucky number, color, planet, affirmation, and tarot energy."""
    from .engine.daily_features import get_daily_features
    
    features = get_daily_features(req.birth_date, req.sun_sign)
    return features


@api.post("/tarot/draw")
def draw_tarot_card():
    """Draw a single tarot card with meaning and advice."""
    from .engine.daily_features import get_tarot_card
    
    card = get_tarot_card()
    return card


class YesNoRequest(BaseModel):
    """Request for yes/no cosmic reading."""
    question: str
    birth_date: Optional[str] = None


@api.post("/oracle/yes-no")
def get_yes_no_answer(req: YesNoRequest):
    """Get a cosmic yes/no reading for a question."""
    from .engine.daily_features import get_yes_no_reading
    
    result = get_yes_no_reading(req.question, req.birth_date)
    return result


class MoodForecastRequest(BaseModel):
    """Request for mood forecast."""
    sun_sign: str
    moon_sign: Optional[str] = None


@api.post("/forecast/mood")
def get_mood_forecast_endpoint(req: MoodForecastRequest):
    """Get today's mood forecast based on astrological influences."""
    from .engine.daily_features import get_mood_forecast
    
    forecast = get_mood_forecast(req.sun_sign, req.moon_sign)
    return forecast


# ========== COSMIC GUIDE CHAT ENDPOINTS ==========


class CosmicGuideRequest(BaseModel):
    """Request for Cosmic Guide chat."""
    message: str
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    rising_sign: Optional[str] = None
    history: Optional[List[dict]] = None


@api.post("/cosmic-guide/chat")
async def chat_with_guide(req: CosmicGuideRequest):
    """Chat with the AI Cosmic Guide for mystical wisdom."""
    from .engine.cosmic_guide import ask_cosmic_guide
    
    # Build chart-like data from context
    chart_data = None
    if req.sun_sign or req.moon_sign:
        planets = []
        if req.sun_sign:
            planets.append({"name": "Sun", "sign": req.sun_sign})
        if req.moon_sign:
            planets.append({"name": "Moon", "sign": req.moon_sign})
        if planets:
            chart_data = {"planets": planets}
            if req.rising_sign:
                chart_data["houses"] = [{"house": 1, "sign": req.rising_sign}]
    
    result = await ask_cosmic_guide(
        question=req.message,
        chart_data=chart_data,
        conversation_history=req.history,
    )
    
    # Return full result for debugging, frontend uses 'response' field
    return result


class QuickInsightRequest(BaseModel):
    """Request for quick cosmic insight."""
    topic: str
    sun_sign: Optional[str] = None


@api.post("/cosmic-guide/insight")
async def get_insight(req: QuickInsightRequest):
    """Get a quick cosmic insight on a specific topic."""
    from .engine.cosmic_guide import get_quick_insight
    
    insight = await get_quick_insight(req.topic, req.sun_sign)
    return {"insight": insight}


# ========== LEARNING CONTENT ENDPOINTS ==========


@api.get("/learn/modules")
def list_learning_modules():
    """List all available learning modules."""
    from .engine.learning_content import (
        MOON_SIGNS, RISING_SIGNS, ELEMENTS_AND_MODALITIES,
        RETROGRADE_INFO, MINI_COURSES
    )
    
    return {
        "modules": [
            {
                "id": "moon_signs",
                "title": "Moon Signs: Your Emotional Self",
                "description": "Discover how your Moon sign shapes your inner world",
                "item_count": len(MOON_SIGNS)
            },
            {
                "id": "rising_signs",
                "title": "Rising Signs: Your Cosmic Mask",
                "description": "Learn how your Ascendant influences first impressions",
                "item_count": len(RISING_SIGNS)
            },
            {
                "id": "elements",
                "title": "Elements & Modalities",
                "description": "Fire, Earth, Air, Water and Cardinal, Fixed, Mutable",
                "item_count": len(ELEMENTS_AND_MODALITIES.get("elements", {})) + len(ELEMENTS_AND_MODALITIES.get("modalities", {}))
            },
            {
                "id": "retrogrades",
                "title": "Planetary Retrogrades",
                "description": "What happens when planets appear to move backward",
                "item_count": len(RETROGRADE_INFO)
            },
            {
                "id": "courses",
                "title": "Mini Courses",
                "description": "Structured lessons for deeper learning",
                "item_count": len(MINI_COURSES)
            }
        ]
    }


@api.get("/learn/module/{module_id}")
def get_module_content(module_id: str):
    """Get full content for a learning module."""
    from .engine.learning_content import get_learning_module
    
    content = get_learning_module(module_id)
    if not content:
        raise HTTPException(status_code=404, detail="Module not found")
    return content


@api.get("/learn/course/{course_id}")
def get_course_content(course_id: str):
    """Get a specific mini course with all lessons."""
    from .engine.learning_content import MINI_COURSES
    
    course = MINI_COURSES.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@api.get("/learn/course/{course_id}/lesson/{lesson_number}")
def get_lesson_content(course_id: str, lesson_number: int):
    """Get a specific lesson from a mini course."""
    from .engine.learning_content import get_lesson
    
    lesson = get_lesson(course_id, lesson_number)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


class SearchLearningRequest(BaseModel):
    """Request to search learning content."""
    query: str


@api.post("/learn/search")
def search_learning(req: SearchLearningRequest):
    """Search across all learning content."""
    from .engine.learning_content import search_learning_content
    
    results = search_learning_content(req.query)
    return {"results": results}


@api.get("/debug/ephemeris", tags=["System"])
def debug_ephemeris():
    """Debug endpoint to check ephemeris files."""
    import swisseph as swe
    ephe_path = EPHEMERIS_PATH
    files = []
    exists = os.path.isdir(ephe_path)
    if exists:
        files = os.listdir(ephe_path)
    # Test swisseph
    swe.set_ephe_path(ephe_path)
    try:
        jd = swe.julday(1990, 6, 15, 12.0)
        result, flags = swe.calc_ut(jd, swe.SUN)
        sun_works = True
        sun_lon = result[0]
    except Exception as e:
        sun_works = False
        sun_lon = str(e)
    # Test asteroid (Chiron = 15)
    try:
        result, flags = swe.calc_ut(jd, swe.CHIRON)
        chiron_works = True
        chiron_lon = result[0]
    except Exception as e:
        chiron_works = False
        chiron_lon = str(e)
    return {
        "ephemeris_path": ephe_path,
        "path_exists": exists,
        "files": files,
        "sun_works": sun_works,
        "sun_longitude": sun_lon,
        "chiron_works": chiron_works,
        "chiron_result": chiron_lon,
    }


@api.get("/health", tags=["System"])
def health():
    """Health check endpoint with system status."""
    # Simple health check that responds quickly
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api.post("/cache/clear", tags=["System"])
def clear_cache():
    """
    Clear the chart calculation cache.
    
    Use this if you need to force recalculation of charts.
    Returns the number of entries cleared.
    """
    cache = get_chart_cache()
    count = cache.clear()
    return {
        "status": "ok",
        "entries_cleared": count,
        "message": f"Cleared {count} cached chart calculations"
    }


@api.post("/cache/cleanup", tags=["System"])
def cleanup_expired_cache():
    """
    Remove expired entries from the chart cache.
    
    This happens automatically on access, but can be triggered manually.
    """
    cache = get_chart_cache()
    count = cache.cleanup_expired()
    stats = cache.get_stats()
    return {
        "status": "ok",
        "expired_removed": count,
        "current_size": stats["size"],
        "message": f"Removed {count} expired entries"
    }


# Startup for Railway / Render / etc - properly handles PORT env variable
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    # In Docker container: working directory is /app so module is app.main
    # In development: use the api object directly
    uvicorn.run(api, host="0.0.0.0", port=port)
# trigger deploy
