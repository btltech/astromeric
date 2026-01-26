"""
API v2 - Year Ahead Endpoints
Comprehensive year-ahead forecasts.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from ..chart_service import build_natal_chart
from ..engine.year_ahead import build_year_ahead_forecast
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

router = APIRouter(prefix="/v2/year-ahead", tags=["Year Ahead"])


def _profile_to_dict(payload: ProfilePayload) -> Dict:
    """Convert ProfilePayload to dict."""
    return {
        "name": payload.name,
        "date_of_birth": payload.date_of_birth,
        "time_of_birth": payload.time_of_birth or "12:00",
        "latitude": payload.latitude or 0.0,
        "longitude": payload.longitude or 0.0,
        "timezone": payload.timezone or "UTC",
    }


class YearAheadRequest(BaseModel):
    """Request for year-ahead forecast."""
    profile: ProfilePayload
    year: Optional[int] = Field(None, description="Year for forecast (defaults to current year)")


@router.post("/forecast", response_model=ApiResponse[Dict[str, Any]])
async def year_ahead_forecast(
    request: Request,
    req: YearAheadRequest,
):
    """
    Get comprehensive year-ahead forecast.
    
    ## Includes
    - Personal Year number and themes
    - Solar Return date
    - Monthly breakdowns
    - Eclipse impacts
    - Major planetary ingresses
    
    ## Parameters
    - **profile**: Birth data
    - **year**: Target year (optional, defaults to current)
    """
    profile = _profile_to_dict(req.profile)
    natal = build_natal_chart(profile)
    year = req.year or datetime.now().year

    forecast = build_year_ahead_forecast(profile, natal, year)
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=forecast
    )
