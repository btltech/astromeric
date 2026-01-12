"""
API v2 - Numerology Endpoint
Standardized request/response format for numerology analysis.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus, NumerologyRequest,
    ProfilePayload
)
from ..exceptions import (
    StructuredLogger, InvalidDateError
)
from ..numerology_engine import build_numerology

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/numerology", tags=["Numerology"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================

class LifePathNumber(BaseModel):
    """Life path number analysis."""
    number: int
    meaning: str
    traits: List[str]
    life_purpose: str


class PersonalYearCycle(BaseModel):
    """Personal year number and meaning."""
    year: int
    cycle_number: int
    interpretation: str
    focus_areas: List[str]


class NumerologyData(BaseModel):
    """Full numerology analysis response."""
    profile: ProfilePayload
    life_path: LifePathNumber
    destiny_number: int
    destiny_interpretation: str
    personal_year: PersonalYearCycle
    compatibility_number: Optional[int] = None
    compatibility_interpretation: Optional[str] = None
    lucky_numbers: List[int]
    auspicious_days: List[int]
    numerology_insights: Dict[str, str]
    generated_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/profile", response_model=ApiResponse[NumerologyData])
async def calculate_numerology_profile(
    request: Request,
    req: NumerologyRequest,
) -> ApiResponse[NumerologyData]:
    """
    Calculate numerology profile for a person.
    
    ## Parameters
    - **profile**: User birth data (name, DOB)
    - **language**: Language code (en, es, fr, de)
    
    ## Response
    Returns standardized API response with numerology analysis including life path,
    destiny number, personal year cycle, and auspicious numbers.
    
    ## Errors
    - `INVALID_DATE`: Invalid date format or values
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
        
        logger.info(
            f"Calculating numerology profile for {req.profile.name}",
            request_id=request_id,
            profile_name=req.profile.name,
        )
        
        # Calculate numerology
        numerology = build_numerology(
            req.profile.name,
            req.profile.date_of_birth,
            datetime.now(timezone.utc),
            lang=getattr(req, 'language', 'en')
        )
        
        # Extract life path number
        life_path_num = numerology.get("life_path_number", 1)
        life_path_data = LifePathNumber(
            number=life_path_num,
            meaning=numerology.get("life_path_meaning", ""),
            traits=numerology.get("life_path_traits", []),
            life_purpose=numerology.get("life_purpose", ""),
        )
        
        # Extract personal year
        personal_year_num = numerology.get("personal_year_number", 1)
        personal_year_data = PersonalYearCycle(
            year=datetime.now(timezone.utc).year,
            cycle_number=personal_year_num,
            interpretation=numerology.get("personal_year_interpretation", ""),
            focus_areas=numerology.get("personal_year_focus", []),
        )
        
        response_data = NumerologyData(
            profile=req.profile,
            life_path=life_path_data,
            destiny_number=numerology.get("destiny_number", 1),
            destiny_interpretation=numerology.get("destiny_interpretation", ""),
            personal_year=personal_year_data,
            compatibility_number=numerology.get("compatibility_number", None),
            compatibility_interpretation=numerology.get("compatibility_interpretation", None),
            lucky_numbers=numerology.get("lucky_numbers", []),
            auspicious_days=numerology.get("auspicious_days", []),
            numerology_insights=numerology.get("insights", {}),
            generated_at=datetime.now(timezone.utc),
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Numerology profile calculated successfully",
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
    except Exception as e:
        logger.error(
            f"Numerology calculation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "NUMEROLOGY_ERROR",
                "message": "Failed to calculate numerology profile",
            }
        )


@router.post("/compatibility", response_model=ApiResponse[Dict[str, Any]])
async def calculate_numerology_compatibility(
    request: Request,
    req: NumerologyRequest,
) -> ApiResponse[Dict[str, Any]]:
    """
    Calculate numerology compatibility between two people.
    
    ## Parameters
    - **person_a**: First person's birth data
    - **person_b**: Second person's birth data
    - **language**: Language code
    
    ## Response
    Returns numerology-based compatibility score and interpretation.
    """
    request_id = request.state.request_id
    
    try:
        # Validate both people have date of birth
        if not hasattr(req, 'person_b') or req.person_b is None:
            raise ValueError("Person B required for compatibility calculation")
        
        for i, profile in enumerate([req.profile, req.person_b], 1):
            try:
                datetime.fromisoformat(profile.date_of_birth)
            except ValueError as e:
                raise InvalidDateError(
                    f"Person {i}: Invalid date format: {str(e)}",
                    value=profile.date_of_birth
                )
        
        logger.info(
            f"Calculating numerology compatibility",
            request_id=request_id,
            person_a=req.profile.name,
            person_b=req.person_b.name if hasattr(req, 'person_b') else "",
        )
        
        # Calculate numerology for both
        numerology_a = build_numerology(
            req.profile.name,
            req.profile.date_of_birth,
            datetime.now(timezone.utc),
        )
        
        numerology_b = build_numerology(
            req.person_b.name,
            req.person_b.date_of_birth,
            datetime.now(timezone.utc),
        )
        
        # Calculate compatibility score
        life_path_a = numerology_a.get("life_path_number", 1)
        life_path_b = numerology_b.get("life_path_number", 1)
        
        # Simple compatibility algorithm: numbers that match or complement are more compatible
        compatibility_score = min(
            1.0,
            max(0.0, 1.0 - (abs(life_path_a - life_path_b) / 10.0))
        )
        
        response_data = {
            "person_a": {
                "name": req.profile.name,
                "life_path": life_path_a,
            },
            "person_b": {
                "name": req.person_b.name,
                "life_path": life_path_b,
            },
            "compatibility_score": compatibility_score,
            "interpretation": f"Life path {life_path_a} and {life_path_b} have moderate compatibility",
            "strengths": numerology_a.get("compatibility_strengths", []),
            "challenges": numerology_a.get("compatibility_challenges", []),
        }
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Numerology compatibility calculated successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Numerology compatibility error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "NUMEROLOGY_ERROR",
                "message": "Failed to calculate numerology compatibility",
            }
        )
