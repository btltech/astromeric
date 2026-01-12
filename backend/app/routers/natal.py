"""
API v2 - Natal Profile Endpoint
Standardized request/response format with proper validation.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus, NatalProfileRequest,
    ProfilePayload
)
from ..exceptions import (
    StructuredLogger, AstroError, InvalidDateError,
    InvalidCoordinatesError, EphemerisError
)
from ..products import build_natal_profile

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/profiles", tags=["Profiles"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================

class NatalChartData(BaseModel):
    """Natal chart calculation results."""
    sun_sign: str
    moon_sign: str
    rising_sign: str
    houses: Dict[str, Any]
    aspects: List[Dict[str, Any]]
    asteroids: Optional[List[Dict[str, Any]]] = None


class NatalProfileResponse(BaseModel):
    """Full natal profile response."""
    profile: ProfilePayload
    chart: NatalChartData
    interpretation: Dict[str, str]
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/natal", response_model=ApiResponse[NatalProfileResponse])
async def calculate_natal_profile(
    request: Request,
    req: NatalProfileRequest,
) -> ApiResponse[NatalProfileResponse]:
    """
    Calculate natal profile with standardized response format.
    
    ## Parameters
    - **profile**: User birth data (name, DOB, time, location)
    - **include_asteroids**: Include Chiron and other minor planets
    - **include_aspects**: Include planetary aspects
    - **orb**: Orb in degrees for aspect calculations (1-20)
    
    ## Response
    Returns standardized API response with natal chart data and interpretation.
    
    ## Errors
    - `INVALID_DATE`: Invalid date format or values
    - `INVALID_COORDINATES`: Invalid latitude/longitude
    - `EPHEMERIS_ERROR`: Ephemeris calculation failed
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
        
        # Calculate natal profile
        logger.info(
            f"Calculating natal profile for {req.profile.name}",
            request_id=request_id,
            profile_name=req.profile.name,
        )
        
        natal_data = build_natal_profile(req.profile)
        
        logger.info(
            f"Natal profile calculated successfully",
            request_id=request_id,
            sun_sign=natal_data.get("sun_sign"),
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=NatalProfileResponse(
                profile=req.profile,
                chart=natal_data.get("chart"),
                interpretation=natal_data.get("interpretation"),
                generated_at=datetime.now(timezone.utc),
            ),
            message="Natal profile calculated successfully",
            request_id=request_id,
        )
        
    except AstroError as e:
        logger.error(
            e.message,
            request_id=request_id,
            code=e.code,
        )
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "field": e.field,
                }
            },
        )
    except Exception as e:
        logger.error(
            "Unexpected error calculating natal profile",
            request_id=request_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )


@router.get("/natal/{profile_id}")
async def get_natal_profile(
    request: Request,
    profile_id: int,
):
    """
    Retrieve previously calculated natal profile.
    Requires user authentication.
    """
    request_id = request.state.request_id
    
    # TODO: Implement database lookup when profiles are saved
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile retrieval not yet implemented",
    )
