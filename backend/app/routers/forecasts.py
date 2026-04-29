"""
API v2 - Forecast Endpoints
Standardized request/response format for daily/weekly/monthly forecasts.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..exceptions import InvalidCoordinatesError, InvalidDateError, StructuredLogger
from ..products.forecast import build_forecast
from ..schemas import ApiResponse, ForecastRequest, ProfilePayload, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/forecasts", tags=["Forecasts"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class ForecastSection(BaseModel):
    """A forecast section with topic scores and interpretation."""

    title: str
    summary: str
    topics: Dict[str, float]
    avoid: List[str] = []
    embrace: List[str] = []


class ForecastData(BaseModel):
    """Daily/weekly/monthly forecast response."""

    profile: ProfilePayload
    scope: str
    date: str  # YYYY-MM-DD
    sections: List[ForecastSection]
    overall_score: float
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================


def _validate_target_date(date_str: Optional[str]) -> None:
    if not date_str:
        return
    try:
        # Strictly require YYYY-MM-DD
        datetime.strptime(date_str, "%Y-%m-%d")
    except Exception as e:
        raise InvalidDateError(
            f"Invalid forecast date (expected YYYY-MM-DD): {str(e)}",
            value=date_str,
        )


def _require_location(profile: ProfilePayload) -> None:
    missing: list[str] = []
    if profile.latitude is None:
        missing.append("latitude")
    if profile.longitude is None:
        missing.append("longitude")
    if not profile.timezone:
        missing.append("timezone")
    if missing:
        raise InvalidCoordinatesError(
            "Forecasts require latitude, longitude, and timezone for accurate calculations "
            f"(missing: {', '.join(missing)})"
        )

    # Validate timezone as an IANA identifier (or UTC/GMT).
    tz = (profile.timezone or "").strip()
    if tz not in ("UTC", "GMT"):
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(tz)
        except Exception:
            raise InvalidCoordinatesError(
                f"Invalid timezone '{profile.timezone}'. Use a valid IANA timezone (e.g., 'America/New_York')."
            )


def _require_birth_time(profile: ProfilePayload) -> None:
    if not profile.time_of_birth:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "MISSING_TIME_OF_BIRTH",
                "message": "Birth time is required for high-precision forecasts (HH:MM or HH:MM:SS).",
                "field": "time_of_birth",
            },
        )


@router.post("/daily", response_model=ApiResponse[ForecastData])
async def calculate_daily_forecast(
    request: Request,
    req: ForecastRequest,
) -> ApiResponse[ForecastData]:
    """
    Calculate daily forecast with standardized response format.

    ## Parameters
    - **profile**: User birth data (name, DOB, time, location)
    - **target_date**: Date for forecast (default: today)
    - **language**: Language code (en, es, fr, de)

    ## Response
    Returns standardized API response with daily forecast sections and guidance.

    ## Errors
    - `INVALID_DATE`: Invalid date format or values
    - `INVALID_COORDINATES`: Invalid latitude/longitude
    """
    request_id = request.state.request_id

    try:
        # Validate date format
        try:
            datetime.fromisoformat(req.profile.date_of_birth)
        except ValueError as e:
            raise InvalidDateError(
                f"Invalid date format: {str(e)}", value=req.profile.date_of_birth
            )

        _validate_target_date(req.date)
        _require_birth_time(req.profile)
        _require_location(req.profile)

        logger.info(
            "Calculating daily forecast",
            request_id=request_id,
            tone=req.tone,
        )

        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "place_of_birth": getattr(req.profile, "place_of_birth", None),
            "latitude": req.profile.latitude,
            "longitude": req.profile.longitude,
            "timezone": req.profile.timezone,
            "house_system": getattr(req.profile, "house_system", None),
        }

        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="daily",
            lang=getattr(req, "language", "en"),
            target_date=req.date,
            tone=req.tone,
        )

        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(
                    ForecastSection(
                        title=section.get("title", ""),
                        summary=section.get("summary", ""),
                        topics=section.get("topics", {}),
                        avoid=section.get("avoid", []),
                        embrace=section.get("embrace", []),
                    )
                )

        response_data = ForecastData(
            profile=req.profile,
            scope="daily",
            date=forecast.get("date")
            or (req.date or datetime.now(timezone.utc).date().isoformat()),
            sections=sections,
            overall_score=forecast.get("overall_score", 0.5),
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Daily forecast calculated successfully",
            request_id=request_id,
        )
    except InvalidDateError as e:
        logger.error(e.message, request_id=request_id, code=e.code, value=e.value)
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "field": "date_of_birth",
                "value": e.value,
            },
        )
    except InvalidCoordinatesError as e:
        logger.error(e.message, request_id=request_id, code=e.code)
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
            },
        )
    except Exception as e:
        logger.error(
            f"Forecast calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FORECAST_ERROR",
                "message": "Failed to calculate forecast",
            },
        )


@router.post("/weekly", response_model=ApiResponse[ForecastData])
async def calculate_weekly_forecast(
    request: Request,
    req: ForecastRequest,
) -> ApiResponse[ForecastData]:
    """Calculate weekly forecast with standardized response format."""
    request_id = request.state.request_id

    try:
        # Validate date format
        try:
            datetime.fromisoformat(req.profile.date_of_birth)
        except ValueError as e:
            raise InvalidDateError(
                f"Invalid date format: {str(e)}", value=req.profile.date_of_birth
            )

        _validate_target_date(req.date)
        _require_birth_time(req.profile)
        _require_location(req.profile)

        logger.info(
            "Calculating weekly forecast",
            request_id=request_id,
            tone=req.tone,
        )

        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "place_of_birth": getattr(req.profile, "place_of_birth", None),
            "latitude": req.profile.latitude,
            "longitude": req.profile.longitude,
            "timezone": req.profile.timezone,
            "house_system": getattr(req.profile, "house_system", None),
        }

        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="weekly",
            lang=getattr(req, "language", "en"),
            target_date=req.date,
            tone=req.tone,
        )

        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(
                    ForecastSection(
                        title=section.get("title", ""),
                        summary=section.get("summary", ""),
                        topics=section.get("topics", {}),
                        avoid=section.get("avoid", []),
                        embrace=section.get("embrace", []),
                    )
                )

        response_data = ForecastData(
            profile=req.profile,
            scope="weekly",
            date=forecast.get("date")
            or (req.date or datetime.now(timezone.utc).date().isoformat()),
            sections=sections,
            overall_score=forecast.get("overall_score", 0.5),
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Weekly forecast calculated successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Forecast calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FORECAST_ERROR",
                "message": "Failed to calculate forecast",
            },
        )


@router.post("/monthly", response_model=ApiResponse[ForecastData])
async def calculate_monthly_forecast(
    request: Request,
    req: ForecastRequest,
) -> ApiResponse[ForecastData]:
    """Calculate monthly forecast with standardized response format."""
    request_id = request.state.request_id

    try:
        # Validate date format
        try:
            datetime.fromisoformat(req.profile.date_of_birth)
        except ValueError as e:
            raise InvalidDateError(
                f"Invalid date format: {str(e)}", value=req.profile.date_of_birth
            )

        _validate_target_date(req.date)
        _require_birth_time(req.profile)
        _require_location(req.profile)

        logger.info(
            "Calculating monthly forecast",
            request_id=request_id,
            tone=req.tone,
        )

        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "place_of_birth": getattr(req.profile, "place_of_birth", None),
            "latitude": req.profile.latitude,
            "longitude": req.profile.longitude,
            "timezone": req.profile.timezone,
            "house_system": getattr(req.profile, "house_system", None),
        }

        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="monthly",
            lang=getattr(req, "language", "en"),
            target_date=req.date,
            tone=req.tone,
        )

        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(
                    ForecastSection(
                        title=section.get("title", ""),
                        summary=section.get("summary", ""),
                        topics=section.get("topics", {}),
                        avoid=section.get("avoid", []),
                        embrace=section.get("embrace", []),
                    )
                )

        response_data = ForecastData(
            profile=req.profile,
            scope="monthly",
            date=forecast.get("date")
            or (req.date or datetime.now(timezone.utc).date().isoformat()),
            sections=sections,
            overall_score=forecast.get("overall_score", 0.5),
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Monthly forecast calculated successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Forecast calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FORECAST_ERROR",
                "message": "Failed to calculate forecast",
            },
        )
