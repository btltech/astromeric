"""
API v2 - Compatibility Endpoint
Standardized request/response format for relationship compatibility analysis.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus, CompatibilityRequest,
    ProfilePayload
)
from ..exceptions import (
    StructuredLogger, InvalidDateError,
    InvalidCoordinatesError
)
from ..products.compatibility import build_compatibility

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/compatibility", tags=["Compatibility"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================

class CompatibilityScore(BaseModel):
    """Individual compatibility dimension score."""
    name: str
    score: float
    interpretation: str


class CompatibilityData(BaseModel):
    """Full compatibility analysis response."""
    person_a: ProfilePayload
    person_b: ProfilePayload
    overall_score: float
    summary: str
    dimensions: List[CompatibilityScore]
    strengths: List[str]
    challenges: List[str]
    recommendations: List[str]
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/romantic", response_model=ApiResponse[CompatibilityData])
async def calculate_romantic_compatibility(
    request: Request,
    req: CompatibilityRequest,
) -> ApiResponse[CompatibilityData]:
    """
    Calculate romantic compatibility between two people.
    
    ## Parameters
    - **person_a**: First person's birth data (name, DOB, time, location)
    - **person_b**: Second person's birth data (name, DOB, time, location)
    - **language**: Language code (en, es, fr, de)
    
    ## Response
    Returns standardized API response with compatibility analysis and guidance.
    
    ## Errors
    - `INVALID_DATE`: Invalid date format or values
    - `INVALID_COORDINATES`: Invalid latitude/longitude
    """
    request_id = request.state.request_id
    
    try:
        # Validate both profiles
        for i, profile in enumerate([req.person_a, req.person_b], 1):
            try:
                datetime.fromisoformat(profile.date_of_birth)
            except ValueError as e:
                raise InvalidDateError(
                    f"Person {i}: Invalid date format: {str(e)}",
                    value=profile.date_of_birth
                )
            
            if profile.latitude is not None or profile.longitude is not None:
                if profile.latitude is None or profile.longitude is None:
                    raise InvalidCoordinatesError(
                        f"Person {i}: Both latitude and longitude must be provided together"
                    )
        
        logger.info(
            f"Calculating compatibility between {req.person_a.name} and {req.person_b.name}",
            request_id=request_id,
            person_a=req.person_a.name,
            person_b=req.person_b.name,
        )
        
        # Build profile data for both people
        profile_a = {
            "name": req.person_a.name,
            "date_of_birth": req.person_a.date_of_birth,
            "time_of_birth": req.person_a.time_of_birth or "12:00:00",
            "latitude": req.person_a.latitude or 0.0,
            "longitude": req.person_a.longitude or 0.0,
            "timezone": req.person_a.timezone or "UTC",
        }
        
        profile_b = {
            "name": req.person_b.name,
            "date_of_birth": req.person_b.date_of_birth,
            "time_of_birth": req.person_b.time_of_birth or "12:00:00",
            "latitude": req.person_b.latitude or 0.0,
            "longitude": req.person_b.longitude or 0.0,
            "timezone": req.person_b.timezone or "UTC",
        }
        
        # Calculate compatibility
        compatibility = build_compatibility(
            profile_a,
            profile_b,
            lang=getattr(req, 'language', 'en')
        )
        
        # Parse dimensions
        dimensions = []
        if isinstance(compatibility.get("dimensions"), list):
            for dimension in compatibility["dimensions"]:
                dimensions.append(CompatibilityScore(
                    name=dimension.get("name", ""),
                    score=dimension.get("score", 0.5),
                    interpretation=dimension.get("interpretation", ""),
                ))
        
        response_data = CompatibilityData(
            person_a=req.person_a,
            person_b=req.person_b,
            overall_score=compatibility.get("overall_score", 0.5),
            summary=compatibility.get("summary", ""),
            dimensions=dimensions,
            strengths=compatibility.get("strengths", []),
            challenges=compatibility.get("challenges", []),
            recommendations=compatibility.get("recommendations", []),
            generated_at=datetime.now(timezone.utc),
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Compatibility analysis calculated successfully",
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
            f"Compatibility calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "COMPATIBILITY_ERROR",
                "message": "Failed to calculate compatibility",
            }
        )


@router.post("/friendship", response_model=ApiResponse[CompatibilityData])
async def calculate_friendship_compatibility(
    request: Request,
    req: CompatibilityRequest,
) -> ApiResponse[CompatibilityData]:
    """Calculate friendship compatibility between two people."""
    request_id = request.state.request_id
    
    try:
        # Validate both profiles
        for i, profile in enumerate([req.person_a, req.person_b], 1):
            try:
                datetime.fromisoformat(profile.date_of_birth)
            except ValueError as e:
                raise InvalidDateError(
                    f"Person {i}: Invalid date format: {str(e)}",
                    value=profile.date_of_birth
                )
        
        logger.info(
            f"Calculating friendship compatibility between {req.person_a.name} and {req.person_b.name}",
            request_id=request_id,
            person_a=req.person_a.name,
            person_b=req.person_b.name,
        )
        
        # Build profile data
        profile_a = {
            "name": req.person_a.name,
            "date_of_birth": req.person_a.date_of_birth,
            "time_of_birth": req.person_a.time_of_birth or "12:00:00",
            "latitude": req.person_a.latitude or 0.0,
            "longitude": req.person_a.longitude or 0.0,
            "timezone": req.person_a.timezone or "UTC",
        }
        
        profile_b = {
            "name": req.person_b.name,
            "date_of_birth": req.person_b.date_of_birth,
            "time_of_birth": req.person_b.time_of_birth or "12:00:00",
            "latitude": req.person_b.latitude or 0.0,
            "longitude": req.person_b.longitude or 0.0,
            "timezone": req.person_b.timezone or "UTC",
        }
        
        # Calculate compatibility (reuse romantic analysis, can be customized)
        compatibility = build_compatibility(
            profile_a,
            profile_b,
            lang=getattr(req, 'language', 'en')
        )
        
        # Parse dimensions
        dimensions = []
        if isinstance(compatibility.get("dimensions"), list):
            for dimension in compatibility["dimensions"]:
                dimensions.append(CompatibilityScore(
                    name=dimension.get("name", ""),
                    score=dimension.get("score", 0.5),
                    interpretation=dimension.get("interpretation", ""),
                ))
        
        response_data = CompatibilityData(
            person_a=req.person_a,
            person_b=req.person_b,
            overall_score=compatibility.get("overall_score", 0.5),
            summary=compatibility.get("summary", ""),
            dimensions=dimensions,
            strengths=compatibility.get("strengths", []),
            challenges=compatibility.get("challenges", []),
            recommendations=compatibility.get("recommendations", []),
            generated_at=datetime.now(timezone.utc),
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Friendship compatibility calculated successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Compatibility calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "COMPATIBILITY_ERROR",
                "message": "Failed to calculate compatibility",
            }
        )
