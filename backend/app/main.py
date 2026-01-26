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

from fastapi import FastAPI, Request, status
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
    """Register all API routers."""

    # V2 Routers (standardized API)
    try:
        from .routers import (
            ai,
            auth,
            charts,
            compatibility,
            cosmic_guide,
            daily_features,
            feedback,
            forecasts,
            habits,
            journal,
            learning,
            moon,
            natal,
            numerology,
            profiles,
            relationships,
            system,
            timing,
            transits,
            year_ahead,
        )

        # Core v2 routers
        api.include_router(auth.router)
        api.include_router(profiles.router)
        api.include_router(natal.router)
        api.include_router(forecasts.router)
        api.include_router(compatibility.router)
        api.include_router(numerology.router)
        api.include_router(charts.router)

        # Feature routers
        api.include_router(daily_features.router)
        api.include_router(moon.router)
        api.include_router(timing.router)
        api.include_router(relationships.router)
        api.include_router(journal.router)
        api.include_router(habits.router)
        api.include_router(year_ahead.router)
        api.include_router(transits.router)

        # AI and learning
        api.include_router(ai.router)
        api.include_router(cosmic_guide.router)
        api.include_router(learning.router)

        # Utility routers
        api.include_router(feedback.router)
        api.include_router(system.router)

        logger.info("Successfully registered v2 routers (20 modules)")

    except ImportError as e:
        logger.warning(f"Could not import some v2 routers: {str(e)}")

    # V2 Additional routers (sky, alerts)
    try:
        from .routers import alerts as v2_alerts
        from .routers import sky as v2_sky

        api.include_router(v2_sky.router)
        api.include_router(v2_alerts.router)

        logger.info("Registered v2 sky and alerts routers")
    except ImportError as e:
        logger.warning(f"Could not import sky/alerts routers: {str(e)}")

    # V1 Routers (backward compatibility - will be deprecated)
    try:
        from .routers import (
            v1_ai,
            v1_auth,
            v1_habits,
            v1_journal,
            v1_learning,
            v1_moon,
            v1_numerology,
            v1_profiles,
            v1_readings,
            v1_relationships,
            v1_timing,
        )

        api.include_router(v1_auth.router)
        api.include_router(v1_profiles.router)
        api.include_router(v1_readings.router)
        api.include_router(v1_learning.router)
        api.include_router(v1_moon.router)
        api.include_router(v1_timing.router)
        api.include_router(v1_journal.router)
        api.include_router(v1_relationships.router)
        api.include_router(v1_habits.router)
        api.include_router(v1_numerology.router)
        api.include_router(v1_ai.router)

        logger.info("Registered v1 legacy routers (11 modules) - will be deprecated")

    except ImportError as e:
        logger.warning(f"Could not import some v1 routers: {str(e)}")


# Register all routers
register_routers()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(api, host="0.0.0.0", port=port)
