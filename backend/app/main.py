"""
main.py
--------
FastAPI entrypoint exposing product endpoints.

Endpoints:
- POST /daily-reading
- POST /weekly-reading
- POST /natal-profile
- POST /compatibility

Deployment notes:
- Swiss Ephemeris files must live at /app/ephemeris (or set EPHEMERIS_PATH).
- Railway start command: uvicorn main:api --host 0.0.0.0 --port $PORT
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .products import build_forecast, build_natal_profile, build_compatibility
from .chart_service import EPHEMERIS_PATH, HAS_FLATLIB  # type: ignore

api = FastAPI(title="AstroNumerology API", version="3.0.0")

# Expose app alias for uvicorn compatibility if using backend.app.main:app
app = api

# CORS config; allow origins via ALLOW_ORIGINS env var (comma-separated)
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


class NatalRequest(BaseModel):
    profile: ProfilePayload


class CompatibilityRequest(BaseModel):
    person_a: ProfilePayload
    person_b: ProfilePayload


def _profile_to_dict(p: ProfilePayload) -> Dict:
    loc = p.location.dict() if p.location else {}
    return {
        "name": p.name,
        "date_of_birth": p.date_of_birth,
        "time_of_birth": p.time_of_birth,
        "latitude": loc.get("latitude", 0.0),
        "longitude": loc.get("longitude", 0.0),
        "timezone": loc.get("timezone", "UTC"),
        "house_system": p.house_system or "Placidus",
    }


@api.post("/daily-reading")
def daily_reading(req: DailyRequest):
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="daily")


@api.post("/weekly-reading")
def weekly_reading(req: WeeklyRequest):
    profile = _profile_to_dict(req.profile)
    return build_forecast(profile, scope="weekly")


@api.post("/natal-profile")
def natal_profile(req: NatalRequest):
    profile = _profile_to_dict(req.profile)
    return build_natal_profile(profile)


@api.post("/compatibility")
def compatibility(req: CompatibilityRequest):
    a = _profile_to_dict(req.person_a)
    b = _profile_to_dict(req.person_b)
    return build_compatibility(a, b)


@api.get("/health")
def health():
    return {
        "status": "ok",
        "ephemeris_path": EPHEMERIS_PATH,
        "flatlib_available": bool(HAS_FLATLIB),
        "timestamp": datetime.utcnow().isoformat(),
    }
