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
                content=(
                    "Astrology is the study of how the positions of the Sun, Moon, planets, and "
                    "stars correspond to personality, events, and timing here on Earth. It is not "
                    "about the stars 'controlling' you — it is a symbolic language, a centuries-old "
                    "system for describing patterns in character, relationships, and timing.\n\n"
                    "The core idea is simple: the sky at the moment you were born forms a map. Where "
                    "each planet sat, which zodiac sign it occupied, and the angles the planets made "
                    "to one another all become symbols an astrologer reads together, like words in a "
                    "sentence.\n\n"
                    "Nearly every culture — Babylonian, Egyptian, Greek, Indian, Chinese, Mayan — "
                    "built its own astrology, because watching the sky was humanity's first calendar "
                    "and compass. Western astrology, which this app uses, traces back to Hellenistic "
                    "Greece and organizes the sky into twelve signs and twelve houses.\n\n"
                    "As you learn, hold two things at once: astrology is a tool for self-reflection, "
                    "not fortune-telling, and its value comes from how thoughtfully you apply it. "
                    "Treat each placement as a tendency to explore, not a fixed fate. The next "
                    "lessons break the map into its pieces — the birth chart, the planets, the signs, "
                    "and the houses — so you can start reading it yourself."
                ),
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
                content=(
                    "Your birth chart (or natal chart) is a 360-degree snapshot of the sky at the "
                    "exact date, time, and place you were born. It is the foundation of everything in "
                    "astrology — every reading, forecast, and compatibility report starts here.\n\n"
                    "Think of the chart as four layers that work together:\n"
                    "• Signs describe style — the 'how'. There are twelve, from Aries to Pisces.\n"
                    "• Planets describe what — the functions of the psyche, like identity (Sun), "
                    "emotion (Moon), or drive (Mars).\n"
                    "• Houses describe where — the twelve areas of life a planet shows up in, from "
                    "self and money to career and relationships.\n"
                    "• Aspects describe relationships — the angles between planets that show where "
                    "energies cooperate or clash.\n\n"
                    "Meaning comes from combining these. 'Mars in Aries in the 10th house' reads as: "
                    "drive (Mars), expressed boldly and directly (Aries), focused on career and "
                    "public life (10th house).\n\n"
                    "Accuracy matters. Your Sun sign needs only your birth date, but your Moon sign, "
                    "rising sign, and houses need your exact birth time and place — even a few hours' "
                    "difference can change them. Without a birth time the chart still works for "
                    "sign-level insight; it just can't place the houses precisely.\n\n"
                    "Don't try to absorb everything at once. Start with your 'big three' — Sun, Moon, "
                    "and Rising — then add one planet at a time."
                ),
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
                content=(
                    "In astrology each planet represents a different function of the personality — a "
                    "distinct voice inside you. Reading a chart gets far easier once each planet "
                    "keeps a clear job.\n\n"
                    "The personal planets shape day-to-day character:\n"
                    "• Sun — your core identity, ego, and what energizes you.\n"
                    "• Moon — your emotions, instincts, and what makes you feel safe.\n"
                    "• Mercury — how you think, learn, and communicate.\n"
                    "• Venus — how you love, what you value, and your sense of beauty.\n"
                    "• Mars — your drive, anger, and how you take action.\n\n"
                    "The social planets describe how you grow and connect to the wider world:\n"
                    "• Jupiter — expansion, luck, beliefs, and where you seek meaning.\n"
                    "• Saturn — discipline, limits, responsibility, and hard-won lessons.\n\n"
                    "The outer planets move slowly and color whole generations:\n"
                    "• Uranus — change, rebellion, and sudden insight.\n"
                    "• Neptune — dreams, intuition, spirituality, and illusion.\n"
                    "• Pluto — power, transformation, and deep renewal.\n\n"
                    "To interpret any planet, combine three things: the planet (what), its sign (how "
                    "it expresses), and its house (where it plays out). For example, Venus (love) in "
                    "Capricorn (cautious, committed) in the 7th house (partnership) suggests someone "
                    "who takes relationships seriously and is loyal once committed.\n\n"
                    "Start with the Sun, Moon, and Mercury — identity, feeling, and mind — and you'll "
                    "already understand most of what drives someone."
                ),
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
                content=(
                    "If signs are 'how' and planets are 'what', the twelve houses are 'where' — the "
                    "areas of life where a planet's energy actually shows up. The houses are set by "
                    "the horizon and your birth time, which is why an accurate time matters so much.\n\n"
                    "Here is the quick tour:\n"
                    "• 1st — self, body, first impressions, how you start things.\n"
                    "• 2nd — money, possessions, values, self-worth.\n"
                    "• 3rd — communication, siblings, learning, short trips.\n"
                    "• 4th — home, family, roots, your private world.\n"
                    "• 5th — creativity, romance, play, children.\n"
                    "• 6th — work, health, daily routines, service.\n"
                    "• 7th — partnerships, marriage, close one-to-one relationships.\n"
                    "• 8th — intimacy, shared resources, transformation, the taboo.\n"
                    "• 9th — travel, higher education, philosophy, belief.\n"
                    "• 10th — career, reputation, public role, ambition.\n"
                    "• 11th — friends, groups, hopes, networks.\n"
                    "• 12th — the unconscious, solitude, spirituality, what's hidden.\n\n"
                    "A planet 'lights up' the house it sits in. Several planets in one house show "
                    "where much of your energy concentrates; an empty house simply means that area "
                    "runs quietly in the background — it isn't a problem.\n\n"
                    "To read a placement, ask: which planet, in which sign, in which house? 'Moon "
                    "(emotion) in Cancer (nurturing) in the 4th house (home)' points to someone "
                    "deeply tied to family and a sense of belonging."
                ),
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
                content=(
                    "Numerology is the study of the meaning behind numbers and how they relate to "
                    "your character and timing. Like astrology, it is a symbolic system: each number "
                    "from 1 to 9 carries a distinct personality, plus the 'master numbers' 11, 22, "
                    "and 33.\n\n"
                    "The practice has roots in Pythagorean Greece, where it was taught that numbers "
                    "are the building blocks of reality. Modern Western numerology turns your name "
                    "and birth date into a small set of core numbers that describe who you are and "
                    "the cycles you move through.\n\n"
                    "The headline numbers are:\n"
                    "• Life Path — from your birth date; your overall direction and life lessons "
                    "(the most important number).\n"
                    "• Expression / Destiny — from the letters of your full birth name; your natural "
                    "talents.\n"
                    "• Soul Urge — from the vowels in your name; your inner desires and motivations.\n"
                    "• Personality — from the consonants; how others first experience you.\n\n"
                    "Numbers are reduced by adding their digits until you reach a single digit (or a "
                    "master number). Numerology shines as a practical tool: pair your core numbers "
                    "with your current cycle (the Personal Year) and you get a simple read on what to "
                    "focus on now. The next lessons cover the Life Path and the yearly cycles."
                ),
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
                content=(
                    "The Life Path is the single most important number in numerology. Calculated "
                    "from your full birth date, it describes your main direction in life — the "
                    "themes, strengths, and lessons that repeat for you across the years.\n\n"
                    "You find it by reducing your birth date to a single digit (keeping 11, 22, and "
                    "33 as master numbers). Each result has a clear flavor:\n"
                    "• 1 — the Leader: independence, initiative, drive.\n"
                    "• 2 — the Diplomat: partnership, sensitivity, balance.\n"
                    "• 3 — the Communicator: creativity, expression, joy.\n"
                    "• 4 — the Builder: structure, discipline, stability.\n"
                    "• 5 — the Explorer: freedom, change, adventure.\n"
                    "• 6 — the Nurturer: responsibility, care, harmony.\n"
                    "• 7 — the Seeker: analysis, intuition, depth.\n"
                    "• 8 — the Powerhouse: ambition, authority, abundance.\n"
                    "• 9 — the Humanitarian: compassion, completion, wisdom.\n"
                    "• 11 / 22 / 33 — master numbers: heightened intuition (11), large-scale "
                    "building (22), compassionate teaching (33).\n\n"
                    "Your Life Path isn't a limit — it's the lens through which your choices play "
                    "out. A '5' will keep meeting themes of freedom and change; the growth is in "
                    "handling that energy wisely rather than restlessly.\n\n"
                    "Life Path is most useful paired with your Personal Year (next lesson), which "
                    "tells you when its themes are most active."
                ),
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
                content=(
                    "Numerology describes not just who you are but when — and the Personal Year is "
                    "the most practical timing tool. Your life moves through repeating nine-year "
                    "cycles, and each year within the cycle carries a distinct theme.\n\n"
                    "You calculate it by adding your birth month and day to the current year, then "
                    "reducing to a single digit. The nine years tend to flow like this:\n"
                    "• Year 1 — fresh starts, new projects, planting seeds.\n"
                    "• Year 2 — patience, partnerships, slow development.\n"
                    "• Year 3 — creativity, socializing, self-expression.\n"
                    "• Year 4 — hard work, structure, laying foundations.\n"
                    "• Year 5 — change, freedom, the unexpected.\n"
                    "• Year 6 — home, family, responsibility, relationships.\n"
                    "• Year 7 — reflection, study, rest, inner growth.\n"
                    "• Year 8 — ambition, money, recognition, power.\n"
                    "• Year 9 — completion, release, letting go to make room.\n\n"
                    "The skill is to work with the year rather than against it. A Year 1 rewards bold "
                    "beginnings; a Year 9 rewards finishing and releasing — pushing to start "
                    "something brand-new in a 9 often feels like swimming upstream.\n\n"
                    "Treat the cycle as a posture, then test it against what's actually happening in "
                    "your life. Combined with your Life Path, it turns numerology into a simple, "
                    "usable planning lens."
                ),
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
                content=(
                    "The twelve zodiac signs are the 'styles' of astrology — twelve distinct ways "
                    "energy expresses itself. Every planet in a chart wears the costume of the sign "
                    "it occupies.\n\n"
                    "Each sign blends an element and a modality. The four elements describe "
                    "temperament: Fire (passion, action), Earth (practicality, stability), Air "
                    "(intellect, connection), and Water (emotion, intuition). The three modalities "
                    "describe approach: Cardinal signs initiate, Fixed signs sustain, Mutable signs "
                    "adapt.\n\n"
                    "In order:\n"
                    "• Aries — bold initiator (Fire, Cardinal).\n"
                    "• Taurus — steady builder (Earth, Fixed).\n"
                    "• Gemini — curious connector (Air, Mutable).\n"
                    "• Cancer — nurturing protector (Water, Cardinal).\n"
                    "• Leo — radiant performer (Fire, Fixed).\n"
                    "• Virgo — careful improver (Earth, Mutable).\n"
                    "• Libra — harmonizing diplomat (Air, Cardinal).\n"
                    "• Scorpio — intense investigator (Water, Fixed).\n"
                    "• Sagittarius — adventurous seeker (Fire, Mutable).\n"
                    "• Capricorn — disciplined achiever (Earth, Cardinal).\n"
                    "• Aquarius — original reformer (Air, Fixed).\n"
                    "• Pisces — compassionate dreamer (Water, Mutable).\n\n"
                    "Signs are styles, not whole identities — you are not 'just' your Sun sign. A "
                    "full chart mixes many signs across its planets. Knowing the element and modality "
                    "of a sign is often enough to grasp how it behaves."
                ),
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
                content=(
                    "Before diving into a whole chart, learn your 'big three': Sun, Moon, and Rising "
                    "sign. Together they give a fast, surprisingly complete sketch of a person.\n\n"
                    "• Sun sign — your core identity, ego, and what lights you up. It's the sign most "
                    "people know, set by your birth date. It answers 'who am I at my center?'\n"
                    "• Moon sign — your emotional nature, instincts, and what you need to feel safe. "
                    "More private than the Sun and often only visible to those close to you; it needs "
                    "your birth date and, ideally, time.\n"
                    "• Rising sign (Ascendant) — the sign that was rising on the eastern horizon at "
                    "your birth. It shapes your first impression and your instinctive approach to "
                    "life, and it needs an accurate birth time.\n\n"
                    "A helpful metaphor: the Rising is the book cover, the Sun is the main character, "
                    "and the Moon is the inner emotional world revealed as you read on.\n\n"
                    "When two people seem to embody their sign very differently, the big three "
                    "usually explain why. A Capricorn Sun with a Leo Rising and Pisces Moon is a very "
                    "different person from a Capricorn with Virgo Rising and Scorpio Moon. Start here "
                    "before adding the other planets."
                ),
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
                content=(
                    "Sign compatibility is a quick way to sense how two people might mesh — useful "
                    "as a first scan, not a final verdict. Real compatibility lives in the full "
                    "charts (synastry), but signs give a fast, intuitive starting point.\n\n"
                    "The most reliable shortcut is elements:\n"
                    "• Same element (e.g., two Fire signs) — easy, instinctive understanding, but can "
                    "lack contrast.\n"
                    "• Complementary elements — Fire + Air feed each other (air fuels fire); Earth + "
                    "Water nourish each other (water shapes earth).\n"
                    "• Challenging mixes — Fire + Water or Earth + Air can clash without effort, but "
                    "also balance each other beautifully when both make room for difference.\n\n"
                    "Modality matters too: two Cardinal signs may both want to lead; two Fixed signs "
                    "may both refuse to budge; two Mutable signs may both struggle to commit.\n\n"
                    "Use sign compatibility to notice the texture of a connection — where it flows "
                    "and where it needs patience. But never write off a pairing on Sun signs alone. "
                    "Two 'incompatible' Suns can be deeply bonded once you look at their Moons, "
                    "Venus, Mars, and the angles between their charts. Signs open the conversation; "
                    "the full chart finishes it."
                ),
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
                content=(
                    "Fire signs — Aries, Leo, and Sagittarius — are the zodiac's spark. They move by "
                    "desire, courage, and momentum, bringing warmth, enthusiasm, and a sense of "
                    "possibility wherever they go.\n\n"
                    "Fire is the element of spirit and action. These signs tend to act first and "
                    "reflect later, lead rather than follow, and inspire others with their "
                    "confidence. At their best they're brave, generous, and motivating; under stress "
                    "they can be impatient, blunt, or burn out by overcommitting.\n\n"
                    "Each Fire sign expresses the flame differently:\n"
                    "• Aries (Cardinal Fire) — the spark of initiation: direct, competitive, "
                    "pioneering. Aries starts things.\n"
                    "• Leo (Fixed Fire) — the steady flame: warm, proud, creative, loyal. Leo "
                    "sustains and radiates.\n"
                    "• Sagittarius (Mutable Fire) — the wandering flame: optimistic, philosophical, "
                    "freedom-loving. Sagittarius expands and explores.\n\n"
                    "If you have strong Fire in your chart, you likely need movement, challenge, and "
                    "room to express yourself; routine and micromanagement drain you. The growth edge "
                    "for Fire is patience — pairing that natural drive with follow-through and "
                    "sensitivity to others. Fire works beautifully with Air (which fuels it) and is "
                    "balanced by Earth and Water."
                ),
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
                content=(
                    "Earth signs — Taurus, Virgo, and Capricorn — are the zodiac's foundation. "
                    "Grounded, practical, and reliable, they turn ideas into tangible results and "
                    "value stability, security, and things that last.\n\n"
                    "Earth is the element of the material world: the body, money, work, and nature. "
                    "These signs trust what they can see, touch, and build. At their best they're "
                    "dependable, patient, and productive; under stress they can become rigid, overly "
                    "cautious, or stuck in materialism.\n\n"
                    "Each Earth sign builds differently:\n"
                    "• Taurus (Fixed Earth) — patient and sensual: values comfort, loyalty, and "
                    "steady progress. Taurus sustains.\n"
                    "• Virgo (Mutable Earth) — precise and improving: analytical, helpful, "
                    "detail-oriented. Virgo refines.\n"
                    "• Capricorn (Cardinal Earth) — ambitious and structured: disciplined, "
                    "strategic, built for the long climb. Capricorn achieves.\n\n"
                    "If Earth is strong in your chart, you likely crave security and tangible "
                    "accomplishment, and you're the person others rely on to get things done. The "
                    "growth edge for Earth is flexibility — staying open to change and to feelings, "
                    "not just facts and plans. Earth pairs naturally with Water (which nourishes it) "
                    "and is energized by Fire and Air."
                ),
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
                content=(
                    "Air signs — Gemini, Libra, and Aquarius — are the zodiac's thinkers and "
                    "connectors. They live in the realm of ideas, language, and relationships, "
                    "thriving on conversation, perspective, and mental stimulation.\n\n"
                    "Air is the element of the mind. These signs gather information, weigh options, "
                    "and connect people and concepts. At their best they're communicative, "
                    "fair-minded, and socially gifted; under stress they can overthink, detach from "
                    "their emotions, or struggle to decide.\n\n"
                    "Each Air sign moves differently:\n"
                    "• Gemini (Mutable Air) — curious and quick: versatile, talkative, endlessly "
                    "interested. Gemini connects ideas.\n"
                    "• Libra (Cardinal Air) — balanced and relational: diplomatic, aesthetic, "
                    "partnership-focused. Libra harmonizes.\n"
                    "• Aquarius (Fixed Air) — original and principled: inventive, independent, "
                    "future-minded. Aquarius reforms.\n\n"
                    "If Air is strong in your chart, you likely need conversation, variety, and "
                    "intellectual freedom, and you process life by talking and thinking it through. "
                    "The growth edge for Air is grounding — landing all those ideas in the body and "
                    "the heart, not just the head. Air feeds Fire and is balanced by Earth and Water."
                ),
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
                content=(
                    "Water signs — Cancer, Scorpio, and Pisces — are the zodiac's emotional depth. "
                    "Intuitive, sensitive, and deeply feeling, they navigate life through emotion and "
                    "connection rather than logic alone.\n\n"
                    "Water is the element of feeling and the unconscious. These signs absorb the "
                    "moods around them, form deep bonds, and often sense things before they can "
                    "explain them. At their best they're empathic, nurturing, and creative; under "
                    "stress they can become moody, over-absorbent of others' pain, or escapist.\n\n"
                    "Each Water sign flows differently:\n"
                    "• Cancer (Cardinal Water) — nurturing and protective: caring, home-loving, "
                    "emotionally intelligent. Cancer shelters.\n"
                    "• Scorpio (Fixed Water) — intense and transformative: passionate, loyal, "
                    "unafraid of depth. Scorpio investigates.\n"
                    "• Pisces (Mutable Water) — compassionate and imaginative: dreamy, artistic, "
                    "spiritually attuned. Pisces dissolves boundaries.\n\n"
                    "If Water is strong in your chart, you likely feel everything deeply and need "
                    "emotional safety, creative outlets, and time to retreat and recharge. The growth "
                    "edge for Water is boundaries — staying open without absorbing everyone else's "
                    "storms. Water nourishes Earth and is balanced by Fire and Air."
                ),
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
