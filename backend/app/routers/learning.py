"""
API v2 - Learning Content Endpoint
Standardized request/response format for educational astrology content.
"""

from typing import Dict, Generic, List, Optional, TypeVar

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from ..engine.glossary import get_sign_info
from ..exceptions import StructuredLogger
from ..schemas import ApiResponse, ResponseStatus

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
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
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
        all_modules_response = await list_learning_modules(
            request, category=None, difficulty=None, page=1, page_size=200
        )
        found = next((m for m in all_modules_response.items if m.id == module_id), None)

        if not found:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"Module {module_id} not found",
                },
            )

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

        # Glossary data
        entries = [
            GlossaryEntry(
                term="Aspect",
                definition="The angular relationship between two planets and the tension or harmony it creates.",
                category="astrology",
                usage_example="A trine usually reads as easier flow between two planetary functions.",
                related_terms=["conjunction", "trine", "opposition"],
            ),
            GlossaryEntry(
                term="House",
                definition="One of the twelve life areas used to place planetary experience into context.",
                category="astrology",
                usage_example="The seventh house tends to frame partnerships, contracts, and one-to-one dynamics.",
                related_terms=["cusp", "ruler"],
            ),
            GlossaryEntry(
                term="Conjunction",
                definition="Two planets at approximately the same degree, intensifying or blending their energies.",
                category="astrology",
                usage_example="A Sun-Mars conjunction can amplify drive and assertiveness.",
                related_terms=["aspect", "orb", "opposition"],
            ),
            GlossaryEntry(
                term="Trine",
                definition="A 120-degree aspect between planets associated with natural ease and flow.",
                category="astrology",
                usage_example="Venus trine Jupiter can show natural luck in relationships or finances.",
                related_terms=["aspect", "sextile", "conjunction"],
            ),
            GlossaryEntry(
                term="Opposition",
                definition="A 180-degree aspect between planets, representing tension or the need for balance.",
                category="astrology",
                usage_example="Sun opposite Moon often shows an inner tension between identity and emotional needs.",
                related_terms=["aspect", "conjunction", "trine"],
            ),
            GlossaryEntry(
                term="Retrograde",
                definition="The apparent backward motion of a planet as seen from Earth, often slowing or internalizing that planet's themes.",
                category="astrology",
                usage_example="Mercury retrograde is associated with communication delays and revisiting old decisions.",
                related_terms=["transit", "direct", "station"],
            ),
            GlossaryEntry(
                term="Rising Sign",
                definition="The zodiac sign on the eastern horizon at birth, used to frame how life arrives and how a person presents.",
                category="zodiac",
                usage_example="The Rising sign often shapes the first impression before the Sun sign becomes visible.",
                related_terms=["ascendant", "houses"],
            ),
            GlossaryEntry(
                term="Ascendant",
                definition="Another name for the Rising sign — the zodiac degree on the eastern horizon at the moment of birth.",
                category="zodiac",
                usage_example="An Aries Ascendant often projects confidence and directness regardless of the Sun sign.",
                related_terms=["rising sign", "first house"],
            ),
            GlossaryEntry(
                term="Sun Sign",
                definition="The zodiac sign the Sun occupied at birth, representing core identity and ego.",
                category="zodiac",
                usage_example="A Scorpio Sun tends to pursue depth and transformation as a life theme.",
                related_terms=["moon sign", "rising sign", "natal chart"],
            ),
            GlossaryEntry(
                term="Moon Sign",
                definition="The zodiac sign the Moon occupied at birth, representing emotional nature and instinctive responses.",
                category="zodiac",
                usage_example="A Cancer Moon often prioritizes security and close emotional bonds.",
                related_terms=["sun sign", "rising sign", "emotions"],
            ),
            GlossaryEntry(
                term="Natal Chart",
                definition="A snapshot of the sky at the moment of birth, used to map planetary placements, houses, and aspects.",
                category="astrology",
                usage_example="Reading a natal chart starts with the Sun, Moon, and Rising as the primary three signals.",
                related_terms=["birth chart", "houses", "planets"],
            ),
            GlossaryEntry(
                term="Transit",
                definition="The current movement of a planet through the sky and its relationship to a natal chart.",
                category="astrology",
                usage_example="Saturn transiting the 10th house often triggers career restructuring or accountability.",
                related_terms=["progression", "retrograde", "natal chart"],
            ),
            GlossaryEntry(
                term="Life Path",
                definition="The core numerology number derived from the birth date that frames long-arc direction.",
                category="numerology",
                usage_example="A Life Path 6 often emphasizes care, responsibility, and relational duty.",
                related_terms=["destiny number", "personal year"],
            ),
            GlossaryEntry(
                term="Personal Year",
                definition="A numerology cycle that describes the main annual timing theme a person is moving through.",
                category="numerology",
                usage_example="A Personal Year 9 often brings completion, closure, or necessary release.",
                related_terms=["life path", "cycles"],
            ),
            GlossaryEntry(
                term="Expression Number",
                definition="A numerology number derived from the full birth name, showing natural talents and how someone expresses themselves.",
                category="numerology",
                usage_example="An Expression 3 often indicates a gift for communication, creativity, or performance.",
                related_terms=["life path", "soul urge"],
            ),
            GlossaryEntry(
                term="Soul Urge",
                definition="A numerology number based on the vowels in the birth name, representing inner motivation and desire.",
                category="numerology",
                usage_example="A Soul Urge 7 often craves quiet, depth, and time to think without distraction.",
                related_terms=["expression number", "life path"],
            ),
            GlossaryEntry(
                term="Element",
                definition="One of four categories — Fire, Earth, Air, Water — grouping zodiac signs by temperament and operating style.",
                category="elements",
                usage_example="Fire signs tend to act quickly, Earth signs prefer to test before committing.",
                related_terms=["modality", "polarity", "zodiac"],
            ),
            GlossaryEntry(
                term="Modality",
                definition="One of three zodiac groupings — Cardinal, Fixed, Mutable — describing how a sign initiates, maintains, or adapts.",
                category="elements",
                usage_example="Fixed signs like Taurus and Scorpio tend to hold course even under pressure.",
                related_terms=["element", "polarity"],
            ),
            GlossaryEntry(
                term="Synastry",
                definition="The comparison of two natal charts to assess relationship dynamics and compatibility.",
                category="astrology",
                usage_example="Strong Venus-Mars contacts in synastry are often associated with physical attraction.",
                related_terms=["composite chart", "compatibility", "aspect"],
            ),
            GlossaryEntry(
                term="Orb",
                definition="The margin of degrees allowed when measuring an aspect — wider orbs are considered weaker.",
                category="astrology",
                usage_example="A 10-degree orb for a conjunction would still count the aspect, but with less intensity.",
                related_terms=["aspect", "conjunction", "trine"],
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
