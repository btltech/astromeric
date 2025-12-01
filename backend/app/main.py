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
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

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
from .chart_service import EPHEMERIS_PATH, HAS_FLATLIB
from .engine.glossary import NUMEROLOGY_GLOSSARY, ZODIAC_GLOSSARY
from .models import Profile as DBProfile
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
No rate limits currently. Be respectful of server resources.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)
app = api  # alias for uvicorn import style

# Allow configurable CORS via env; default open for dev
allow_origins_env = os.getenv("ALLOW_ORIGINS", "")
if allow_origins_env:
    allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]
else:
    allow_origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
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


class WeeklyRequest(BaseModel):
    profile: ProfilePayload


class MonthlyRequest(BaseModel):
    profile: ProfilePayload


class ForecastRequest(BaseModel):
    profile: Optional[ProfilePayload] = None
    profile_id: Optional[int] = None
    scope: str = Field("daily", pattern=r"^(daily|weekly|monthly)$")


class NatalRequest(BaseModel):
    profile: ProfilePayload


class CompatibilityRequest(BaseModel):
    person_a: ProfilePayload
    person_b: ProfilePayload


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== AUTH ENDPOINTS ==========


@api.post("/auth/register", response_model=Token)
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
        "user": {"id": user.id, "email": user.email},
    }


@api.post("/auth/login", response_model=Token)
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
        "user": {"id": user.id, "email": user.email},
    }


@api.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {"id": current_user.id, "email": current_user.email}


# ========== AI ENDPOINTS ==========


@api.post("/ai/explain", response_model=AIExplainResponse)
def explain_reading(payload: AIExplainRequest):
    sections = [section.dict() for section in payload.sections]
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
    loc = payload.location.dict() if payload.location else {}
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
    """
    Profile storage is disabled for privacy.
    Always returns empty list - profiles are session-only on frontend.
    """
    return []


@api.post("/profiles")
def create_profile(
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Profile storage is disabled for privacy.
    Returns a fake ID but does NOT save to database.
    Profiles are session-only on frontend.
    """
    # Return a response that looks successful but doesn't persist anything
    return {
        "id": -1,  # Negative ID indicates session-only
        "name": req.name,
        "date_of_birth": req.date_of_birth,
        "time_of_birth": req.time_of_birth,
        "place_of_birth": req.place_of_birth,
        "latitude": req.latitude if req.latitude is not None else 0.0,
        "longitude": req.longitude if req.longitude is not None else 0.0,
        "timezone": req.timezone or "UTC",
        "house_system": req.house_system or "Placidus",
    }


@api.post("/daily-reading", tags=["Readings"])
def daily_reading(req: DailyRequest):
    """Get a daily astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="daily")


@api.post("/weekly-reading", tags=["Readings"])
def weekly_reading(req: WeeklyRequest):
    """Get a weekly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="weekly")


@api.post("/monthly-reading", tags=["Readings"])
def monthly_reading(req: MonthlyRequest):
    """Get a monthly astrological and numerological reading."""
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="monthly")


@api.post("/forecast", tags=["Readings"])
def generic_forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    """Get a forecast for any scope (daily, weekly, monthly)."""
    if req.profile:
        profile = _profile_to_dict(req.profile)
    elif req.profile_id:
        profile = _profile_from_id(req.profile_id, db)
    else:
        raise HTTPException(status_code=400, detail="Profile data is required")
    return build_forecast(profile, scope=req.scope)


@api.post("/natal-profile", tags=["Readings"])
def natal_profile(req: NatalRequest):
    """Get a complete natal profile including chart and interpretations."""
    profile = _profile_to_dict(req.profile)
    return build_natal_profile(profile)


@api.post("/compatibility", tags=["Readings"])
def compatibility(req: CompatibilityRequest):
    """Get compatibility analysis between two people."""
    a = _profile_to_dict(req.person_a)
    b = _profile_to_dict(req.person_b)
    return build_compatibility(a, b)


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
def numerology_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get numerology profile for a saved profile."""
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
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
def get_daily_transits(profile_id: int, db: Session = Depends(get_db)):
    """Get today's transit aspects for a profile."""
    from .transit_alerts import check_daily_transits

    profile = _profile_from_id(profile_id, db)
    return check_daily_transits(profile)


@api.post("/transits/daily")
def get_daily_transits_post(req: NatalRequest):
    """Get today's transit aspects for a profile payload."""
    from .transit_alerts import check_daily_transits

    profile = _profile_to_dict(req.profile)
    return check_daily_transits(profile)


@api.post("/transits/subscribe")
def subscribe_transit_alerts(
    profile_id: int,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subscribe to daily transit alert emails for a profile."""
    # In a full implementation, this would store the subscription
    # For now, just validate and return success
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your profile")

    # TODO: Store subscription in database
    return {
        "status": "subscribed",
        "profile_id": profile_id,
        "email": email,
        "message": "You will receive daily transit alerts at this email.",
    }


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
    from .engine.cosmic_guide import chat_with_cosmic_guide
    
    user_context = {}
    if req.sun_sign:
        user_context["sun_sign"] = req.sun_sign
    if req.moon_sign:
        user_context["moon_sign"] = req.moon_sign
    if req.rising_sign:
        user_context["rising_sign"] = req.rising_sign
    
    response = await chat_with_cosmic_guide(
        req.message, 
        user_context if user_context else None,
        req.history
    )
    return {"response": response}


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


@api.get("/health", tags=["System"])
def health():
    """Health check endpoint with system status."""
    redis_status = "disconnected"
    if os.getenv("REDIS_URL"):
        try:
            from .engine.fusion import _get_redis_client

            redis_client = _get_redis_client()
            if redis_client and redis_client.ping():
                redis_status = "connected"
        except Exception:
            redis_status = "error"

    # Get cache stats
    cache_stats = get_chart_cache().get_stats()

    return {
        "status": "ok",
        "ephemeris_path": EPHEMERIS_PATH,
        "flatlib_available": bool(HAS_FLATLIB),
        "redis_status": redis_status,
        "cache": cache_stats,
        "features": {
            "pdf_export": True,
            "transit_alerts": True,
            "geocoding": True,
            "synastry": True,
            "daily_features": True,
            "cosmic_guide": True,
            "learning": True,
            "tarot": True,
            "oracle": True,
        },
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
