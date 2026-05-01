import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.interpretation.translations import get_translation

try:
    import redis
except ImportError:
    redis = None

from .astrology import get_element, get_sign_traits, get_zodiac_sign
from .numerology import (
    calculate_life_path_number,
    calculate_name_number,
    get_life_path_data,
)

# Pools for different scopes and tracks
LOVE_POOLS = [
    "Your capacity for {traits} is your greatest romantic asset right now — let it lead.",
    "Love opens wider when you bring {traits} into how you show up for others.",
    "Intimacy deepens through {traits} today; small gestures carry lasting weight.",
    "Romance responds to your {traits} energy — authenticity is more magnetic than perfection.",
    "Connection blooms where {traits} meets real vulnerability. Be seen.",
    "Your {traits} draws people closer; don't second-guess what feels natural.",
    "Relationships grow when {traits} guides your words rather than just your actions.",
    "The heart wants what resonates — your {traits} knows the way.",
]

MONEY_POOLS = [
    "Your {traits} is the financial edge others don't have — use it deliberately.",
    "Wealth follows the path of {traits} right now; trust the slow build.",
    "Money flows toward {traits}; resist shortcuts that bypass your instincts.",
    "Financial clarity comes from leaning into {traits} rather than hedging every move.",
    "Resources respond to {traits}; one disciplined decision today compounds forward.",
    "Prosperity is a practice — your {traits} is showing you exactly where to focus.",
    "The gap between planning and earning closes when you apply {traits} consistently.",
    "An opportunity may look small but carry real weight — {traits} helps you see it.",
]

CAREER_POOLS = [
    "Your {traits} is visible to the right people right now — let it speak.",
    "Professional momentum builds where {traits} meets consistent follow-through.",
    "Ambition sharpens when you channel {traits} into the next concrete step.",
    "Work rewards {traits} right now; don't dilute your effort across too many fronts.",
    "Career growth lives at the intersection of {traits} and timing — today both align.",
    "The work that feels most authentic to your {traits} is also the work that stands out.",
    "Step into the harder conversation or the harder project — {traits} makes you ready.",
    "Authority and recognition come naturally to your {traits} when you stop holding back.",
]

HEALTH_POOLS = [
    "Your body is communicating through {traits} — listen before you push harder.",
    "Vitality returns when you align with {traits} rather than override it.",
    "Wellbeing deepens through {traits} today; recovery is part of the work.",
    "Energy is renewable when you honor {traits}; force drains what rest replenishes.",
    "Your {traits} holds the key to what your body actually needs right now.",
    "Small rituals rooted in {traits} compound into real physical resilience.",
    "Movement and stillness both have a role; {traits} tells you which one today.",
]

SPIRITUAL_POOLS = [
    "Your {traits} is the doorway to the inner work available right now.",
    "Spiritual growth moves at the pace of {traits} — don't rush what is unfolding.",
    "Inner clarity arrives when you stop explaining {traits} and start inhabiting it.",
    "The practice isn't complicated — your {traits} already knows the direction.",
    "What you seek is seeking you; {traits} is how you stay receptive.",
    "Meaning reveals itself at the edge of {traits}; lean toward the quiet.",
    "Your {traits} connects you to something larger than the moment demands.",
    "The day holds more depth than it appears — {traits} helps you find it.",
]

SCOPE_SUMMARIES = {
    "daily": [
        "Today's cosmic alignment favors {sign} with Life Path {life_path} energy.",
        "A day of {element} influence for {sign}, guided by Life Path {life_path}.",
        "{sign} energy is active today — Life Path {life_path} shapes how it lands.",
    ],
    "weekly": [
        "This week's themes revolve around {sign}'s {element} qualities, amplified by Life Path {life_path}.",
        "Over the next 7 days, {sign} energy builds momentum with Life Path {life_path} support.",
        "A {element} week ahead — {sign} steady-states with Life Path {life_path} in the background.",
    ],
    "monthly": [
        "This month brings {sign}'s {element} essence to the forefront, shaped by Life Path {life_path}.",
        "Big opportunities emerge for {sign} this month, with Life Path {life_path} as your guide.",
        "Long-range {element} themes deepen for {sign} — Life Path {life_path} holds the thread.",
    ],
}

TRACK_POOLS = {
    "general": {
        "pools": [
            "Your {traits} is the throughline of today — follow where it leads.",
            "The day opens around your {traits}; don't talk yourself out of what feels clear.",
            "Everything sharpens when you trust your {traits} rather than override it.",
            "Today's energy bends toward {traits}; you'll feel it in the choices that matter.",
            "Your {traits} gives you an edge right now — use it, don't explain it.",
        ],
        "ratings": True,
    },
    "love": {"pools": LOVE_POOLS, "ratings": True},
    "money": {"pools": MONEY_POOLS, "ratings": True},
    "career": {"pools": CAREER_POOLS, "ratings": True},
    "health": {"pools": HEALTH_POOLS, "ratings": True},
    "spiritual": {"pools": SPIRITUAL_POOLS, "ratings": True},
}

THEME_WORDS = [
    "Resilience",
    "Harmony",
    "Creativity",
    "Stability",
    "Freedom",
    "Responsibility",
    "Wisdom",
    "Power",
    "Compassion",
    "Inspiration",
    "Momentum",
    "Clarity",
    "Alignment",
    "Expansion",
    "Focus",
    "Equilibrium",
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
    "Close a lingering loop to free energy.",
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

REDIS_URL = os.getenv("REDIS_URL")
FUSION_CACHE_TTL = int(os.getenv("FUSION_CACHE_TTL", "86400"))
_redis_client = None


def _seconds_until_midnight() -> int:
    """Returns seconds remaining until UTC midnight — used to expire daily caches at day boundary."""
    now = datetime.now(timezone.utc)
    next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta

    next_midnight += timedelta(days=1)
    return max(60, int((next_midnight - now).total_seconds()))


LUCKY_NUMBERS_POOL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, 12, 15, 18, 21, 24, 27, 30]
LUCKY_COLORS_POOL = [
    "#FF5252",
    "#448AFF",
    "#69F0AE",
    "#FFD740",
    "#E040FB",
    "#536DFE",
    "#05C46B",
    "#0FB9B1",
    "#D2DAE2",
]

# Simple rising sign approximation by hour bucket (placeholder for deeper astro)
RISING_BY_HOUR = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
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


def compute_rising_sign(
    time_of_birth: str,
    dob: str = None,
    latitude: float = None,
    longitude: float = None,
) -> str:
    """Compute the true Ascendant (rising sign) using the flatlib ephemeris.

    Requires birth time, date, latitude and longitude for an accurate result.
    Falls back to a rough hour-bucket estimate when flatlib is unavailable or
    location data is missing — this fallback is clearly imprecise (±1 sign) and
    should only trigger for users who have not provided birth location.
    """
    # --- Attempt real calculation via flatlib ---
    try:
        if dob and latitude is not None and longitude is not None and time_of_birth:
            from flatlib import const as fl_const
            from flatlib.chart import Chart as FLChart
            from flatlib.datetime import Datetime as FLDatetime
            from flatlib.geopos import GeoPos

            # Parse date
            parts = dob.split("-")
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

            # Parse time — accept HH:MM or HH:MM:SS
            t_parts = time_of_birth.split(":")
            hour = int(t_parts[0])
            minute = int(t_parts[1]) if len(t_parts) > 1 else 0

            # flatlib uses "+HH:MM" UTC offset; assume UTC when we don't have tz
            fl_dt = FLDatetime(
                f"{year}/{month:02d}/{day:02d}", f"{hour:02d}:{minute:02d}", "+00:00"
            )
            fl_pos = GeoPos(str(latitude), str(longitude))
            fl_chart = FLChart(fl_dt, fl_pos)

            # House 1 cusp = Ascendant
            asc = fl_chart.get(fl_const.ASC)
            return asc.sign
    except Exception:
        pass  # Fall through to stub

    # --- Stub fallback (hour-bucket approximation) ---
    # This is intentionally imprecise — it only activates when flatlib fails or
    # birth location is unavailable. It is NOT presented as accurate.
    try:
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


def get_localized_pool(pool_name: str, default_pool: List[str], lang: str) -> List[str]:
    """Get localized pool content."""
    if lang == "en":
        return default_pool

    localized_pool = []
    for i, item in enumerate(default_pool):
        key = f"fusion_{pool_name}_{i}"
        translated = get_translation(lang, "fusion_content", key)
        localized_pool.append(translated if translated else item)
    return localized_pool


def fuse_prediction(
    name: str,
    dob: str,
    date: str,
    scope: str = "daily",
    time_of_birth: str = None,
    place_of_birth: str = None,
    latitude: float = None,
    longitude: float = None,
    lang: str = "en",
) -> Dict[str, Any]:
    """Public fused prediction with optional Redis caching.

    Daily scope TTL expires at UTC midnight so each day's reading is fresh.
    Weekly/monthly scope use the configured FUSION_CACHE_TTL.
    """
    cache_client = _get_redis_client()
    cache_key = _fusion_cache_key(
        name, dob, date, scope, time_of_birth, place_of_birth, lang
    )
    if cache_client:
        cached = cache_client.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                cache_client.delete(cache_key)

    result = _fuse_prediction(
        name, dob, date, scope, time_of_birth, place_of_birth, latitude, longitude, lang
    )
    if cache_client:
        # Daily readings expire at midnight so tomorrow's reading is always fresh.
        # Weekly/monthly readings use the configured TTL.
        ttl = _seconds_until_midnight() if scope == "daily" else FUSION_CACHE_TTL
        cache_client.setex(cache_key, ttl, json.dumps(result))
    return result


def _fuse_prediction(
    name: str,
    dob: str,
    date: str,
    scope: str,
    time_of_birth: str = None,
    place_of_birth: str = None,
    latitude: float = None,
    longitude: float = None,
    lang: str = "en",
) -> Dict[str, Any]:
    """Internal fusion logic for scopes and tracks."""
    sign = get_zodiac_sign(dob)
    element = get_element(sign)

    # Localize element for display
    element_display = element
    if lang != "en":
        element_display = get_translation(lang, "elements", element) or element

    life_path = calculate_life_path_number(dob)
    name_number = calculate_name_number(name)
    sign_traits = get_sign_traits(sign, lang=lang)
    life_data = get_life_path_data(life_path, lang=lang)

    # Seed includes scope
    seed = (
        f"{name.lower()}{dob}{date}{scope}{time_of_birth or ''}{place_of_birth or ''}"
    )

    # --- Phase 5: Pull real natal chart context ---
    chart_ctx = _get_chart_context(
        dob=dob,
        time_of_birth=time_of_birth,
        latitude=latitude,
        longitude=longitude,
    )

    # --- Fix 1: Transit positions and aspects for daily scope ---
    active_transits: List[Dict] = []
    transit_narrative: str = ""
    if scope == "daily" and date:
        transit_positions = _get_transit_positions(date)
        if transit_positions and chart_ctx:
            # Build natal absolute-degree map from chart_ctx sign→midpoint (rough)
            # For a richer version we need actual natal degrees; use what we have
            try:
                from ..chart_service import build_natal_chart as _bnc

                _natal_profile = {
                    "date_of_birth": dob,
                    "time_of_birth": time_of_birth or "12:00",
                    "latitude": latitude or 0.0,
                    "longitude": longitude or 0.0,
                    "timezone": "UTC",
                }
                _natal_chart = _bnc(_natal_profile)
                _natal_planets = {
                    p["name"]: float(p.get("absolute_degree", 0))
                    for p in _natal_chart.get("planets", [])
                }
                _natal_points = {
                    p["name"]: float(p.get("absolute_degree", 0))
                    for p in _natal_chart.get("points", [])
                }
                _natal_positions = {**_natal_planets, **_natal_points}
            except Exception:
                _natal_positions = {}

            if _natal_positions:
                aspects = _find_transit_aspects(transit_positions, _natal_positions)
                best = _pick_best_transit(aspects)
                if best:
                    from app.interpretation.planet_sign_copy import (
                        build_transit_sentence,
                    )

                    transit_narrative = build_transit_sentence(
                        best["transit_planet"],
                        best["aspect"],
                        best["natal_planet"],
                        best["orb"],
                    )
                    active_transits = aspects[:5]  # top 5 tightest

    # Map tracks to the most astrologically relevant natal planet
    _track_planet: Dict[str, str] = {
        "love": chart_ctx.get("venus_sign") or sign,
        "money": chart_ctx.get("venus_sign") or sign,
        "career": chart_ctx.get("mars_sign") or sign,
        "health": chart_ctx.get("moon_sign") or sign,
        "spiritual": chart_ctx.get("moon_sign") or sign,
        "general": sign,
    }

    # Detect retrograde planets from today's transit positions
    _retrograde_planets: List[str] = []
    if scope == "daily" and date and transit_positions:
        try:
            from flatlib import const as _fl_const
            from flatlib.chart import Chart as _FLChart
            from flatlib.datetime import Datetime as _FLDt
            from flatlib.geopos import GeoPos as _GeoPos

            _dt = _FLDt(date.replace("-", "/"), "12:00", "+00:00")
            _pos = _GeoPos("0n00", "0e00")
            _tc = _FLChart(_dt, _pos)
            for _pname in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                try:
                    _obj = _tc.get(getattr(_fl_const, _pname.upper()))
                    if _obj and _obj.movement() == _fl_const.RETROGRADE:
                        _retrograde_planets.append(_pname)
                except Exception:
                    pass
        except Exception:
            pass

    # Moon phase for daily scope
    _moon_phase_name: str = ""
    _moon_phase_emoji: str = ""
    if scope == "daily" and date:
        try:
            from .moon_phases import calculate_moon_phase as _cmp

            _mp = _cmp(datetime.fromisoformat(date))
            _moon_phase_name = _mp.get("phase", "")
            _moon_phase_emoji = _mp.get("emoji", "")
        except Exception:
            pass

    # TL;DR summary — try enriched version first
    enriched_tldr = _chart_enriched_tldr(
        sign, life_path, element_display, chart_ctx, scope, seed
    )
    if not enriched_tldr:
        scope_summaries = SCOPE_SUMMARIES.get(scope, SCOPE_SUMMARIES["daily"])
        scope_summaries = get_localized_pool(f"scope_{scope}", scope_summaries, lang)
        tldr_idx = generate_deterministic_index(seed + "tldr", len(scope_summaries))
        enriched_tldr = scope_summaries[tldr_idx].format(
            sign=sign, life_path=life_path, element=element_display
        )
    # Append transit narrative for daily scope when available
    if transit_narrative:
        tldr = f"{enriched_tldr} {transit_narrative}."
    else:
        tldr = enriched_tldr

    # Prepend moon phase to tldr for daily scope
    if _moon_phase_name and scope == "daily":
        phase_str = f"{_moon_phase_emoji} {_moon_phase_name}".strip()
        tldr = f"{phase_str}. {tldr}"

    # Append progressed Sun context for daily scope
    if scope == "daily" and dob and date:
        try:
            from ..chart_service import build_progressed_chart as _bpc

            _prog_profile = {
                "date_of_birth": dob,
                "time_of_birth": time_of_birth or "12:00",
                "latitude": latitude or 0.0,
                "longitude": longitude or 0.0,
                "timezone": "UTC",
            }
            _prog_chart = _bpc(_prog_profile, date)
            _prog_sun = next(
                (p for p in _prog_chart.get("planets", []) if p["name"] == "Sun"),
                None,
            )
            _prog_moon = next(
                (p for p in _prog_chart.get("planets", []) if p["name"] == "Moon"),
                None,
            )
            prog_sun_sign = _prog_sun.get("sign") if _prog_sun else None
            prog_moon_sign = _prog_moon.get("sign") if _prog_moon else None
            if prog_sun_sign and prog_sun_sign != sign:
                prog_note = f"Your progressed Sun is in {prog_sun_sign}"
                if prog_moon_sign and prog_moon_sign != chart_ctx.get("moon_sign"):
                    prog_note += f", progressed Moon in {prog_moon_sign}"
                tldr = f"{tldr} {prog_note}."
            elif prog_moon_sign and prog_moon_sign != chart_ctx.get("moon_sign"):
                tldr = f"{tldr} Progressed Moon in {prog_moon_sign}."
        except Exception:
            pass  # progressions are enhancement only

    # Tracks
    tracks = {}
    ratings = {}
    # planet name per track (for richer copy lookup)
    _track_planet_name: Dict[str, str] = {
        "love": "Venus",
        "money": "Venus",
        "career": "Mars",
        "health": "Moon",
        "spiritual": "Moon",
        "general": "Sun",
    }
    try:
        from app.interpretation.planet_sign_copy import ASPECT_FLAVOUR as _asp_flavour
        from app.interpretation.planet_sign_copy import TRACK_TRANSIT_RELEVANCE as _ttr
        from app.interpretation.planet_sign_copy import get_planet_sign_traits as _pst

        _has_pst = True
    except Exception:
        _has_pst = False
        _ttr = {}
        _asp_flavour = {}

    for track_name, track_data in TRACK_POOLS.items():
        pools = get_localized_pool(f"track_{track_name}", track_data["pools"], lang)

        # Use the planet-specific sign's traits when available
        planet_sign = _track_planet.get(track_name, sign)
        planet_name_for_track = _track_planet_name.get(track_name, "Sun")

        # Fix 4: try richer planet-in-sign copy first
        trait_pool: List[str] = []
        if _has_pst:
            trait_pool = _pst(planet_name_for_track, planet_sign, track_name)

        # Fall back to existing get_sign_traits mechanism
        if not trait_pool:
            planet_traits = (
                get_sign_traits(planet_sign, lang=lang)
                if planet_sign != sign
                else sign_traits
            )
            traits_key = f"{track_name}_traits"
            if track_name in planet_traits:
                trait_pool = planet_traits[track_name]
            elif "general" in planet_traits:
                trait_pool = planet_traits["general"]
            else:
                trait_pool = sign_traits.get("general", ["adaptable energy"])

        if not trait_pool:
            trait_pool = sign_traits.get("general", ["adaptable energy"])

        traits_key = f"{track_name}_traits"
        traits = trait_pool[
            generate_deterministic_index(seed + traits_key, len(trait_pool))
        ]

        text_idx = generate_deterministic_index(seed + track_name, len(pools))
        text = pools[text_idx].format(traits=traits)

        # Inject transit note when a relevant transit is active for this track
        if active_transits and _ttr:
            relevant = [
                t
                for t in active_transits
                if track_name in _ttr.get(t["transit_planet"], [])
            ]
            if relevant:
                best_t = relevant[0]  # already sorted by orb
                t_planet = best_t["transit_planet"]
                n_planet = best_t["natal_planet"]
                asp = best_t["aspect"]
                asp_verb = _asp_flavour.get(asp, "aspecting")
                transit_note = f"{t_planet} is {asp_verb} your natal {n_planet} now."
                text = f"{text.rstrip('.')}. {transit_note}"

        # Retrograde notes per track
        if _retrograde_planets:
            _rx_track_map = {
                "Mercury": ["general", "career"],
                "Venus": ["love", "money"],
                "Mars": ["career", "health"],
                "Jupiter": ["money", "spiritual"],
                "Saturn": ["career", "money"],
            }
            for _rx in _retrograde_planets:
                if track_name in _rx_track_map.get(_rx, []):
                    _rx_notes = {
                        "Mercury": {
                            "general": "Mercury is retrograde — review before committing.",
                            "career": "Mercury Rx: slow down, recheck, then advance.",
                        },
                        "Venus": {
                            "love": "Venus is retrograde — old connections resurface; tread thoughtfully.",
                            "money": "Venus Rx: pause on new financial commitments.",
                        },
                        "Mars": {
                            "career": "Mars is retrograde — redirect energy inward before pushing forward.",
                            "health": "Mars Rx: rest and restore rather than strain.",
                        },
                        "Jupiter": {
                            "money": "Jupiter Rx: opportunities need a second look.",
                            "spiritual": "Jupiter Rx: revisit beliefs that no longer fit.",
                        },
                        "Saturn": {
                            "career": "Saturn Rx: structural reviews pay off now.",
                            "money": "Saturn Rx: shore up foundations before expanding.",
                        },
                    }
                    note = _rx_notes.get(_rx, {}).get(track_name)
                    if note:
                        text = f"{text.rstrip('.')}. {note}"
                    break  # one retrograde note per track is enough

        tracks[track_name] = text

        if track_data["ratings"]:
            rating = generate_deterministic_index(seed + f"{track_name}_rating", 5) + 1
            ratings[track_name] = rating

    # Lucky elements (same as before)
    num_count = 3 + generate_deterministic_index(seed + "num_count", 3)
    lucky_numbers = _pick_unique(LUCKY_NUMBERS_POOL, seed, num_count, "num")
    color_count = 1 + generate_deterministic_index(seed + "color_count", 3)
    lucky_colors = _pick_unique(LUCKY_COLORS_POOL, seed, color_count, "color")

    theme_words_pool = get_localized_pool("theme_words", THEME_WORDS, lang)
    theme_word = theme_words_pool[
        generate_deterministic_index(seed + "theme", len(theme_words_pool))
    ]

    advice_pool = get_localized_pool("advice", ADVICE_POOLS, lang)
    advice = advice_pool[
        generate_deterministic_index(seed + "advice", len(advice_pool))
    ]

    # Rising sign — use real flatlib Ascendant when birth time + location are available
    rising_sign = chart_ctx.get("asc_sign") or (
        compute_rising_sign(
            time_of_birth,
            dob=dob,
            latitude=latitude,
            longitude=longitude,
        )
        if time_of_birth
        else ""
    )
    place_vibe = None
    if place_of_birth:
        place_vibes_pool = get_localized_pool("place_vibes", PLACE_VIBES, lang)
        place_vibe = place_vibes_pool[
            generate_deterministic_index(seed + "place", len(place_vibes_pool))
        ]

    # Affirmation and daily action
    affirmation_pool = get_localized_pool("affirmations", AFFIRMATION_POOLS, lang)
    affirmation = affirmation_pool[
        generate_deterministic_index(seed + "affirmation", len(affirmation_pool))
    ]

    daily_actions_pool = get_localized_pool("daily_actions", DAILY_ACTIONS, lang)
    daily_action = daily_actions_pool[
        generate_deterministic_index(seed + "action", len(daily_actions_pool))
    ]

    # Build natal context summary for clients
    natal_context: Dict[str, Any] = {"sun_sign": sign}
    if chart_ctx:
        natal_context.update(
            {
                "moon_sign": chart_ctx.get("moon_sign") or None,
                "asc_sign": chart_ctx.get("asc_sign") or None,
                "venus_sign": chart_ctx.get("venus_sign") or None,
                "mars_sign": chart_ctx.get("mars_sign") or None,
                "mercury_sign": chart_ctx.get("mercury_sign") or None,
            }
        )

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
        "element": element_display,
        "place_vibe": place_vibe,
        "natal_context": natal_context,
        "active_transits": active_transits if active_transits else None,
    }


# ---------------------------------------------------------------------------
# Transit helpers (Fix 1)
# ---------------------------------------------------------------------------

_TRANSIT_ASPECT_ANGLES = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}
_TRANSIT_ORB = 3.5  # degrees


def _angular_diff(a: float, b: float) -> float:
    """Shortest arc between two ecliptic longitudes (0–360)."""
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def _get_transit_positions(date_str: str) -> Dict[str, float]:
    """
    Compute noon-UTC planetary longitudes for *date_str* (YYYY-MM-DD).
    Returns {planet_name: absolute_degree_0_360}.
    Uses flatlib when available; silently returns {} on failure.
    """
    try:
        from flatlib import const as flat_const
        from flatlib.chart import Chart
        from flatlib.datetime import Datetime
        from flatlib.geopos import GeoPos

        dt_str = date_str.replace("-", "/")
        dt = Datetime(dt_str, "12:00", "+00:00")
        pos = GeoPos("0n00", "0e00")
        chart = Chart(dt, pos)
        planets_out: Dict[str, float] = {}
        for name in [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]:
            try:
                p = chart.get(getattr(flat_const, name.upper(), None) or name)
                if p:
                    planets_out[name] = float(p.lon) % 360
            except Exception:
                pass
        return planets_out
    except Exception:
        return {}


def _find_transit_aspects(
    transit_positions: Dict[str, float],
    natal_positions: Dict[str, float],
    orb: float = _TRANSIT_ORB,
) -> List[Dict[str, Any]]:
    """
    Find tight aspects between transiting and natal planets.
    Returns list of dicts sorted by orb asc.
    """
    aspects: List[Dict[str, Any]] = []
    for t_name, t_lon in transit_positions.items():
        for n_name, n_lon in natal_positions.items():
            diff = _angular_diff(t_lon, n_lon)
            for asp_name, asp_angle in _TRANSIT_ASPECT_ANGLES.items():
                asp_orb = abs(diff - asp_angle)
                if asp_orb <= orb:
                    aspects.append(
                        {
                            "transit_planet": t_name,
                            "natal_planet": n_name,
                            "aspect": asp_name,
                            "orb": round(asp_orb, 2),
                        }
                    )
    return sorted(aspects, key=lambda x: x["orb"])


# Priority order for picking the most narrative-worthy transit
_TRANSIT_PLANET_PRIORITY = [
    "Venus",
    "Mars",
    "Sun",
    "Moon",
    "Mercury",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]
_NATAL_PLANET_PRIORITY = [
    "Sun",
    "Moon",
    "Ascendant",
    "Venus",
    "Mars",
    "Mercury",
    "Midheaven",
    "Jupiter",
    "Saturn",
]


def _pick_best_transit(aspects: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Pick the most astrologically significant transit from the aspect list."""
    if not aspects:
        return None

    # Score each aspect: lower score = higher priority
    def _score(a: Dict) -> int:
        tp = (
            _TRANSIT_PLANET_PRIORITY.index(a["transit_planet"])
            if a["transit_planet"] in _TRANSIT_PLANET_PRIORITY
            else 99
        )
        np = (
            _NATAL_PLANET_PRIORITY.index(a["natal_planet"])
            if a["natal_planet"] in _NATAL_PLANET_PRIORITY
            else 99
        )
        asp_prio = {
            "conjunction": 0,
            "opposition": 1,
            "square": 2,
            "trine": 3,
            "sextile": 4,
        }.get(a["aspect"], 5)
        return tp * 10 + np * 3 + asp_prio

    return min(aspects, key=_score)


def _get_chart_context(
    dob: str,
    time_of_birth: str = None,
    latitude: float = None,
    longitude: float = None,
    timezone: str = "UTC",
) -> Dict[str, Any]:
    """
    Return natal planet context from the chart engine.

    On success returns a dict with sun_sign, moon_sign, asc_sign and the
    sign for Venus, Mars, Mercury so track generation can reference the
    relevant planet.  Returns an empty dict on any failure so callers
    degrade gracefully.
    """
    if latitude is None or longitude is None or not dob:
        return {}
    try:
        from ..chart_service import build_natal_chart

        profile = {
            "date_of_birth": dob,
            "time_of_birth": time_of_birth or "12:00",
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
        }
        chart = build_natal_chart(profile)
        planets_list = chart.get("planets", [])
        planets = {p["name"]: p for p in planets_list}
        points_list = chart.get("points", [])
        points = {p["name"]: p for p in points_list}

        asc_sign = chart.get("ascendant", {}).get("sign") or ""

        def _sign(name: str) -> str:
            p = planets.get(name) or points.get(name) or {}
            return p.get("sign", "")

        return {
            "sun_sign": _sign("Sun"),
            "moon_sign": _sign("Moon"),
            "mercury_sign": _sign("Mercury"),
            "venus_sign": _sign("Venus"),
            "mars_sign": _sign("Mars"),
            "jupiter_sign": _sign("Jupiter"),
            "asc_sign": asc_sign,
        }
    except Exception:
        return {}


def _chart_enriched_tldr(
    sign: str,
    life_path: int,
    element_display: str,
    chart_ctx: Dict[str, Any],
    scope: str,
    seed: str,
) -> str:
    """Build a more specific TL;DR using real natal data when available."""
    moon = chart_ctx.get("moon_sign") or ""
    asc = chart_ctx.get("asc_sign") or ""

    if moon and asc:
        templates = [
            f"Your {sign} Sun, {moon} Moon, and {asc} rising shape this {scope}'s energy around Life Path {life_path}.",
            f"With {sign} solar energy, a {moon} Moon, and {asc} on the horizon, {scope} calls for {element_display} focus.",
            f"{scope.title()}'s vibration blends {sign}'s {element_display} drive with your {moon} Moon's instincts and {asc} ascendant.",
        ]
    elif moon:
        templates = [
            f"Your {sign} Sun and {moon} Moon guide this {scope}'s energy — Life Path {life_path} leads the way.",
            f"{sign} solar warmth meets {moon} lunar depth; a {scope} for integrating both.",
        ]
    else:
        # Fallback: use existing scope pools
        return ""

    idx = generate_deterministic_index(seed + "enriched_tldr", len(templates))
    return templates[idx]


def _get_redis_client():
    global _redis_client
    if not REDIS_URL or redis is None:
        return None
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL)
    return _redis_client


def _fusion_cache_key(
    name: str,
    dob: str,
    date: str,
    scope: str,
    time_of_birth: str,
    place_of_birth: str,
    lang: str = "en",
) -> str:
    return f"fusion:{name}:{dob}:{date}:{scope}:{time_of_birth or ''}:{place_of_birth or ''}:{lang}"
