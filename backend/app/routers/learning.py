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

        all_modules = [
            # Astrology
            LearningModule(
                id="astro-1",
                title="What is Astrology?",
                description="Understanding the cosmic language",
                category="astrology",
                difficulty="beginner",
                duration_minutes=5,
                content="Astrology is an ancient practice that studies the positions and movements of celestial bodies and their influence on human affairs. For thousands of years, cultures around the world have looked to the stars for guidance, believing that the cosmos reflects patterns in our lives.",
                keywords=["astrology", "basics", "introduction"],
                related_modules=["astro-2", "astro-3"],
            ),
            LearningModule(
                id="astro-2",
                title="The Birth Chart",
                description="Your cosmic blueprint",
                category="astrology",
                difficulty="beginner",
                duration_minutes=8,
                content="Your birth chart, also known as a natal chart, is a snapshot of the sky at the exact moment you were born. It shows the positions of all major celestial bodies in relation to the zodiac signs and houses.",
                keywords=["birth chart", "natal chart", "blueprint"],
                related_modules=["astro-1", "astro-3"],
            ),
            LearningModule(
                id="astro-3",
                title="Planets & Their Meanings",
                description="Celestial influences",
                category="astrology",
                difficulty="intermediate",
                duration_minutes=10,
                content="Each planet in astrology represents different aspects of life and personality. The Sun represents your core identity, the Moon your emotions, Mercury your communication style, Venus your approach to love and beauty, and Mars your drive and energy.",
                keywords=["planets", "meanings", "celestial"],
                related_modules=["astro-2", "astro-4"],
            ),
            LearningModule(
                id="astro-4",
                title="Houses in Astrology",
                description="Life areas and experiences",
                category="astrology",
                difficulty="intermediate",
                duration_minutes=12,
                content="The 12 houses in astrology represent different areas of life. The 1st house is about self and appearance, the 7th about relationships, the 10th about career, and so on. Each house tells a story about a specific life domain.",
                keywords=["houses", "life areas", "domains"],
                related_modules=["astro-3"],
            ),
            # Numerology
            LearningModule(
                id="num-1",
                title="Introduction to Numerology",
                description="The power of numbers",
                category="numerology",
                difficulty="beginner",
                duration_minutes=5,
                content="Numerology is the study of the mystical relationship between numbers and events in life. Each number carries its own unique vibration and meaning that can reveal insights about your personality and life path.",
                keywords=["numerology", "numbers", "introduction"],
                related_modules=["num-2"],
            ),
            LearningModule(
                id="num-2",
                title="Your Life Path Number",
                description="Your soul's purpose",
                category="numerology",
                difficulty="beginner",
                duration_minutes=7,
                content="The Life Path Number is the most important number in your numerology chart. Calculated from your birth date, it reveals your primary purpose in life and the lessons you're here to learn.",
                keywords=["life path", "purpose", "destiny"],
                related_modules=["num-1", "num-3"],
            ),
            LearningModule(
                id="num-3",
                title="Personal Year Cycles",
                description="Annual energy themes",
                category="numerology",
                difficulty="intermediate",
                duration_minutes=8,
                content="Personal Year cycles run in 9-year patterns. Each year carries a specific energy and theme that influences what you should focus on. Year 1 is about new beginnings, Year 5 about change, Year 9 about completion.",
                keywords=["cycles", "personal year", "themes"],
                related_modules=["num-2"],
            ),
            # Zodiac
            LearningModule(
                id="zodiac-1",
                title="The 12 Signs",
                description="Overview of the zodiac",
                category="zodiac",
                difficulty="beginner",
                duration_minutes=10,
                content="The zodiac consists of 12 signs, each with unique characteristics. From fiery Aries to dreamy Pisces, each sign represents a different archetype and approach to life.",
                keywords=["zodiac", "signs", "overview"],
                related_modules=["zodiac-2"],
            ),
            LearningModule(
                id="zodiac-2",
                title="Sun, Moon & Rising",
                description="Your cosmic trinity",
                category="zodiac",
                difficulty="intermediate",
                duration_minutes=8,
                content="Your Sun sign represents your core identity, your Moon sign your emotional nature, and your Rising sign how others perceive you. Together, these three create a more complete picture of your personality.",
                keywords=["sun", "moon", "rising", "trinity"],
                related_modules=["zodiac-1", "zodiac-3"],
            ),
            LearningModule(
                id="zodiac-3",
                title="Sign Compatibility",
                description="Cosmic connections",
                category="zodiac",
                difficulty="intermediate",
                duration_minutes=10,
                content="Some signs naturally harmonize while others create tension. Understanding sign compatibility can help you navigate relationships more effectively.",
                keywords=["compatibility", "relationships", "harmony"],
                related_modules=["zodiac-2"],
            ),
            # Elements
            LearningModule(
                id="elem-1",
                title="Fire Signs",
                description="Aries, Leo, Sagittarius",
                category="elements",
                difficulty="beginner",
                duration_minutes=6,
                content="Fire signs are passionate, dynamic, and energetic. They bring warmth and enthusiasm to everything they do. Aries leads with courage, Leo with heart, and Sagittarius with adventure.",
                keywords=["fire", "aries", "leo", "sagittarius"],
                related_modules=["elem-2", "elem-3", "elem-4"],
            ),
            LearningModule(
                id="elem-2",
                title="Earth Signs",
                description="Taurus, Virgo, Capricorn",
                category="elements",
                difficulty="beginner",
                duration_minutes=6,
                content="Earth signs are grounded, practical, and reliable. They value stability and material security. Taurus brings patience, Virgo brings precision, and Capricorn brings ambition.",
                keywords=["earth", "taurus", "virgo", "capricorn"],
                related_modules=["elem-1", "elem-3", "elem-4"],
            ),
            LearningModule(
                id="elem-3",
                title="Air Signs",
                description="Gemini, Libra, Aquarius",
                category="elements",
                difficulty="beginner",
                duration_minutes=6,
                content="Air signs are intellectual, communicative, and social. They thrive on ideas and connections. Gemini brings curiosity, Libra brings harmony, and Aquarius brings innovation.",
                keywords=["air", "gemini", "libra", "aquarius"],
                related_modules=["elem-1", "elem-2", "elem-4"],
            ),
            LearningModule(
                id="elem-4",
                title="Water Signs",
                description="Cancer, Scorpio, Pisces",
                category="elements",
                difficulty="beginner",
                duration_minutes=6,
                content="Water signs are emotional, intuitive, and sensitive. They navigate life through feeling. Cancer brings nurturing, Scorpio brings depth, and Pisces brings compassion.",
                keywords=["water", "cancer", "scorpio", "pisces"],
                related_modules=["elem-1", "elem-2", "elem-3"],
            ),
        ]
        modules = all_modules

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

        # Reuse the same catalogue as list_learning_modules
        all_modules_response = await list_learning_modules(request, category=None, difficulty=None, params=None)
        found = next((m for m in all_modules_response.items if m.id == module_id), None)

        if not found:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Module {module_id} not found"})

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=found,
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
