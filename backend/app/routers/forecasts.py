"""
API v2 - Forecast Endpoints
Standardized request/response format for daily/weekly/monthly forecasts.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus, ForecastRequest,
    ProfilePayload
)
from ..exceptions import (
    StructuredLogger, InvalidDateError,
    InvalidCoordinatesError
)
from ..products.forecast import build_forecast

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
    date: datetime
    sections: List[ForecastSection]
    overall_score: float
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

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
                f"Invalid date format: {str(e)}",
                value=req.profile.date_of_birth
            )
        
        # Validate coordinates if provided
        if req.profile.latitude is not None or req.profile.longitude is not None:
            if req.profile.latitude is None or req.profile.longitude is None:
                raise InvalidCoordinatesError(
                    "Both latitude and longitude must be provided together"
                )
        
        logger.info(
            f"Calculating daily forecast for {req.profile.name}",
            request_id=request_id,
            profile_name=req.profile.name,
        )
        
        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "latitude": req.profile.latitude or 0.0,
            "longitude": req.profile.longitude or 0.0,
            "timezone": req.profile.timezone or "UTC",
        }
        
        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="daily",
            lang=getattr(req, 'language', 'en')
        )
        
        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(ForecastSection(
                    title=section.get("title", ""),
                    summary=section.get("summary", ""),
                    topics=section.get("topics", {}),
                    avoid=section.get("avoid", []),
                    embrace=section.get("embrace", []),
                ))
        
        response_data = ForecastData(
            profile=req.profile,
            scope="daily",
            date=req.date or datetime.now(timezone.utc).date().isoformat(),
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
            }
        )
    except InvalidCoordinatesError as e:
        logger.error(e.message, request_id=request_id, code=e.code)
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
            }
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
            }
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
                f"Invalid date format: {str(e)}",
                value=req.profile.date_of_birth
            )
        
        logger.info(
            f"Calculating weekly forecast for {req.profile.name}",
            request_id=request_id,
            profile_name=req.profile.name,
        )
        
        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "latitude": req.profile.latitude or 0.0,
            "longitude": req.profile.longitude or 0.0,
            "timezone": req.profile.timezone or "UTC",
        }
        
        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="weekly",
            lang=getattr(req, 'language', 'en')
        )
        
        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(ForecastSection(
                    title=section.get("title", ""),
                    summary=section.get("summary", ""),
                    topics=section.get("topics", {}),
                    avoid=section.get("avoid", []),
                    embrace=section.get("embrace", []),
                ))
        
        response_data = ForecastData(
            profile=req.profile,
            scope="weekly",
            date=req.date or datetime.now(timezone.utc).date().isoformat(),
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
            }
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
                f"Invalid date format: {str(e)}",
                value=req.profile.date_of_birth
            )
        
        logger.info(
            f"Calculating monthly forecast for {req.profile.name}",
            request_id=request_id,
            profile_name=req.profile.name,
        )
        
        # Build forecast profile data
        profile_data = {
            "name": req.profile.name,
            "date_of_birth": req.profile.date_of_birth,
            "time_of_birth": req.profile.time_of_birth or "12:00:00",
            "latitude": req.profile.latitude or 0.0,
            "longitude": req.profile.longitude or 0.0,
            "timezone": req.profile.timezone or "UTC",
        }
        
        # Calculate forecast
        forecast = build_forecast(
            profile_data,
            scope="monthly",
            lang=getattr(req, 'language', 'en')
        )
        
        # Parse sections
        sections = []
        if isinstance(forecast.get("sections"), list):
            for section in forecast["sections"]:
                sections.append(ForecastSection(
                    title=section.get("title", ""),
                    summary=section.get("summary", ""),
                    topics=section.get("topics", {}),
                    avoid=section.get("avoid", []),
                    embrace=section.get("embrace", []),
                ))
        
        response_data = ForecastData(
            profile=req.profile,
            scope="monthly",
            date=req.date or datetime.now(timezone.utc).date().isoformat(),
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
            }
        )
