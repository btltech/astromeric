"""
astro_context.py
----------------
Single source of truth for all daily feature inputs.

Resolves natal context, current sky, numerology cycles, and trust gates
from a profile payload and reference date, then returns a plain dict that
every daily-feature generator can consume without re-calculating anything.

Usage
-----
    from app.engine.astro_context import build_astro_context

    context = build_astro_context(profile, reference_date)
    # Pass context to any feature function — never re-derive inputs inside them.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Traditional weekday planetary rulers (Python weekday: 0 = Monday)
WEEKDAY_RULER: Dict[int, str] = {
    0: "Moon",
    1: "Mars",
    2: "Mercury",
    3: "Jupiter",
    4: "Venus",
    5: "Saturn",
    6: "Sun",
}

# Classical Chaldean / Pythagorean planet correspondence numbers
# Used as optional "resonance" anchors in lucky-number tier 3.
PLANET_NUMBERS: Dict[str, int] = {
    "Sun": 1,
    "Moon": 2,
    "Jupiter": 3,
    "Uranus": 4,  # modern; traditional slot is Saturn=4
    "Mercury": 5,
    "Venus": 6,
    "Neptune": 7,  # modern; traditional slot is Saturn=7
    "Saturn": 8,
    "Mars": 9,
}

# Traditional sign rulers (used when birth time is trusted and Ascendant is known)
SIGN_RULERS: Dict[str, str] = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

SIGN_ELEMENTS: Dict[str, str] = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}

# Birth times that indicate the noon fallback / unknown time
_NOON_FALLBACKS = {"12:00", "12:00:00", "noon", "12", ""}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _reduce_to_single(n: int, *, preserve_master: bool = True) -> int:
    """
    Reduce integer to a single digit.
    Preserves master numbers 11, 22, 33 when preserve_master is True.
    """
    while n > 9:
        if preserve_master and n in (11, 22, 33):
            break
        n = sum(int(d) for d in str(n))
    return n


def _traditional_life_path(dob: str) -> int:
    """
    Pythagorean Traditional method: reduce Month, Day, and Year *separately*,
    then sum. Preserves master numbers 11, 22, 33.

    This is the platform's canonical life-path calculation.
    """
    try:
        parts = dob.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        m = _reduce_to_single(month)
        d = _reduce_to_single(day)
        y = _reduce_to_single(year)
        return _reduce_to_single(m + d + y)
    except Exception:
        return 1


def _compute_universal_day(ref: date) -> int:
    """Universal day number: reduce all digits of the full date."""
    digits = str(ref.year).zfill(4) + str(ref.month).zfill(2) + str(ref.day).zfill(2)
    return _reduce_to_single(sum(int(c) for c in digits))


def _compute_calendar_reduction(ref: date) -> int:
    """Calendar reduction: day + month, reduced to single digit."""
    return _reduce_to_single(ref.day + ref.month)


def _is_noon_fallback(time_str: Optional[str]) -> bool:
    """Return True when birth time was not provided or is the noon default."""
    if not time_str:
        return True
    cleaned = time_str.strip().lower().replace(" ", "")
    return cleaned in _NOON_FALLBACKS


def _profile_get(profile: Any, field: str, default=None):
    """Access a field from either a Pydantic model or a plain dict."""
    if hasattr(profile, field):
        return getattr(profile, field, default)
    if isinstance(profile, dict):
        return profile.get(field, default)
    return default


def _sun_sign_from_month_day(month: int, day: int) -> str:
    """
    Pure-Python Sun-sign derivation — used as a fallback when the
    astrology engine import fails.
    """
    ranges = [
        ("Aries", (3, 21), (4, 19)),
        ("Taurus", (4, 20), (5, 20)),
        ("Gemini", (5, 21), (6, 20)),
        ("Cancer", (6, 21), (7, 22)),
        ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)),
        ("Libra", (9, 23), (10, 22)),
        ("Scorpio", (10, 23), (11, 21)),
        ("Sagittarius", (11, 22), (12, 21)),
        ("Capricorn", (12, 22), (1, 19)),
        ("Aquarius", (1, 20), (2, 18)),
        ("Pisces", (2, 19), (3, 20)),
    ]
    for sign, (sm, sd), (em, ed) in ranges:
        if (month == sm and day >= sd) or (month == em and day <= ed):
            return sign
    return "Capricorn"


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------


def build_astro_context(
    profile: Any,
    reference_date: date,
    *,
    force_birth_time_trusted: Optional[bool] = None,
    force_location_trusted: Optional[bool] = None,
) -> Dict:
    """
    Build the complete AstroContext for ``reference_date``.

    This is the SINGLE source of truth used by all daily-feature generators.
    No feature function should separately resolve Moon sign, life path,
    personal day, or trust gates — they must use this context dict.

    Parameters
    ----------
    profile : ProfilePayload | dict
        User profile containing at least ``date_of_birth``.
        Optional: ``time_of_birth``, ``latitude``, ``longitude``, ``timezone``.
    reference_date : date
        Calendar date for which daily features are being generated.
    force_birth_time_trusted : bool, optional
        Override the automatic birth-time trust gate (useful in tests).
    force_location_trusted : bool, optional
        Override the automatic location trust gate (useful in tests).

    Returns
    -------
    dict
        A flat context dict. Keys are documented in the module docstring.
    """

    dob = _profile_get(profile, "date_of_birth") or "1990-01-01"
    time_of_birth = _profile_get(profile, "time_of_birth")
    latitude = _profile_get(profile, "latitude")
    longitude = _profile_get(profile, "longitude")

    # ── Trust gates ─────────────────────────────────────────────────────────
    if force_birth_time_trusted is not None:
        birth_time_trusted = force_birth_time_trusted
    else:
        birth_time_trusted = not _is_noon_fallback(time_of_birth)

    if force_location_trusted is not None:
        location_trusted = force_location_trusted
    else:
        location_trusted = bool(
            latitude is not None
            and longitude is not None
            and not (latitude == 0.0 and longitude == 0.0)
        )

    usable_inputs = {
        "can_use_ascendant": birth_time_trusted,
        "can_use_chart_ruler": birth_time_trusted,
        "can_use_house_logic": birth_time_trusted,
        "can_use_local_timing": location_trusted,
    }

    # ── Natal Sun / dominant element ────────────────────────────────────────
    natal_sun = None
    dominant_element = "Fire"
    try:
        from .astrology import get_element, get_zodiac_sign

        natal_sun = get_zodiac_sign(dob)
        dominant_element = get_element(natal_sun)
    except Exception:
        try:
            parts = dob.split("-")
            natal_sun = _sun_sign_from_month_day(int(parts[1]), int(parts[2]))
            dominant_element = SIGN_ELEMENTS.get(natal_sun, "Fire")
        except Exception:
            natal_sun = "Aries"
            dominant_element = "Fire"

    # ── Natal Moon (birth-time Moon; estimated from birth date at noon) ──────
    natal_moon: Optional[str] = None
    try:
        from .moon_phases import estimate_moon_sign

        parts = dob.split("-")
        birth_dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]), 12, 0)
        natal_moon = estimate_moon_sign(birth_dt)
    except Exception:
        pass

    # ── Ascendant + chart ruler (only when birth time is trusted) ───────────
    natal_ascendant: Optional[str] = None
    chart_ruler: Optional[str] = None

    if birth_time_trusted:
        # Attempt via natal chart builder (requires ephemeris)
        try:
            from ..chart_service import build_natal_chart

            profile_dict = {
                "name": _profile_get(profile, "name") or "User",
                "date_of_birth": dob,
                "time_of_birth": time_of_birth or "12:00",
                "latitude": latitude or 40.7128,
                "longitude": longitude or -74.006,
                "timezone": _profile_get(profile, "timezone") or "UTC",
            }
            natal = build_natal_chart(profile_dict)
            asc = natal.get("ascendant") or natal.get("houses", {}).get("ascendant")
            if isinstance(asc, dict):
                natal_ascendant = asc.get("sign")
            elif isinstance(asc, str):
                natal_ascendant = asc
            if natal_ascendant:
                chart_ruler = SIGN_RULERS.get(natal_ascendant)
        except Exception:
            pass

    # ── Current-sky Moon ─────────────────────────────────────────────────────
    moon_sign = "Cancer"
    moon_sign_basis = "estimated"
    moon_phase = "Waxing Crescent"
    moon_illumination = 50.0
    moon_phase_emoji = "🌒"

    try:
        from .moon_phases import calculate_moon_phase, estimate_moon_sign

        ref_dt = datetime(
            reference_date.year, reference_date.month, reference_date.day, 12, 0
        )
        moon_data = calculate_moon_phase(ref_dt)
        moon_sign = moon_data.get("moon_sign") or estimate_moon_sign(ref_dt)
        moon_sign_basis = "calculated"
        moon_phase = moon_data.get("phase_name", "Waxing Crescent")
        moon_illumination = moon_data.get("illumination", 50.0)
        moon_phase_emoji = moon_data.get("emoji", "🌒")
    except Exception:
        pass

    # ── Numerology cycles ────────────────────────────────────────────────────
    life_path = _traditional_life_path(dob)
    personal_year = 5
    personal_month = 5
    personal_day = 5

    try:
        from .numerology_extended import (
            calculate_personal_day,
            calculate_personal_month,
            calculate_personal_year,
        )

        personal_year = calculate_personal_year(dob, reference_date.year)
        personal_month = calculate_personal_month(personal_year, reference_date.month)
        personal_day = calculate_personal_day(personal_month, reference_date.day)
    except Exception:
        # Graceful fallback using simple reduction
        personal_year = _reduce_to_single(life_path + reference_date.year % 9 or 9)
        personal_month = _reduce_to_single(personal_year + reference_date.month)
        personal_day = _reduce_to_single(personal_month + reference_date.day)

    universal_day = _compute_universal_day(reference_date)
    calendar_reduction = _compute_calendar_reduction(reference_date)

    # ── Day ruler ─────────────────────────────────────────────────────────────
    day_ruler = WEEKDAY_RULER.get(reference_date.weekday(), "Sun")

    # ── Assemble and return ───────────────────────────────────────────────────
    return {
        # Calendar
        "reference_date": reference_date,
        # Natal placements
        "natal_sun": natal_sun,
        "natal_moon": natal_moon,  # estimated from birth date; Moon sign at noon on DOB
        "natal_ascendant": natal_ascendant,  # None if birth_time_trusted is False
        "chart_ruler": chart_ruler,  # None if birth_time_trusted is False
        # Element / nature
        "dominant_element": dominant_element,
        # Numerology
        "life_path": life_path,
        "personal_year": personal_year,
        "personal_month": personal_month,
        "personal_day": personal_day,
        "universal_day": universal_day,
        "calendar_reduction": calendar_reduction,
        # Current sky
        "moon_sign": moon_sign,
        "moon_sign_basis": moon_sign_basis,  # "calculated" | "estimated"
        "moon_phase": moon_phase,
        "moon_illumination": moon_illumination,
        "moon_phase_emoji": moon_phase_emoji,
        "day_ruler": day_ruler,
        "planetary_hour": None,  # Reserved; not yet implemented
        # Trust gates
        "birth_time_trusted": birth_time_trusted,
        "location_trusted": location_trusted,
        "usable_inputs": usable_inputs,
    }
