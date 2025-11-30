import hashlib
from datetime import datetime
from typing import Dict, List, Any
from functools import lru_cache
from .astrology import get_zodiac_sign, get_element, get_sign_traits
from .numerology import calculate_life_path_number, calculate_name_number, get_life_path_data


# Pools for different scopes and tracks
LOVE_POOLS = [
    "In matters of the heart, {traits}. Focus on genuine connections.",
    "Romantic energies suggest {traits}. Be open to new possibilities.",
    "Love life benefits from {traits}. Communicate your feelings clearly.",
    "Intimacy grows when you lean into {traits}. Offer steady presence.",
    "Affection deepens through {traits}; choose quality time today."
]

MONEY_POOLS = [
    "Financial prospects involve {traits}. Make informed decisions.",
    "Wealth opportunities arise through {traits}. Stay grounded.",
    "Money matters favor {traits}. Plan for long-term stability.",
    "Prosperity follows {traits}; refine your plan before acting.",
    "Resources respond to {traits}; be disciplined yet open to surprise."
]

CAREER_POOLS = [
    "Professional path enhances with {traits}. Seize opportunities.",
    "Work life thrives on {traits}. Demonstrate your skills.",
    "Career growth comes from {traits}. Stay focused and dedicated.",
    "Authority notices {traits}; let your actions be visible.",
    "Momentum builds through {traits}; prioritize the hard thing first."
]

HEALTH_POOLS = [
    "Wellbeing focuses on {traits}. Prioritize rest and nourishment.",
    "Health energies support {traits}. Listen to your body's signals.",
    "Vitality grows through {traits}; balance activity with recovery.",
]

SPIRITUAL_POOLS = [
    "Personal growth calls for {traits}. Explore inner wisdom.",
    "Spiritual path deepens with {traits}. Trust your intuition.",
    "Enlightenment flows from {traits}; seek meaningful connections.",
]

SCOPE_SUMMARIES = {
    "daily": [
        "Today's cosmic alignment favors {sign} with Life Path {life_path} energy.",
        "A day of {element} influence for {sign}, guided by Life Path {life_path}.",
    ],
    "weekly": [
        "This week's themes revolve around {sign}'s {element} qualities, amplified by Life Path {life_path}.",
        "Over the next 7 days, {sign} energy builds momentum with Life Path {life_path} support.",
    ],
    "monthly": [
        "This month brings {sign}'s {element} essence to the forefront, shaped by Life Path {life_path}.",
        "Big opportunities emerge for {sign} this month, with Life Path {life_path} as your guide.",
    ]
}

TRACK_POOLS = {
    "general": {
        "pools": [
            "Overview: Today's energy supports {traits}. Trust your instincts.",
            "General outlook: Focus on {traits} for best results.",
            "Overall theme: Embrace {traits} to navigate today's path.",
        ],
        "ratings": True
    },
    "love": {
        "pools": LOVE_POOLS,
        "ratings": True
    },
    "money": {
        "pools": MONEY_POOLS,
        "ratings": True
    },
    "health": {
        "pools": [
            "Wellbeing focuses on {traits}. Prioritize rest and nourishment.",
            "Health energies support {traits}. Listen to your body's signals.",
            "Vitality grows through {traits}; balance activity with recovery.",
        ],
        "ratings": True
    },
    "spiritual": {
        "pools": [
            "Personal growth calls for {traits}. Explore inner wisdom.",
            "Spiritual path deepens with {traits}. Trust your intuition.",
            "Enlightenment flows from {traits}; seek meaningful connections.",
        ],
        "ratings": True
    }
}

LOVE_POOLS = [
    "In matters of the heart, {traits}. Focus on genuine connections.",
    "Romantic energies suggest {traits}. Be open to new possibilities.",
    "Love life benefits from {traits}. Communicate your feelings clearly.",
    "Intimacy grows when you lean into {traits}. Offer steady presence.",
    "Affection deepens through {traits}; choose quality time today."
]

MONEY_POOLS = [
    "Financial prospects involve {traits}. Make informed decisions.",
    "Wealth opportunities arise through {traits}. Stay grounded.",
    "Money matters favor {traits}. Plan for long-term stability.",
    "Prosperity follows {traits}; refine your plan before acting.",
    "Resources respond to {traits}; be disciplined yet open to surprise."
]

CAREER_POOLS = [
    "Professional path enhances with {traits}. Seize opportunities.",
    "Work life thrives on {traits}. Demonstrate your skills.",
    "Career growth comes from {traits}. Stay focused and dedicated.",
    "Authority notices {traits}; let your actions be visible.",
    "Momentum builds through {traits}; prioritize the hard thing first."
]

THEME_WORDS = [
    "Resilience", "Harmony", "Creativity", "Stability", "Freedom", "Responsibility",
    "Wisdom", "Power", "Compassion", "Inspiration", "Momentum", "Clarity",
    "Alignment", "Expansion", "Focus", "Equilibrium"
]

ADVICE_POOLS = [
    "Trust your inner guidance today.",
    "Balance action with reflection.",
    "Embrace opportunities with confidence.",
    "Nurture relationships and self-care.",
    "Seek knowledge and apply it wisely.",
    "Let patience shape your choices.",
    "Choose courage over comfort in one key decision.",
    "Simplify one plan before you move forward.",
    "Delegate the noise; keep the signal.",
    "Let curiosity lead one conversation.",
    "Close a lingering loop to free energy."
]

AFFIRMATION_POOLS = [
    "I am aligned with my highest purpose.",
    "Abundance flows to me effortlessly.",
    "I embrace change with courage and grace.",
    "My intuition guides me to the right choices.",
    "I am worthy of love and success.",
    "Every challenge is an opportunity to grow.",
    "I trust the universe's timing.",
    "I radiate positive energy in all I do.",
    "My potential is limitless.",
    "I am the architect of my own destiny.",
    "Clarity comes naturally to me.",
    "I release what no longer serves me.",
    "I welcome new beginnings with open arms.",
    "My inner light shines brightly.",
    "I am grounded, centered, and at peace.",
]

DAILY_ACTIONS = [
    "Write down three things you're grateful for.",
    "Take a 10-minute walk in nature.",
    "Reach out to someone you haven't spoken to recently.",
    "Declutter one small space in your home.",
    "Spend 5 minutes in silent meditation.",
    "Learn one new fact about something that interests you.",
    "Do one thing that scares you (in a good way).",
    "Drink an extra glass of water mindfully.",
    "Compliment a stranger or colleague.",
    "Set one intention for tomorrow before bed.",
    "Review your goals and adjust if needed.",
    "Practice deep breathing for 3 minutes.",
    "Write a short journal entry about today.",
    "Listen to music that uplifts your spirit.",
    "Perform a random act of kindness.",
]

LUCKY_NUMBERS_POOL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, 12, 15, 18, 21, 24, 27, 30]
LUCKY_COLORS_POOL = ["#FF5252", "#448AFF", "#69F0AE", "#FFD740", "#E040FB", "#536DFE", "#05C46B", "#0FB9B1", "#D2DAE2"]

# Simple rising sign approximation by hour bucket (placeholder for deeper astro)
RISING_BY_HOUR = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Cultural/place flavor tags for copy
PLACE_VIBES = [
    "rooted tradition",
    "open horizons",
    "coastal calm",
    "mountain resolve",
    "urban momentum",
    "ancient echoes",
    "creative pulse",
    "river clarity",
    "sunlit optimism",
    "night-sky focus",
    "garden steadiness",
    "crossroads energy",
]

def generate_deterministic_index(seed: str, pool_size: int) -> int:
    """Generate a deterministic index from a seed string."""
    hash_obj = hashlib.md5(seed.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    return hash_int % pool_size

def compute_rising_sign(time_of_birth: str) -> str:
    """Approximate rising sign based on hour bucket (placeholder for real astro)."""
    try:
        # Expect HH:MM or HH:MM:SS
        hour = int(time_of_birth.split(":")[0])
        bucket = (hour // 2) % 12
        return RISING_BY_HOUR[bucket]
    except Exception:
        return ""

def _pick_unique(pool: List[Any], seed: str, count: int, label: str) -> List[Any]:
    """Deterministically pick unique items from a pool."""
    chosen = []
    attempts = 0
    max_attempts = len(pool) * 2  # avoid infinite loops if count > pool
    while len(chosen) < count and attempts < max_attempts:
        idx = generate_deterministic_index(f"{seed}{label}{attempts}", len(pool))
        candidate = pool[idx]
        if candidate not in chosen:
            chosen.append(candidate)
        attempts += 1
    return chosen



@lru_cache(maxsize=4096)
def fuse_prediction(name: str, dob: str, date: str, scope: str = "daily", time_of_birth: str = None, place_of_birth: str = None) -> Dict[str, Any]:
    """Public fused prediction with in-memory LRU caching.

    scope: 'daily', 'weekly', 'monthly'
    """
    return _fuse_prediction(name, dob, date, scope, time_of_birth, place_of_birth)

def _fuse_prediction(name: str, dob: str, date: str, scope: str, time_of_birth: str = None, place_of_birth: str = None) -> Dict[str, Any]:
    """Internal fusion logic for scopes and tracks."""
    sign = get_zodiac_sign(dob)
    element = get_element(sign)
    life_path = calculate_life_path_number(dob)
    name_number = calculate_name_number(name)
    sign_traits = get_sign_traits(sign)
    life_data = get_life_path_data(life_path)

    # Seed includes scope
    seed = f"{name.lower()}{dob}{date}{scope}{time_of_birth or ''}{place_of_birth or ''}"

    # TL;DR summary
    scope_summaries = SCOPE_SUMMARIES.get(scope, SCOPE_SUMMARIES["daily"])
    tldr_idx = generate_deterministic_index(seed + "tldr", len(scope_summaries))
    tldr = scope_summaries[tldr_idx].format(sign=sign, life_path=life_path, element=element)

    # Tracks
    tracks = {}
    ratings = {}
    for track_name, track_data in TRACK_POOLS.items():
        pools = track_data["pools"]
        traits_key = f"{track_name}_traits"
        if track_name in sign_traits:
            traits = sign_traits[track_name][generate_deterministic_index(seed + traits_key, len(sign_traits[track_name]))]
        else:
            traits = sign_traits["general"][generate_deterministic_index(seed + traits_key, len(sign_traits["general"]))]  # fallback

        text_idx = generate_deterministic_index(seed + track_name, len(pools))
        text = pools[text_idx].format(traits=traits)
        tracks[track_name] = text

        if track_data["ratings"]:
            rating = (generate_deterministic_index(seed + f"{track_name}_rating", 5) + 1)
            ratings[track_name] = rating

    # Lucky elements (same as before)
    num_count = 3 + generate_deterministic_index(seed + "num_count", 3)
    lucky_numbers = _pick_unique(LUCKY_NUMBERS_POOL, seed, num_count, "num")
    color_count = 1 + generate_deterministic_index(seed + "color_count", 3)
    lucky_colors = _pick_unique(LUCKY_COLORS_POOL, seed, color_count, "color")
    theme_word = THEME_WORDS[generate_deterministic_index(seed + "theme", len(THEME_WORDS))]
    advice = ADVICE_POOLS[generate_deterministic_index(seed + "advice", len(ADVICE_POOLS))]

    # Rising and place
    rising_sign = compute_rising_sign(time_of_birth) if time_of_birth else ""
    place_vibe = None
    if place_of_birth:
        place_vibe = PLACE_VIBES[generate_deterministic_index(seed + "place", len(PLACE_VIBES))]

    # Affirmation and daily action
    affirmation = AFFIRMATION_POOLS[generate_deterministic_index(seed + "affirmation", len(AFFIRMATION_POOLS))]
    daily_action = DAILY_ACTIONS[generate_deterministic_index(seed + "action", len(DAILY_ACTIONS))]

    return {
        "scope": scope,
        "date": date,
        "tldr": tldr,
        "tracks": tracks,
        "ratings": ratings,
        "lucky": {"numbers": lucky_numbers, "colours": lucky_colors},
        "theme_word": theme_word,
        "advice": advice,
        "affirmation": affirmation,
        "daily_action": daily_action,
        "sign": sign,
        "rising_sign": rising_sign or None,
        "life_path_number": life_path,
        "life_path_meaning": life_data.get("meaning"),
        "life_path_advice": life_data.get("life_advice", advice),
        "name_number": name_number,
        "element": element,
        "place_vibe": place_vibe,
    }
