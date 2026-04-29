"""
API v2 - Natal Profile Endpoint
Standardized request/response format with proper validation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..exceptions import (
    AstroError,
    InvalidCoordinatesError,
    InvalidDateError,
    StructuredLogger,
)
from ..models import SessionLocal, User
from ..products import build_natal_profile
from ..schemas import ApiResponse, NatalProfileRequest, ProfilePayload, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/profiles", tags=["Profiles"])


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class NatalChartData(BaseModel):
    """Natal chart calculation results."""

    # Raw chart dict from `chart_service.build_natal_chart`.
    metadata: Dict[str, Any]
    planets: List[Dict[str, Any]]
    houses: List[Dict[str, Any]]
    aspects: List[Dict[str, Any]]
    ascendant: Optional[Dict[str, Any]] = None
    midheaven: Optional[Dict[str, Any]] = None


class NatalProfileResponse(BaseModel):
    """Full natal profile response."""

    profile: ProfilePayload
    chart: NatalChartData
    numerology: Dict[str, Any]
    sections: List[Dict[str, Any]]
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================


def _profile_payload_to_dict(profile: ProfilePayload) -> Dict[str, Any]:
    if hasattr(profile, "model_dump"):
        data = profile.model_dump(exclude_none=True)
    else:
        data = profile.dict(exclude_none=True)  # type: ignore[attr-defined]

    return data


def _require_natal_inputs(profile: ProfilePayload) -> None:
    """Validate coordinates consistency only — missing time/location is allowed
    (the chart_service will use graceful fallbacks and set data_quality accordingly)."""
    # Only reject if one of lat/lon is provided but not the other
    if (profile.latitude is None) != (profile.longitude is None):
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "MISSING_PROFILE_FIELDS",
                    "message": "Both latitude and longitude must be provided together.",
                    "missing": [
                        "latitude" if profile.latitude is None else "longitude"
                    ],
                }
            },
        )

    tz = (profile.timezone or "").strip()
    if tz and tz not in ("UTC", "GMT"):
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(tz)
        except Exception:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "INVALID_TIMEZONE",
                        "message": f"Invalid timezone '{profile.timezone}'. Use a valid IANA timezone (e.g., 'America/New_York').",
                        "field": "timezone",
                    }
                },
            )


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
                f"Invalid date format: {str(e)}", value=req.profile.date_of_birth
            )

        # Validate coordinates if provided
        if req.profile.latitude is not None or req.profile.longitude is not None:
            if req.profile.latitude is None or req.profile.longitude is None:
                raise InvalidCoordinatesError(
                    "Both latitude and longitude must be provided together"
                )

        _require_natal_inputs(req.profile)

        # Calculate natal profile
        logger.info(
            "Calculating natal profile",
            request_id=request_id,
        )

        natal_data = build_natal_profile(_profile_payload_to_dict(req.profile))
        birth_time_assumed = natal_data.get("metadata", {}).get(
            "birth_time_assumed", False
        )
        data_quality = natal_data.get("metadata", {}).get("data_quality", "unknown")

        logger.info(
            "Natal profile calculated successfully",
            request_id=request_id,
            provider=natal_data.get("chart", {}).get("metadata", {}).get("provider"),
            birth_time_assumed=birth_time_assumed,
            data_quality=data_quality,
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=NatalProfileResponse(
                profile=req.profile,
                chart=NatalChartData(**(natal_data.get("chart") or {})),
                numerology=natal_data.get("numerology") or {},
                sections=natal_data.get("sections") or [],
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


@router.get("/natal/{profile_id}", response_model=ApiResponse[NatalProfileResponse])
async def get_natal_profile(
    request: Request,
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[NatalProfileResponse]:
    """
    Retrieve a previously calculated natal profile.

    ## Parameters
    - **profile_id**: The ID of the saved profile

    ## Response
    Returns the natal chart data and interpretation for the profile.

    ## Errors
    - `PROFILE_NOT_FOUND`: Profile doesn't exist or user doesn't own it
    - `UNAUTHORIZED`: User is not authenticated
    """
    request_id = request.state.request_id

    try:
        from ..models import Profile as DBProfile

        logger.info(
            f"Retrieving natal profile {profile_id}",
            request_id=request_id,
            profile_id=profile_id,
            user_id=current_user.id,
        )

        # Get profile from database
        db_profile = (
            db.query(DBProfile)
            .filter(
                DBProfile.id == profile_id,
                DBProfile.user_id == current_user.id,  # Ensure user owns this profile
            )
            .first()
        )

        if not db_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Profile not found or you don't have access to it",
                    "field": "profile_id",
                },
            )

        # Convert DB profile to ProfilePayload
        profile_payload = ProfilePayload(
            name=db_profile.name,
            date_of_birth=db_profile.date_of_birth,
            time_of_birth=db_profile.time_of_birth,
            place_of_birth=db_profile.place_of_birth,
            latitude=db_profile.latitude,
            longitude=db_profile.longitude,
            timezone=db_profile.timezone,
            house_system=db_profile.house_system,
        )

        _require_natal_inputs(profile_payload)

        # Calculate natal chart (same as POST /natal)
        natal_data = build_natal_profile(_profile_payload_to_dict(profile_payload))

        logger.info(
            f"Natal profile {profile_id} retrieved successfully",
            request_id=request_id,
            provider=natal_data.get("chart", {}).get("metadata", {}).get("provider"),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=NatalProfileResponse(
                profile=profile_payload,
                chart=NatalChartData(**(natal_data.get("chart") or {})),
                numerology=natal_data.get("numerology") or {},
                sections=natal_data.get("sections") or [],
                generated_at=datetime.now(timezone.utc),
            ),
            message="Natal profile retrieved successfully",
            request_id=request_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving natal profile",
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
