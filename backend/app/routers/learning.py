"""
API v2 - Learning Content Endpoint
Standardized request/response format for educational astrology content.
"""

from typing import Dict, Generic, List, Optional, TypeVar

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from ..engine.glossary import get_sign_info
from ..exceptions import StructuredLogger
from ..schemas import ApiResponse, PaginationParams, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/learning", tags=["Learning"])
PageT = TypeVar("PageT")

ELEMENT_COMPATIBILITY = {
    "Fire": {
        "leo": 0.95,
        "sagittarius": 0.92,
        "gemini": 0.84,
        "libra": 0.8,
        "aquarius": 0.78,
    },
    "Earth": {
        "virgo": 0.94,
        "capricorn": 0.92,
        "cancer": 0.82,
        "pisces": 0.8,
        "scorpio": 0.77,
    },
    "Air": {
        "libra": 0.95,
        "aquarius": 0.92,
        "aries": 0.84,
        "leo": 0.8,
        "sagittarius": 0.78,
    },
    "Water": {
        "scorpio": 0.95,
        "pisces": 0.92,
        "taurus": 0.82,
        "virgo": 0.8,
        "capricorn": 0.77,
    },
}


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class LearningModule(BaseModel):
    """Single learning module."""

    id: str
    title: str
    description: str
    category: str
    difficulty: str  # beginner, intermediate, advanced
    duration_minutes: int
    content: str
    keywords: List[str]
    related_modules: List[str] = []


class ZodiacGuidance(BaseModel):
    """Zodiac sign guidance."""

    sign: str
    date_range: str
    element: str
    ruling_planet: str
    characteristics: List[str]
    compatibility: Dict[str, float]
    guidance: str


class GlossaryEntry(BaseModel):
    """Learning glossary entry."""

    term: str
    definition: str
    category: str
    usage_example: str
    related_terms: List[str] = []


class LegacyCompatiblePage(BaseModel, Generic[PageT]):
    """Pagination payload that preserves old iOS keys and new v2 metadata."""

    data: List[PageT]
    items: List[PageT]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


def _build_legacy_page(
    items: List[PageT],
    page: int,
    page_size: int,
    total: int,
) -> LegacyCompatiblePage[PageT]:
    total_pages = max(1, ((total - 1) // page_size) + 1) if page_size else 1
    has_next = page < total_pages
    has_prev = page > 1
    return LegacyCompatiblePage(
        data=items,
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/modules", response_model=LegacyCompatiblePage[LearningModule])
async def list_learning_modules(
    request: Request,
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    params: PaginationParams = None,
) -> LegacyCompatiblePage[LearningModule]:
    """
    List available learning modules with pagination.

    ## Parameters
    - **category**: Filter by category (astrology, numerology, tarot)
    - **difficulty**: Filter by difficulty level
    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 10)

    ## Response
    Returns paginated list of learning modules.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Listing learning modules",
            request_id=request_id,
            category=category,
            difficulty=difficulty,
        )

        # Mock data - integrate with actual database
        modules = [
            LearningModule(
                id="mod_001",
                title="Understanding the Zodiac",
                description="Learn the 12 zodiac signs and their characteristics",
                category="astrology",
                difficulty="beginner",
                duration_minutes=15,
                content="The zodiac is a band of constellations...",
                keywords=["zodiac", "astrology", "signs"],
            ),
            LearningModule(
                id="mod_002",
                title="Reading Your Natal Chart",
                description="How to interpret your birth chart",
                category="astrology",
                difficulty="intermediate",
                duration_minutes=30,
                content="Your natal chart is a snapshot of the sky...",
                keywords=["natal chart", "birth chart", "interpretation"],
            ),
        ]

        # Apply filters
        if category:
            modules = [m for m in modules if m.category == category]
        if difficulty:
            modules = [m for m in modules if m.difficulty == difficulty]

        # Pagination
        page = params.page if params else 1
        page_size = params.page_size if params else 10
        start_idx = (page - 1) * page_size
        paginated = modules[start_idx : start_idx + page_size]

        return _build_legacy_page(
            items=paginated,
            page=page,
            page_size=page_size,
            total=len(modules),
        )
    except Exception as e:
        logger.error(
            f"Module listing error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LISTING_ERROR",
                "message": "Failed to list modules",
            },
        )


@router.get("/module/{module_id}", response_model=ApiResponse[LearningModule])
async def get_learning_module(
    request: Request,
    module_id: str,
) -> ApiResponse[LearningModule]:
    """
    Get a specific learning module by ID.

    ## Parameters
    - **module_id**: Module identifier

    ## Response
    Returns full module content and metadata.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Retrieving learning module",
            request_id=request_id,
            module_id=module_id,
        )

        # Mock data
        module = LearningModule(
            id=module_id,
            title="Understanding the Zodiac",
            description="Learn the 12 zodiac signs",
            category="astrology",
            difficulty="beginner",
            duration_minutes=15,
            content="The zodiac is a band of constellations...",
            keywords=["zodiac", "astrology"],
            related_modules=["mod_002", "mod_003"],
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=module,
            message="Module retrieved successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Module retrieval error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RETRIEVAL_ERROR",
                "message": "Failed to retrieve module",
            },
        )


@router.get("/zodiac/{sign}", response_model=ApiResponse[ZodiacGuidance])
async def get_zodiac_guidance(
    request: Request,
    sign: str,
) -> ApiResponse[ZodiacGuidance]:
    """
    Get guidance for a specific zodiac sign.

    ## Parameters
    - **sign**: Zodiac sign name (aries, taurus, gemini, etc.)

    ## Response
    Returns zodiac characteristics, compatibility, and current guidance.
    """
    request_id = request.state.request_id

    try:
        sign_lower = sign.lower()

        logger.info(
            "Retrieving zodiac guidance",
            request_id=request_id,
            sign=sign_lower,
        )

        sign_name = sign_lower.capitalize()
        sign_info = get_sign_info(sign_name)
        if not sign_info:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ZODIAC_NOT_FOUND",
                    "message": f"Unknown zodiac sign: {sign}",
                },
            )

        zodiac_data = ZodiacGuidance(
            sign=sign_name,
            date_range=sign_info["dates"],
            element=sign_info["element"],
            ruling_planet=sign_info["ruler"],
            characteristics=sign_info["traits"],
            compatibility=ELEMENT_COMPATIBILITY.get(sign_info["element"], {}),
            guidance=sign_info["description"],
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=zodiac_data,
            message="Zodiac guidance retrieved successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Zodiac guidance error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ZODIAC_ERROR",
                "message": "Failed to retrieve zodiac guidance",
            },
        )


@router.get("/glossary", response_model=LegacyCompatiblePage[GlossaryEntry])
async def list_glossary(
    request: Request,
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
) -> LegacyCompatiblePage[GlossaryEntry]:
    """
    List glossary terms with optional filtering.

    ## Parameters
    - **search**: Search term (searches title and definition)
    - **category**: Filter by category

    ## Response
    Returns paginated list of glossary entries.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Listing glossary",
            request_id=request_id,
            search=search,
            category=category,
        )

        # Mock glossary data
        entries = [
            GlossaryEntry(
                term="Aspect",
                definition="Angular relationship between two planets",
                category="astrology",
                usage_example="A 60-degree aspect is called a sextile",
                related_terms=["conjunction", "opposition", "trine"],
            ),
            GlossaryEntry(
                term="House",
                definition="One of 12 divisions of the natal chart",
                category="astrology",
                usage_example="The 7th house rules relationships",
                related_terms=["cusp", "ruler"],
            ),
        ]

        # Apply filters
        if search:
            search_lower = search.lower()
            entries = [
                e
                for e in entries
                if search_lower in e.term.lower()
                or search_lower in e.definition.lower()
            ]
        if category:
            entries = [e for e in entries if e.category == category]

        return _build_legacy_page(
            items=entries,
            page=1,
            page_size=10,
            total=len(entries),
        )
    except Exception as e:
        logger.error(
            f"Glossary listing error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "GLOSSARY_ERROR",
                "message": "Failed to list glossary",
            },
        )
