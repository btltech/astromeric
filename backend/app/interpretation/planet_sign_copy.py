"""
planet_sign_copy.py
--------------------
Concise, track-specific copy for planet-in-sign combinations.

Used by fusion.py to generate richer daily/weekly/monthly reading text
that references the user's actual natal Venus, Mars, Moon, Mercury, etc.
rather than generic Sun-sign traits.

Structure:
  PLANET_SIGN_COPY[planet][sign][track] = list of copy strings
  where track in {"love", "money", "career", "health", "spiritual", "general"}

Each list has 3+ short descriptive phrases (not full sentences — they are
inserted as {traits} into the track pool templates).
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Venus in Sign — love and money flavour
# ---------------------------------------------------------------------------

VENUS_SIGN = {
    "Aries": {
        "love": [
            "bold pursuit",
            "passionate directness",
            "spontaneous affection",
            "fearless romantic initiative",
        ],
        "money": [
            "impulsive spending on desire",
            "first-mover instinct",
            "confident investment decisions",
        ],
        "general": ["fiery warmth", "courageous heart energy"],
    },
    "Taurus": {
        "love": [
            "steadfast devotion",
            "sensual comfort",
            "patient loyalty",
            "pleasure-seeking tenderness",
        ],
        "money": [
            "patient wealth-building",
            "grounded financial instincts",
            "value-over-price discipline",
        ],
        "general": ["earthy affection", "stable and reliable charm"],
    },
    "Gemini": {
        "love": [
            "witty flirtation",
            "intellectual chemistry",
            "curious playfulness",
            "variety in affection",
        ],
        "money": [
            "quick-thinking deals",
            "flexible financial planning",
            "networking for opportunity",
        ],
        "general": ["communicative warmth", "light-hearted social ease"],
    },
    "Cancer": {
        "love": [
            "nurturing devotion",
            "emotional security-seeking",
            "protective tenderness",
            "deep family bonds",
        ],
        "money": [
            "intuitive saving instincts",
            "home-centred investment",
            "cautious financial care",
        ],
        "general": ["empathetic warmth", "heartfelt loyalty"],
    },
    "Leo": {
        "love": [
            "generous adoration",
            "dramatic romance",
            "loyal lionhearted devotion",
            "celebratory affection",
        ],
        "money": [
            "bold spending on quality",
            "generous gifting",
            "attraction of abundance through confidence",
        ],
        "general": ["radiant magnetism", "warm-hearted generosity"],
    },
    "Virgo": {
        "love": [
            "thoughtful service",
            "practical caring",
            "detail-oriented devotion",
            "sincere helpfulness",
        ],
        "money": [
            "meticulous budgeting",
            "quality over quantity",
            "careful analytical finance",
        ],
        "general": ["quiet, steady affection", "refined discriminating taste"],
    },
    "Libra": {
        "love": [
            "harmonious partnership",
            "graceful romance",
            "seeking beauty in connection",
            "fair and balanced affection",
        ],
        "money": [
            "balanced financial decisions",
            "aesthetic investment",
            "partnership-driven prosperity",
        ],
        "general": ["diplomatic charm", "elegant social grace"],
    },
    "Scorpio": {
        "love": [
            "intense passionate bonding",
            "transformative intimacy",
            "all-or-nothing devotion",
            "magnetic depth",
        ],
        "money": [
            "strategic resource management",
            "deep financial research",
            "calculated risk for transformation",
        ],
        "general": ["penetrating magnetism", "powerful emotional depth"],
    },
    "Sagittarius": {
        "love": [
            "adventurous freedom in love",
            "philosophical connection",
            "spontaneous romance",
            "expansive affection",
        ],
        "money": [
            "optimistic risk-taking",
            "global opportunity seeking",
            "big-picture financial vision",
        ],
        "general": ["joyful open-hearted energy", "adventurous enthusiasm"],
    },
    "Capricorn": {
        "love": [
            "committed long-term devotion",
            "responsible partnership",
            "steady reliable affection",
            "ambitious loyalty",
        ],
        "money": [
            "disciplined wealth strategy",
            "long-term investment patience",
            "structured financial planning",
        ],
        "general": ["grounded mature warmth", "reliable enduring charm"],
    },
    "Aquarius": {
        "love": [
            "unconventional connection",
            "friendship-rooted love",
            "progressive open-minded affection",
            "intellectual bonds",
        ],
        "money": [
            "innovative financial thinking",
            "community-minded investment",
            "tech-forward opportunity spotting",
        ],
        "general": ["unique independent magnetism", "humanitarian warmth"],
    },
    "Pisces": {
        "love": [
            "dreamy romantic idealism",
            "compassionate merging",
            "spiritual soulmate seeking",
            "selfless devotion",
        ],
        "money": [
            "intuitive financial flow",
            "generous spirit with resources",
            "imaginative creative income",
        ],
        "general": ["soft boundless empathy", "ethereal romantic energy"],
    },
}

# ---------------------------------------------------------------------------
# Mars in Sign — career and energy flavour
# ---------------------------------------------------------------------------

MARS_SIGN = {
    "Aries": {
        "career": [
            "bold pioneering initiative",
            "competitive drive",
            "fearless leadership",
            "urgent decisive action",
        ],
        "health": [
            "high physical energy",
            "vigorous athletic drive",
            "need to burn intensity through movement",
        ],
        "general": ["raw powerful force", "courageous direct action"],
    },
    "Taurus": {
        "career": [
            "steady persistent effort",
            "patient methodical progress",
            "determined resource-building",
            "finishing what you start",
        ],
        "health": [
            "physical endurance",
            "slow-burning stamina",
            "sensory body awareness",
        ],
        "general": ["deliberate powerful momentum", "grounded tenacious will"],
    },
    "Gemini": {
        "career": [
            "versatile multi-tasking energy",
            "sharp communicative drive",
            "quick adaptive thinking",
            "idea-to-action speed",
        ],
        "health": [
            "restless mental-physical energy",
            "variety in movement",
            "need for mental stimulation alongside exercise",
        ],
        "general": ["quick-witted agile energy", "intellectually driven action"],
    },
    "Cancer": {
        "career": [
            "protective motivated effort",
            "emotionally invested work",
            "intuitive strategic moves",
            "family-driven ambition",
        ],
        "health": [
            "emotionally linked physical wellbeing",
            "rest and nurture cycles",
            "gut-instinct body signals",
        ],
        "general": ["defensive fierce protection", "emotionally fuelled drive"],
    },
    "Leo": {
        "career": [
            "dramatic bold performance",
            "confident visible leadership",
            "creative ambitious drive",
            "desire to be recognised",
        ],
        "health": [
            "heart-centred vitality",
            "energetic showmanship",
            "need for joy in movement",
        ],
        "general": ["radiant powerful will", "charismatic commanding energy"],
    },
    "Virgo": {
        "career": [
            "precision-driven diligence",
            "analytical productive effort",
            "improvement-focused work ethic",
            "meticulous task mastery",
        ],
        "health": [
            "health-conscious routine discipline",
            "body-mind attunement",
            "systematic wellness habits",
        ],
        "general": ["efficient purposeful energy", "perfecting critical drive"],
    },
    "Libra": {
        "career": [
            "diplomatically strategic moves",
            "collaborative action",
            "seeking fairness in competition",
            "partnership-driven initiative",
        ],
        "health": [
            "balance-seeking physical harmony",
            "moderate consistent activity",
            "beauty and body alignment",
        ],
        "general": ["charming persuasive action", "socially calibrated drive"],
    },
    "Scorpio": {
        "career": [
            "relentless investigative drive",
            "transformative strategic power",
            "deep penetrating focus",
            "unstoppable regenerative will",
        ],
        "health": [
            "intense regenerative capacity",
            "all-or-nothing physical cycles",
            "deep healing potential",
        ],
        "general": ["volcanic controlled power", "magnetic unstoppable force"],
    },
    "Sagittarius": {
        "career": [
            "expansive optimistic drive",
            "philosophical goal-setting",
            "adventurous risk-taking",
            "freedom-seeking ambition",
        ],
        "health": [
            "outdoor active energy",
            "expansive movement needs",
            "philosophical approach to wellness",
        ],
        "general": ["enthusiastic far-reaching energy", "bold adventurous force"],
    },
    "Capricorn": {
        "career": [
            "disciplined structured ambition",
            "patient long-game strategy",
            "authority-building resolve",
            "status-driven focused effort",
        ],
        "health": [
            "disciplined body maintenance",
            "endurance through challenge",
            "bone and joint attentiveness",
        ],
        "general": [
            "relentless focused determination",
            "authoritative commanding will",
        ],
    },
    "Aquarius": {
        "career": [
            "innovative rebellious drive",
            "team-oriented action",
            "future-forward initiative",
            "progressive disruptive energy",
        ],
        "health": [
            "unconventional wellness approaches",
            "collective energetic synergy",
            "circulation and nervous system focus",
        ],
        "general": ["electric unpredictable force", "humanitarian revolutionary drive"],
    },
    "Pisces": {
        "career": [
            "fluid adaptive effort",
            "compassion-driven work",
            "intuitive creative action",
            "behind-the-scenes strategic moves",
        ],
        "health": [
            "sensitive psychic body awareness",
            "fluid movement and flow",
            "emotional-physical boundary care",
        ],
        "general": ["dissolving effortless action", "spiritually channelled drive"],
    },
}

# ---------------------------------------------------------------------------
# Moon in Sign — health, spiritual, emotional flavour
# ---------------------------------------------------------------------------

MOON_SIGN = {
    "Aries": {
        "health": [
            "instinctive gut-driven wellbeing",
            "quick emotional recovery",
            "need for physical release of feelings",
        ],
        "spiritual": [
            "spontaneous spiritual impulses",
            "warrior-faith in the moment",
            "fresh starts renewing the soul",
        ],
        "general": ["fiery emotional immediacy", "bold instinctive responses"],
    },
    "Taurus": {
        "health": [
            "sensory self-care rituals",
            "comfort and routine for stability",
            "physical grounding for emotional security",
        ],
        "spiritual": [
            "earth-based contemplative practice",
            "steadfast faith through sensation",
            "patient spiritual deepening",
        ],
        "general": [
            "calm reliable emotional anchor",
            "nourishing self-sustaining instincts",
        ],
    },
    "Gemini": {
        "health": [
            "mental-emotional dialogue awareness",
            "need for stimulating variety",
            "light adaptive nervous system care",
        ],
        "spiritual": [
            "curiosity as spiritual path",
            "multiple perspectives on the sacred",
            "learning as devotion",
        ],
        "general": [
            "quick-shifting emotional weather",
            "intellectually processed feelings",
        ],
    },
    "Cancer": {
        "health": [
            "nurturing emotional self-care",
            "home comfort as medicine",
            "gut-intuition body signals",
        ],
        "spiritual": [
            "ancestral and lineage connection",
            "moon cycle attunement",
            "home as sacred temple",
        ],
        "general": ["deep empathic emotional tides", "protective nurturing instincts"],
    },
    "Leo": {
        "health": [
            "heart-centred joyful living",
            "creative expression for wellbeing",
            "need for recognition boosting vitality",
        ],
        "spiritual": [
            "solar devotional practice",
            "creative expression as prayer",
            "bold authentic soul expression",
        ],
        "general": ["warm generous emotional radiance", "dramatic heartfelt instincts"],
    },
    "Virgo": {
        "health": [
            "analytical wellness routines",
            "diet and body awareness",
            "service and usefulness for emotional peace",
        ],
        "spiritual": [
            "ritual-based practice",
            "sacred ordinary daily acts",
            "discernment as spiritual gift",
        ],
        "general": [
            "careful discriminating emotional instincts",
            "helpful modest inner world",
        ],
    },
    "Libra": {
        "health": [
            "relational harmony for wellbeing",
            "aesthetic beauty as medicine",
            "balance-seeking body routines",
        ],
        "spiritual": [
            "beauty as spiritual path",
            "partnership in sacred practice",
            "seeking divine balance",
        ],
        "general": [
            "emotionally harmonising instincts",
            "peace-seeking relational needs",
        ],
    },
    "Scorpio": {
        "health": [
            "deep regenerative healing capacity",
            "emotional purging for vitality",
            "psycho-somatic body awareness",
        ],
        "spiritual": [
            "shadow integration as spiritual path",
            "death-rebirth transformation",
            "depth mysticism",
        ],
        "general": [
            "intense penetrating emotional depths",
            "powerful regenerative instincts",
        ],
    },
    "Sagittarius": {
        "health": [
            "movement and freedom for wellbeing",
            "optimistic mindset as medicine",
            "outdoor expansive physical care",
        ],
        "spiritual": [
            "philosophical spiritual seeking",
            "travel as pilgrimage",
            "expanding belief horizons",
        ],
        "general": [
            "adventurous freedom-loving emotional nature",
            "joyful optimistic instincts",
        ],
    },
    "Capricorn": {
        "health": [
            "structured disciplined self-care",
            "long-term health strategy",
            "emotional restraint and mastery",
        ],
        "spiritual": [
            "duty as devotion",
            "elder wisdom traditions",
            "climbing toward mastery as spiritual path",
        ],
        "general": [
            "reserved emotionally self-sufficient instincts",
            "practical cautious inner world",
        ],
    },
    "Aquarius": {
        "health": [
            "community and social connection for wellbeing",
            "detached analytical health awareness",
            "unconventional wellness experiments",
        ],
        "spiritual": [
            "collective consciousness connection",
            "humanitarian spiritual vision",
            "awakening as spiritual path",
        ],
        "general": [
            "cool independent emotional detachment",
            "future-oriented progressive instincts",
        ],
    },
    "Pisces": {
        "health": [
            "fluid restorative rest needs",
            "spiritual emotional boundaries",
            "water and intuitive body healing",
        ],
        "spiritual": [
            "mystical dissolution practice",
            "compassion as spiritual foundation",
            "dream and vision attunement",
        ],
        "general": [
            "boundless empathic emotional sea",
            "psychic dreamlike inner world",
        ],
    },
}

# ---------------------------------------------------------------------------
# Transit aspect interpretation phrases
# Keyed by (transiting_planet, aspect_type, natal_planet)
# aspect_type: "conjunction" | "opposition" | "trine" | "square" | "sextile"
# ---------------------------------------------------------------------------

# Transiting planet keywords for injection
TRANSIT_PLANET_KEYWORDS = {
    "Sun": "solar confidence and vitality",
    "Moon": "emotional sensitivity and instinct",
    "Mercury": "mental clarity and communication",
    "Venus": "harmony, attraction, and pleasure",
    "Mars": "drive, assertion, and energy",
    "Jupiter": "expansion, opportunity, and optimism",
    "Saturn": "discipline, structure, and lessons",
    "Uranus": "sudden change and awakening",
    "Neptune": "inspiration, intuition, and dissolution",
    "Pluto": "deep transformation and power",
}

TRANSIT_NATAL_KEYWORDS = {
    "Sun": "core identity and purpose",
    "Moon": "emotional needs and instincts",
    "Mercury": "thoughts and communication style",
    "Venus": "values, love, and pleasure",
    "Mars": "drive and personal will",
    "Jupiter": "sense of abundance and philosophy",
    "Saturn": "discipline and responsibilities",
    "Ascendant": "outer self and first impressions",
    "Midheaven": "career direction and public reputation",
}

ASPECT_FLAVOUR = {
    "conjunction": "merging with and intensifying",
    "trine": "flowing harmoniously to support",
    "sextile": "opening opportunities through",
    "square": "challenging and activating",
    "opposition": "creating dynamic tension with",
}

TRACK_TRANSIT_RELEVANCE = {
    # transit planet → relevant tracks
    "Sun": ["general", "career"],
    "Moon": ["health", "spiritual"],
    "Mercury": ["general", "career"],
    "Venus": ["love", "money"],
    "Mars": ["career", "health"],
    "Jupiter": ["money", "spiritual"],
    "Saturn": ["career", "money"],
    "Uranus": ["general", "career"],
    "Neptune": ["spiritual", "love"],
    "Pluto": ["spiritual", "general"],
}


def get_planet_sign_traits(planet: str, sign: str, track: str) -> List[str]:
    """
    Return copy traits for a planet in a sign for a given track.
    Falls back to general if specific track not found.
    """
    lookup: Dict = {}
    if planet == "Venus":
        lookup = VENUS_SIGN.get(sign, {})
    elif planet == "Mars":
        lookup = MARS_SIGN.get(sign, {})
    elif planet == "Moon":
        lookup = MOON_SIGN.get(sign, {})

    return lookup.get(track) or lookup.get("general") or []


def build_transit_sentence(
    transit_planet: str,
    aspect: str,
    natal_planet: str,
    orb: float,
) -> str:
    """
    Build a human-readable transit sentence for use in daily readings.
    """
    n_kw = TRANSIT_NATAL_KEYWORDS.get(natal_planet, f"natal {natal_planet.lower()}")
    asp_flavour = ASPECT_FLAVOUR.get(aspect, "aspecting")
    orb_str = f"({orb:.1f}° orb)" if orb < 2.0 else ""
    return f"{transit_planet} {asp_flavour} your {n_kw} {orb_str}".strip()
