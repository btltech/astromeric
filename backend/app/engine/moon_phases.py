"""
moon_phases.py
--------------
Moon Phase calculations and personalized ritual recommendations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo
import math
from app.interpretation.translations import get_translation

# Moon phase constants
LUNAR_CYCLE_DAYS = 29.530589  # Synodic month in days
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14)  # Known new moon reference

# Zodiac signs in order
ZODIAC_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Element groupings
ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"],
}

# Moon phase names and angles
MOON_PHASES = [
    {"name": "New Moon", "angle_start": 0, "angle_end": 45, "emoji": "🌑"},
    {"name": "Waxing Crescent", "angle_start": 45, "angle_end": 90, "emoji": "🌒"},
    {"name": "First Quarter", "angle_start": 90, "angle_end": 135, "emoji": "🌓"},
    {"name": "Waxing Gibbous", "angle_start": 135, "angle_end": 180, "emoji": "🌔"},
    {"name": "Full Moon", "angle_start": 180, "angle_end": 225, "emoji": "🌕"},
    {"name": "Waning Gibbous", "angle_start": 225, "angle_end": 270, "emoji": "🌖"},
    {"name": "Last Quarter", "angle_start": 270, "angle_end": 315, "emoji": "🌗"},
    {"name": "Waning Crescent", "angle_start": 315, "angle_end": 360, "emoji": "🌘"},
]

# Ritual recommendations by phase
PHASE_RITUALS = {
    "New Moon": {
        "theme": "Planting Seeds",
        "energy": "Intention setting and new beginnings",
        "activities": [
            "Set intentions for the lunar cycle",
            "Start new projects",
            "Create a vision board",
            "Write down goals",
            "Meditate on desires",
        ],
        "avoid": [
            "Major launches (wait for waxing moon)",
            "Harvest activities",
            "Pushing for results",
        ],
        "crystals": ["Black Moonstone", "Labradorite", "Obsidian"],
        "colors": ["Black", "Dark Purple", "Silver"],
        "affirmation": "I plant seeds of intention that will blossom in divine timing.",
    },
    "Waxing Crescent": {
        "theme": "Building Momentum",
        "energy": "Faith and initial action",
        "activities": [
            "Take first steps toward goals",
            "Build on New Moon intentions",
            "Gather resources",
            "Network and connect",
            "Research and learn",
        ],
        "avoid": [
            "Giving up too early",
            "Doubting your path",
        ],
        "crystals": ["Citrine", "Green Aventurine", "Carnelian"],
        "colors": ["Light Green", "Yellow", "Orange"],
        "affirmation": "I take inspired action toward my dreams.",
    },
    "First Quarter": {
        "theme": "Overcoming Challenges",
        "energy": "Decision-making and commitment",
        "activities": [
            "Make important decisions",
            "Push through obstacles",
            "Reassess and adjust plans",
            "Take decisive action",
            "Strengthen resolve",
        ],
        "avoid": [
            "Procrastination",
            "Avoiding necessary confrontations",
        ],
        "crystals": ["Tiger's Eye", "Red Jasper", "Sunstone"],
        "colors": ["Red", "Orange", "Gold"],
        "affirmation": "I commit fully to my chosen path and overcome all obstacles.",
    },
    "Waxing Gibbous": {
        "theme": "Refinement",
        "energy": "Fine-tuning and perseverance",
        "activities": [
            "Refine and polish projects",
            "Make adjustments",
            "Analyze progress",
            "Trust the process",
            "Practice patience",
        ],
        "avoid": [
            "Perfectionism paralysis",
            "Last-minute major changes",
        ],
        "crystals": ["Amethyst", "Fluorite", "Lepidolite"],
        "colors": ["Purple", "Lavender", "Blue"],
        "affirmation": "I trust that my efforts are manifesting perfectly.",
    },
    "Full Moon": {
        "theme": "Culmination",
        "energy": "Manifestation, illumination, release",
        "activities": [
            "Celebrate achievements",
            "Release what no longer serves",
            "Charge crystals",
            "Full Moon ritual bathing",
            "Express gratitude",
            "Forgiveness work",
        ],
        "avoid": [
            "Starting new ventures",
            "Making impulsive decisions",
            "Emotional reactivity",
        ],
        "crystals": ["Clear Quartz", "Selenite", "Moonstone"],
        "colors": ["White", "Silver", "Iridescent"],
        "affirmation": "I celebrate my progress and release what no longer serves my highest good.",
    },
    "Waning Gibbous": {
        "theme": "Gratitude & Sharing",
        "energy": "Reflection and giving back",
        "activities": [
            "Share knowledge and wisdom",
            "Express gratitude",
            "Mentor others",
            "Reflect on lessons learned",
            "Give to charity",
        ],
        "avoid": [
            "Hoarding resources",
            "Ignoring lessons",
        ],
        "crystals": ["Rose Quartz", "Rhodonite", "Green Jade"],
        "colors": ["Pink", "Green", "Peach"],
        "affirmation": "I share my gifts generously and receive with gratitude.",
    },
    "Last Quarter": {
        "theme": "Release & Surrender",
        "energy": "Letting go and clearing",
        "activities": [
            "Release limiting beliefs",
            "Clear physical clutter",
            "Break bad habits",
            "Forgive and let go",
            "Cord-cutting rituals",
        ],
        "avoid": [
            "Starting new projects",
            "Clinging to the past",
        ],
        "crystals": ["Smoky Quartz", "Black Tourmaline", "Apache Tears"],
        "colors": ["Gray", "Brown", "Dark Blue"],
        "affirmation": "I release all that no longer serves my highest good.",
    },
    "Waning Crescent": {
        "theme": "Rest & Renewal",
        "energy": "Surrender and preparation",
        "activities": [
            "Rest and restore",
            "Dream work",
            "Meditation",
            "Prepare for the new cycle",
            "Journaling and reflection",
        ],
        "avoid": [
            "Overexertion",
            "Major decisions",
            "New commitments",
        ],
        "crystals": ["Howlite", "Blue Lace Agate", "Iolite"],
        "colors": ["Light Blue", "White", "Silver"],
        "affirmation": "I rest and restore, preparing for a new beginning.",
    },
}

# Sign-based ritual enhancements
SIGN_RITUAL_FOCUS = {
    "Aries": {
        "theme": "Action & Initiative",
        "focus": "Starting new ventures, physical vitality, courage",
        "body_area": "Head, face",
        "element_boost": "Light candles, work with fire energy",
    },
    "Taurus": {
        "theme": "Stability & Abundance",
        "focus": "Financial matters, sensory pleasures, self-worth",
        "body_area": "Throat, neck",
        "element_boost": "Ground outdoors, work with earth and plants",
    },
    "Gemini": {
        "theme": "Communication & Learning",
        "focus": "Writing, speaking, networking, siblings",
        "body_area": "Arms, hands, lungs",
        "element_boost": "Use incense, breathwork, affirmations",
    },
    "Cancer": {
        "theme": "Home & Nurturing",
        "focus": "Family, emotional healing, home improvements",
        "body_area": "Chest, stomach",
        "element_boost": "Moon water, baths, emotional release",
    },
    "Leo": {
        "theme": "Creativity & Self-Expression",
        "focus": "Creative projects, romance, children, joy",
        "body_area": "Heart, back",
        "element_boost": "Sunbathing, warm colors, creative arts",
    },
    "Virgo": {
        "theme": "Health & Service",
        "focus": "Daily routines, health habits, organization",
        "body_area": "Digestive system",
        "element_boost": "Herbal work, cleaning, practical service",
    },
    "Libra": {
        "theme": "Relationships & Balance",
        "focus": "Partnerships, beauty, justice, harmony",
        "body_area": "Kidneys, lower back",
        "element_boost": "Partner rituals, beautification, balance work",
    },
    "Scorpio": {
        "theme": "Transformation & Depth",
        "focus": "Shadow work, intimacy, shared resources",
        "body_area": "Reproductive organs",
        "element_boost": "Water rituals, deep meditation, release work",
    },
    "Sagittarius": {
        "theme": "Expansion & Adventure",
        "focus": "Travel, higher learning, beliefs, optimism",
        "body_area": "Hips, thighs",
        "element_boost": "Vision quests, philosophical study, outdoor rituals",
    },
    "Capricorn": {
        "theme": "Achievement & Structure",
        "focus": "Career, goals, discipline, authority",
        "body_area": "Bones, knees, skin",
        "element_boost": "Goal-setting, building, practical magic",
    },
    "Aquarius": {
        "theme": "Innovation & Community",
        "focus": "Friendships, technology, humanitarian causes",
        "body_area": "Ankles, circulation",
        "element_boost": "Group rituals, innovation, breaking patterns",
    },
    "Pisces": {
        "theme": "Spirituality & Dreams",
        "focus": "Intuition, dreams, artistic expression, healing",
        "body_area": "Feet",
        "element_boost": "Water rituals, dream work, meditation, music",
    },
}


def calculate_moon_phase(date: datetime = None) -> Dict:
    """
    Calculate the current moon phase.
    Returns phase name, illumination percentage, and days until next phase.
    """
    if date is None:
        date = datetime.now()
    
    # Convert offset-aware datetime to offset-naive for comparison
    if hasattr(date, 'tzinfo') and date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    # Calculate days since known new moon
    diff = date - KNOWN_NEW_MOON
    days_since = diff.total_seconds() / (24 * 3600)
    
    # Calculate phase angle (0-360)
    cycle_position = (days_since % LUNAR_CYCLE_DAYS) / LUNAR_CYCLE_DAYS
    phase_angle = cycle_position * 360
    
    # Calculate illumination (0-100%)
    illumination = round((1 - math.cos(math.radians(phase_angle))) * 50, 1)
    
    # Determine phase name
    phase_info = None
    for phase in MOON_PHASES:
        if phase["angle_start"] <= phase_angle < phase["angle_end"]:
            phase_info = phase
            break
    
    if phase_info is None:
        phase_info = MOON_PHASES[0]  # New Moon (wraps around)
    
    # Calculate days into current phase and days until next
    phase_start_angle = phase_info["angle_start"]
    phase_end_angle = phase_info["angle_end"]
    phase_length_days = (phase_end_angle - phase_start_angle) / 360 * LUNAR_CYCLE_DAYS
    
    days_in_phase = (phase_angle - phase_start_angle) / 360 * LUNAR_CYCLE_DAYS
    days_until_next = phase_length_days - days_in_phase
    
    return {
        "phase_name": phase_info["name"],
        "emoji": phase_info["emoji"],
        "illumination": illumination,
        "phase_angle": round(phase_angle, 1),
        "days_in_phase": round(days_in_phase, 1),
        "days_until_next_phase": round(days_until_next, 1),
        "is_waxing": phase_angle < 180,
        "is_waning": phase_angle >= 180,
    }


def estimate_moon_sign(date: datetime = None) -> str:
    """
    Estimate the Moon's sign based on date.
    Moon changes signs approximately every 2.5 days.
    Note: This is an approximation - for accurate placement use ephemeris.
    """
    if date is None:
        date = datetime.now()
    
    # Convert offset-aware datetime to offset-naive for comparison
    if hasattr(date, 'tzinfo') and date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    # Known Moon position reference (Moon in Aries at midnight)
    reference_date = datetime(2024, 1, 1, 0, 0)
    reference_sign_idx = 0  # Aries
    
    # Moon moves through zodiac in ~27.3 days
    days_diff = (date - reference_date).total_seconds() / (24 * 3600)
    signs_moved = (days_diff / 27.3) * 12
    
    current_sign_idx = int((reference_sign_idx + signs_moved) % 12)
    
    return ZODIAC_ORDER[current_sign_idx]


def get_upcoming_moon_events(days: int = 30) -> List[Dict]:
    """
    Get upcoming New and Full Moons for the next N days.
    """
    events = []
    now = datetime.now()
    
    # Calculate days since known new moon
    diff = now - KNOWN_NEW_MOON
    days_since = diff.total_seconds() / (24 * 3600)
    cycle_position = days_since % LUNAR_CYCLE_DAYS
    
    # Find next New Moon
    days_to_new = LUNAR_CYCLE_DAYS - cycle_position
    if days_to_new <= days:
        new_moon_date = now + timedelta(days=days_to_new)
        events.append({
            "type": "New Moon",
            "date": new_moon_date.strftime("%Y-%m-%d"),
            "emoji": "🌑",
            "days_away": round(days_to_new, 1),
            "sign": estimate_moon_sign(new_moon_date),
        })
    
    # Find next Full Moon
    days_to_full = (LUNAR_CYCLE_DAYS / 2) - cycle_position
    if days_to_full < 0:
        days_to_full += LUNAR_CYCLE_DAYS
    
    if days_to_full <= days:
        full_moon_date = now + timedelta(days=days_to_full)
        events.append({
            "type": "Full Moon",
            "date": full_moon_date.strftime("%Y-%m-%d"),
            "emoji": "🌕",
            "days_away": round(days_to_full, 1),
            "sign": estimate_moon_sign(full_moon_date),
        })
    
    # Sort by days away
    events.sort(key=lambda x: x["days_away"])
    
    return events


def get_personalized_ritual(
    phase_name: str,
    moon_sign: str,
    natal_chart: Optional[Dict] = None,
    personal_day: Optional[int] = None,
    lang: str = "en",
) -> Dict:
    """
    Generate personalized ritual recommendations based on:
    - Current Moon phase
    - Moon's sign
    - Natal chart (if provided)
    - Personal day number (if provided)
    """
    phase_ritual = PHASE_RITUALS.get(phase_name, PHASE_RITUALS["New Moon"])
    sign_focus = SIGN_RITUAL_FOCUS.get(moon_sign, SIGN_RITUAL_FOCUS["Aries"])
    
    # Localize Phase Ritual
    phase_key_base = f"moon_phase_{phase_name.lower().replace(' ', '_')}"
    
    phase_theme_trans = get_translation(lang, f"{phase_key_base}_theme")
    phase_theme = phase_theme_trans[0] if phase_theme_trans else phase_ritual['theme']
    
    phase_energy_trans = get_translation(lang, f"{phase_key_base}_energy")
    phase_energy = phase_energy_trans[0] if phase_energy_trans else phase_ritual['energy']
    
    phase_affirmation_trans = get_translation(lang, f"{phase_key_base}_affirmation")
    phase_affirmation = phase_affirmation_trans[0] if phase_affirmation_trans else phase_ritual['affirmation']

    # Localize Sign Focus
    sign_key_base = f"moon_sign_{moon_sign.lower()}"
    
    sign_theme_trans = get_translation(lang, f"{sign_key_base}_theme")
    sign_theme = sign_theme_trans[0] if sign_theme_trans else sign_focus['theme']
    
    sign_focus_desc_trans = get_translation(lang, f"{sign_key_base}_focus")
    sign_focus_desc = sign_focus_desc_trans[0] if sign_focus_desc_trans else sign_focus['focus']
    
    sign_element_trans = get_translation(lang, f"{sign_key_base}_element")
    sign_element = sign_element_trans[0] if sign_element_trans else sign_focus['element_boost']
    
    sign_body_trans = get_translation(lang, f"{sign_key_base}_body")
    sign_body = sign_body_trans[0] if sign_body_trans else sign_focus['body_area']

    # Combine phase and sign recommendations
    ritual = {
        "phase": phase_name,
        "moon_sign": moon_sign,
        "theme": f"{phase_theme} in {sign_theme}",
        "energy": phase_energy,
        "sign_focus": sign_focus_desc,
        "activities": phase_ritual["activities"][:4],
        "avoid": phase_ritual["avoid"],
        "element_boost": sign_element,
        "body_focus": sign_body,
        "crystals": phase_ritual["crystals"],
        "colors": phase_ritual["colors"],
        "affirmation": phase_affirmation,
    }
    
    # Add personalized natal insights if available
    if natal_chart:
        natal_moon = next(
            (p for p in natal_chart.get("planets", []) if p["name"] == "Moon"),
            None
        )
        if natal_moon:
            natal_moon_sign = natal_moon.get("sign", "")
            if natal_moon_sign == moon_sign:
                insight_trans = get_translation(lang, "moon_insight_return")
                ritual["natal_insight"] = insight_trans[0] if insight_trans else "🌙 Lunar Return: Moon returns to your natal sign - heightened emotional awareness"
            elif natal_moon_sign in ELEMENTS.get(_get_element(moon_sign), []):
                insight_trans = get_translation(lang, "moon_insight_trine")
                ritual["natal_insight"] = insight_trans[0] if insight_trans else "Moon trines your natal Moon - harmonious emotional energy"
    
    # Add numerology insight if personal day provided
    if personal_day:
        pd_key = f"moon_pd_{personal_day}"
        pd_trans = get_translation(lang, pd_key)
        
        if pd_trans:
             ritual["numerology_insight"] = pd_trans[0]
        else:
            day_insights = {
                1: "Amplify leadership in your ritual",
                2: "Include a partner or focus on balance",
                3: "Add creative expression to your practice",
                4: "Structure your ritual carefully",
                5: "Embrace spontaneity in your practice",
                6: "Include family or loved ones",
                7: "Deepen meditation and introspection",
                8: "Focus on abundance and manifestation",
                9: "Include release and forgiveness work",
            }
            ritual["numerology_insight"] = day_insights.get(personal_day, "Trust your intuition")
    
    return ritual


def _get_element(sign: str) -> str:
    """Get element for a zodiac sign."""
    for element, signs in ELEMENTS.items():
        if sign in signs:
            return element
    return "Fire"


def get_moon_phase_summary(
    natal_chart: Optional[Dict] = None,
    numerology: Optional[Dict] = None,
    lang: str = "en",
) -> Dict:
    """
    Get complete moon phase summary with rituals for current phase.
    """
    now = datetime.now()
    phase = calculate_moon_phase(now)
    moon_sign = estimate_moon_sign(now)
    upcoming = get_upcoming_moon_events(30)
    
    # Get personal day if numerology provided
    personal_day = None
    if numerology:
        personal_day = numerology.get("cycles", {}).get("personal_day", {}).get("number")
    
    ritual = get_personalized_ritual(
        phase["phase_name"],
        moon_sign,
        natal_chart,
        personal_day,
        lang=lang,
    )
    
    return {
        "current_phase": phase,
        "moon_sign": moon_sign,
        "ritual": ritual,
        "upcoming_events": upcoming,
    }
