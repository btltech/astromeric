"""
API v2 - Numerology Endpoint
Standardized request/response format for numerology analysis.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..exceptions import InvalidDateError, StructuredLogger
from ..numerology_engine import build_numerology
from ..schemas import (
    ApiResponse,
    NumerologyCompatibilityRequest,
    NumerologyRequest,
    ProfilePayload,
    ResponseStatus,
)

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
# HELPER FUNCTIONS
# ============================================================================


# Life path traits by number
LIFE_PATH_TRAITS = {
    1: ["Independent", "Ambitious", "Innovative", "Leadership"],
    2: ["Diplomatic", "Cooperative", "Sensitive", "Harmonious"],
    3: ["Creative", "Expressive", "Social", "Optimistic"],
    4: ["Practical", "Organized", "Dedicated", "Reliable"],
    5: ["Adventurous", "Versatile", "Freedom-loving", "Dynamic"],
    6: ["Nurturing", "Responsible", "Caring", "Family-oriented"],
    7: ["Analytical", "Intuitive", "Spiritual", "Introspective"],
    8: ["Ambitious", "Authoritative", "Successful", "Material-focused"],
    9: ["Humanitarian", "Compassionate", "Wise", "Selfless"],
    11: ["Visionary", "Intuitive", "Inspiring", "Spiritual leader"],
    22: ["Master builder", "Practical visionary", "Powerful", "Achiever"],
    33: ["Master teacher", "Compassionate healer", "Selfless", "Uplifting"],
}

LIFE_PATH_PURPOSE = {
    1: "To develop individuality and lead through innovation",
    2: "To create harmony and support others through cooperation",
    3: "To express creativity and bring joy to the world",
    4: "To build lasting foundations and manifest practical solutions",
    5: "To embrace change and inspire freedom in others",
    6: "To nurture, heal, and create loving environments",
    7: "To seek truth and share spiritual wisdom",
    8: "To achieve material success and empower others",
    9: "To serve humanity and complete karmic cycles",
    11: "To inspire spiritual awakening and illuminate truth",
    22: "To manifest dreams into reality on a grand scale",
    33: "To heal and teach through unconditional love",
}

PERSONAL_YEAR_FOCUS = {
    1: ["New beginnings", "Self-development", "Taking initiative"],
    2: ["Relationships", "Patience", "Cooperation"],
    3: ["Creativity", "Self-expression", "Social connections"],
    4: ["Building foundations", "Hard work", "Organization"],
    5: ["Change", "Freedom", "Adventure"],
    6: ["Home", "Family", "Responsibility"],
    7: ["Reflection", "Spirituality", "Inner growth"],
    8: ["Career", "Finances", "Achievement"],
    9: ["Completion", "Letting go", "Humanitarian work"],
}


def _generate_life_path_traits(number: int) -> List[str]:
    """Generate traits for a life path number."""
    return LIFE_PATH_TRAITS.get(number, LIFE_PATH_TRAITS.get(number % 9 or 9, ["Unique", "Balanced"]))


def _generate_life_purpose(number: int) -> str:
    """Generate life purpose for a life path number."""
    return LIFE_PATH_PURPOSE.get(number, LIFE_PATH_PURPOSE.get(number % 9 or 9, "To find your unique path"))


def _generate_focus_areas(number: int) -> List[str]:
    """Generate focus areas for a personal year."""
    return PERSONAL_YEAR_FOCUS.get(number, PERSONAL_YEAR_FOCUS.get(number % 9 or 9, ["Growth", "Balance"]))


def _generate_lucky_numbers(life_path: int, destiny: int, personal_year: int, personal_month: int) -> List[int]:
    """Generate lucky numbers based on core numerology numbers.
    Includes personal_month so numbers update every calendar month.
    """
    base_nums = {life_path, destiny, personal_year, personal_month}
    lucky = list(base_nums)
    for n in list(base_nums):
        complement = 9 - (n % 9) if n % 9 != 0 else 9
        if complement not in lucky and complement > 0:
            lucky.append(complement)
    # Add a monthly-shifted derived number so the set visibly changes each month
    lucky.append((life_path + destiny + personal_month) % 9 or 9)
    return sorted(set(lucky))[:6]


def _generate_auspicious_days(life_path: int, month: int, year: int) -> List[int]:
    """Generate auspicious days of the month based on life path.
    Includes current month and year so the dates change each calendar month.
    """
    # Personal month seed shifts the base days
    personal_month = (life_path + month) % 9 or 9
    base_days = [life_path, life_path + personal_month, life_path + 9]
    compatible = [(life_path * personal_month) % 28 or 28, (personal_month * 2 + month) % 28 or 1]
    all_days = [d for d in base_days + compatible if 1 <= d <= 31]
    return sorted(set(all_days))[:5]


# ============================================================================
# ENDPOINTS
# ============================================================================


class CoreNumerologyRequest(BaseModel):
    """Request for core number calculation with method selection."""
    profile: ProfilePayload
    method: str = "pythagorean"  # 'pythagorean' or 'chaldean'


@router.post("/core", response_model=ApiResponse[Dict[str, Any]])
async def calculate_core_numerology(
    request: Request,
    req: CoreNumerologyRequest,
) -> ApiResponse[Dict[str, Any]]:
    """
    Calculate core numerology numbers with system selection.

    ## Parameters
    - **profile**: Name + date of birth
    - **method**: `pythagorean` (default, Western 1–9) or `chaldean` (Babylonian 1–8)

    ## Response
    Returns life_path, name_number, method label, meaning, and advice.
    Fast deterministic calculation — no chart needed.
    """
    from ..engine.numerology import calculate_core_numbers

    try:
        datetime.fromisoformat(req.profile.date_of_birth)
    except ValueError as e:
        raise InvalidDateError(f"Invalid date: {e}", value=req.profile.date_of_birth)

    result = calculate_core_numbers(
        dob=req.profile.date_of_birth,
        name=req.profile.name,
        method=req.method,
    )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=result,
        message=f"Core numbers calculated using {result['method']} method",
    )


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
                f"Invalid date format: {str(e)}", value=req.profile.date_of_birth
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
            method=req.method,
        )

        # Extract from core_numbers structure (correct mapping)
        core = numerology.get("core_numbers", {})
        cycles = numerology.get("cycles", {})

        # Life path data
        life_path_raw = core.get("life_path", {})
        life_path_num = life_path_raw.get("number", 1)
        life_path_meaning = life_path_raw.get("meaning", "")
        
        # Expression = Destiny in traditional numerology
        expression_raw = core.get("expression", {})
        destiny_num = expression_raw.get("number", 1)
        destiny_meaning = expression_raw.get("meaning", "")
        
        # Soul urge and personality for traits
        soul_urge_raw = core.get("soul_urge", {})
        personality_raw = core.get("personality", {})
        
        # Personal year cycle
        personal_year_raw = cycles.get("personal_year", {})
        personal_year_num = personal_year_raw.get("number", 1)
        personal_year_meaning = personal_year_raw.get("meaning", "")

        # Build structured life path data
        life_path_data = LifePathNumber(
            number=life_path_num,
            meaning=life_path_meaning,
            traits=_generate_life_path_traits(life_path_num),
            life_purpose=_generate_life_purpose(life_path_num),
        )

        # Build personal year data
        personal_year_data = PersonalYearCycle(
            year=datetime.now(timezone.utc).year,
            cycle_number=personal_year_num,
            interpretation=personal_year_meaning,
            focus_areas=_generate_focus_areas(personal_year_num),
        )

        # Get current month/year for time-sensitive calculations
        now_utc = datetime.now(timezone.utc)
        current_month = now_utc.month
        current_year = now_utc.year

        # Personal month cycle (changes per calendar month)
        personal_month_raw = cycles.get("personal_month", {})
        personal_month_num = personal_month_raw.get("number", 1)

        # Generate lucky numbers including personal month (changes monthly)
        lucky_nums = _generate_lucky_numbers(life_path_num, destiny_num, personal_year_num, personal_month_num)

        # Build insights from all core numbers
        insights = {
            "soul_urge": soul_urge_raw.get("meaning", ""),
            "personality": personality_raw.get("meaning", ""),
            "personal_month": personal_month_raw.get("meaning", ""),
            "personal_day": cycles.get("personal_day", {}).get("meaning", ""),
        }

        response_data = NumerologyData(
            profile=req.profile,
            life_path=life_path_data,
            destiny_number=destiny_num,
            destiny_interpretation=destiny_meaning,
            personal_year=personal_year_data,
            compatibility_number=None,
            compatibility_interpretation=None,
            lucky_numbers=lucky_nums,
            auspicious_days=_generate_auspicious_days(life_path_num, current_month, current_year),
            numerology_insights=insights,
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
            },
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(
            f"Numerology calculation error: {str(e)}\n{tb}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "NUMEROLOGY_ERROR",
                "message": "Failed to calculate numerology profile",
                "debug": f"{type(e).__name__}: {str(e)}",
            },
        )


@router.post("/compatibility", response_model=ApiResponse[Dict[str, Any]])
async def calculate_numerology_compatibility(
    request: Request,
    req: NumerologyCompatibilityRequest,
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
        for i, profile in enumerate([req.profile, req.person_b], 1):
            try:
                datetime.fromisoformat(profile.date_of_birth)
            except ValueError as e:
                raise InvalidDateError(
                    f"Person {i}: Invalid date format: {str(e)}",
                    value=profile.date_of_birth,
                )

        logger.info(
            f"Calculating numerology compatibility",
            request_id=request_id,
            person_a=req.profile.name,
            person_b=req.person_b.name,
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
        life_path_a = (
            numerology_a.get("core_numbers", {})
            .get("life_path", {})
            .get("number", 1)
        )
        life_path_b = (
            numerology_b.get("core_numbers", {})
            .get("life_path", {})
            .get("number", 1)
        )

        # Simple compatibility algorithm: numbers that match or complement are more compatible
        compatibility_score = min(
            1.0, max(0.0, 1.0 - (abs(life_path_a - life_path_b) / 10.0))
        )

        if abs(life_path_a - life_path_b) == 0:
            interpretation = (
                f"Life path {life_path_a} and {life_path_b} share strong resonance"
            )
        elif abs(life_path_a - life_path_b) <= 2:
            interpretation = (
                f"Life path {life_path_a} and {life_path_b} have good compatibility"
            )
        else:
            interpretation = (
                f"Life path {life_path_a} and {life_path_b} have moderate compatibility"
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
            "interpretation": interpretation,
            "strengths": numerology_a.get("compatibility_strengths", []),
            "challenges": numerology_a.get("compatibility_challenges", []),
        }

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Numerology compatibility calculated successfully",
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
            },
        )
