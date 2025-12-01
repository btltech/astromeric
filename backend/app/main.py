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
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

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

api = FastAPI(title="AstroNumerology API", version="3.2.0")
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


class Location(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = "UTC"


class ProfilePayload(BaseModel):
    name: str
    date_of_birth: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")
    time_of_birth: Optional[str] = None
    location: Optional[Location] = None
    house_system: Optional[str] = "Placidus"


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
    """Get all profiles. If authenticated, returns user's profiles only."""
    if current_user:
        profiles = (
            db.query(DBProfile)
            .filter(DBProfile.user_id == current_user.id)
            .order_by(DBProfile.created_at.desc())
            .all()
        )
    else:
        # For guest users, return profiles without user_id (guest profiles)
        profiles = (
            db.query(DBProfile)
            .filter(DBProfile.user_id.is_(None))
            .order_by(DBProfile.created_at.desc())
            .all()
        )
    return [_db_profile_to_dict(p) for p in profiles]


@api.post("/profiles")
def create_profile(
    req: CreateProfileRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Create a new profile. Associates with user if authenticated."""
    db_profile = DBProfile(
        name=req.name,
        date_of_birth=req.date_of_birth,
        time_of_birth=req.time_of_birth,
        place_of_birth=req.place_of_birth,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.timezone or "UTC",
        house_system=req.house_system or "Placidus",
        user_id=current_user.id if current_user else None,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return _db_profile_to_dict(db_profile)


@api.post("/daily-reading")
def daily_reading(req: DailyRequest):
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="daily")


@api.post("/weekly-reading")
def weekly_reading(req: WeeklyRequest):
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="weekly")


@api.post("/monthly-reading")
def monthly_reading(req: MonthlyRequest):
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="monthly")


@api.post("/forecast")
def generic_forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    if req.profile:
        profile = _profile_to_dict(req.profile)
    elif req.profile_id:
        profile = _profile_from_id(req.profile_id, db)
    else:
        raise HTTPException(status_code=400, detail="Profile data is required")
    return build_forecast(profile, scope=req.scope)


@api.post("/natal-profile")
def natal_profile(req: NatalRequest):
    profile = _profile_to_dict(req.profile)
    return build_natal_profile(profile)


@api.post("/compatibility")
def compatibility(req: CompatibilityRequest):
    a = _profile_to_dict(req.person_a)
    b = _profile_to_dict(req.person_b)
    return build_compatibility(a, b)


@api.get("/numerology/profile/{profile_id}")
def numerology_profile(profile_id: int, db: Session = Depends(get_db)):
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


@api.post("/chart/natal")
def get_natal_chart(req: NatalRequest):
    """Get raw natal chart data for visualization."""
    from .chart_service import build_natal_chart

    profile = _profile_to_dict(req.profile)
    return build_natal_chart(profile)


@api.post("/chart/synastry")
def get_synastry_chart(req: CompatibilityRequest):
    """Get synastry chart data for two people."""
    from .chart_service import build_natal_chart
    from .transit_alerts import find_transit_aspects

    person_a = _profile_to_dict(req.person_a)
    person_b = _profile_to_dict(req.person_b)

    chart_a = build_natal_chart(person_a)
    chart_b = build_natal_chart(person_b)

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


@api.get("/health")
def health():
    redis_status = "disconnected"
    if os.getenv("REDIS_URL"):
        try:
            from .engine.fusion import _get_redis_client

            redis_client = _get_redis_client()
            if redis_client and redis_client.ping():
                redis_status = "connected"
        except Exception:
            redis_status = "error"

    return {
        "status": "ok",
        "ephemeris_path": EPHEMERIS_PATH,
        "flatlib_available": bool(HAS_FLATLIB),
        "redis_status": redis_status,
        "features": {
            "pdf_export": True,
            "transit_alerts": True,
            "geocoding": True,
            "synastry": True,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Startup for Railway / Render / etc - properly handles PORT env variable
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    # In Docker container: working directory is /app so module is app.main
    # In development: use the api object directly
    uvicorn.run(api, host="0.0.0.0", port=port)
