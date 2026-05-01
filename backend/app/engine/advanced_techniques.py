"""
advanced_techniques.py
-----------------------
Phase 3 astrology techniques:
  - Annual & Monthly Profections (Hellenistic house-activation timing)
  - Declinations and Parallel / Contra-Parallel aspects
  - Fixed Star conjunctions (15 major stars)
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# PROFECTIONS
# ---------------------------------------------------------------------------

# Traditional whole-sign house rulers (used for profection lord)
_HOUSE_RULERS = {
    1: "Mars",  # Aries
    2: "Venus",  # Taurus
    3: "Mercury",  # Gemini
    4: "Moon",  # Cancer
    5: "Sun",  # Leo
    6: "Mercury",  # Virgo
    7: "Venus",  # Libra
    8: "Mars",  # Scorpio  (traditional)
    9: "Jupiter",  # Sagittarius
    10: "Saturn",  # Capricorn
    11: "Saturn",  # Aquarius (traditional)
    12: "Jupiter",  # Pisces   (traditional)
}

_HOUSE_FOCUS = {
    1: "Identity, body, and new beginnings",
    2: "Resources, money, and personal values",
    3: "Communication, siblings, and local travel",
    4: "Home, family, roots, and endings",
    5: "Creativity, romance, children, and pleasure",
    6: "Health, daily work, and service",
    7: "Partnerships, marriage, and open enemies",
    8: "Transformation, shared resources, and rebirth",
    9: "Higher education, long-distance travel, and philosophy",
    10: "Career, public reputation, and authority",
    11: "Friends, allies, groups, and long-term goals",
    12: "Hidden matters, isolation, karma, and retreat",
}

_LORD_KEYWORDS = {
    "Sun": "recognition, vitality, leadership, and self-expression",
    "Moon": "emotions, home, intuition, and the public",
    "Mercury": "communication, learning, contracts, and short journeys",
    "Venus": "love, beauty, harmony, pleasure, and finances",
    "Mars": "action, courage, conflict, drive, and sexuality",
    "Jupiter": "expansion, opportunity, wisdom, and abundance",
    "Saturn": "discipline, responsibility, restriction, and long-term building",
}


def calculate_profections(dob: str, ref_date: Optional[str] = None) -> Dict:
    """
    Annual and Monthly Profections.

    Every year of life advances the active house by 1 (Ascendant = House 1 at birth).
    Monthly sub-division further advances by 1 house per month.

    Returns the active annual house, its traditional lord, the monthly sub-lord,
    and thematic interpretations for the year.
    """
    dob_date = datetime.fromisoformat(dob).date()
    ref = datetime.fromisoformat(ref_date).date() if ref_date else date.today()

    # Full years elapsed since last birthday
    age = (ref.year - dob_date.year) - (
        1 if (ref.month, ref.day) < (dob_date.month, dob_date.day) else 0
    )

    # How many months into the current profected year
    last_bday = dob_date.replace(
        year=ref.year
        - (1 if (ref.month, ref.day) < (dob_date.month, dob_date.day) else 0)
    )
    months_elapsed = (ref.year - last_bday.year) * 12 + (ref.month - last_bday.month)
    if ref.day < last_bday.day:
        months_elapsed -= 1
    months_elapsed = max(0, min(11, months_elapsed))

    annual_house = (age % 12) + 1
    monthly_house = ((annual_house - 1 + months_elapsed) % 12) + 1

    annual_lord = _HOUSE_RULERS[annual_house]
    monthly_lord = _HOUSE_RULERS[monthly_house]

    return {
        "age": age,
        "annual_house": annual_house,
        "annual_lord": annual_lord,
        "annual_focus": _HOUSE_FOCUS[annual_house],
        "annual_lord_themes": _LORD_KEYWORDS.get(annual_lord, ""),
        "monthly_house": monthly_house,
        "monthly_lord": monthly_lord,
        "monthly_focus": _HOUSE_FOCUS[monthly_house],
        "months_into_year": months_elapsed + 1,
        "interpretation": (
            f"Year {age + 1} activates House {annual_house}: {_HOUSE_FOCUS[annual_house]}. "
            f"{annual_lord} becomes the Time Lord for the year, bringing themes of "
            f"{_LORD_KEYWORDS.get(annual_lord, 'change')}. "
            f"This month (month {months_elapsed + 1}) sub-activates House {monthly_house}: "
            f"{_HOUSE_FOCUS[monthly_house]}."
        ),
    }


# ---------------------------------------------------------------------------
# DECLINATIONS & PARALLEL ASPECTS
# ---------------------------------------------------------------------------

# Mean obliquity of the ecliptic (J2000, degrees).
# For maximum accuracy use pyswisseph swe.calc(jd, swe.ECL_NUT) — here we
# use the IAU 2006 series truncated to the linear term which is accurate
# to within ±0.01° for dates 1900–2100.
_J2000 = 2451545.0  # Julian date of J2000.0


def _obliquity_deg(jd: float) -> float:
    """Mean obliquity of the ecliptic in degrees for a given Julian date."""
    T = (jd - _J2000) / 36525.0  # Julian centuries from J2000
    eps0 = (
        23.439291111 - 0.013004167 * T - 0.000000164 * T * T + 0.000000504 * T * T * T
    )
    return eps0


def _ecliptic_to_declination(lon_deg: float, lat_deg: float, eps_deg: float) -> float:
    """Return the declination (degrees) from ecliptic coordinates."""
    lon = math.radians(lon_deg)
    lat = math.radians(lat_deg)
    eps = math.radians(eps_deg)
    sin_dec = math.sin(lat) * math.cos(eps) + math.cos(lat) * math.sin(eps) * math.sin(
        lon
    )
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_dec))))


# swisseph planet body IDs (same as in chart_service.py)
_PLANET_BODIES = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    "Chiron": 15,
    "North Node": 11,
    "South Node": 11,  # True Node
}

_PARALLEL_ORB = 1.2  # degrees — standard for parallel/contra-parallel


def calculate_declinations(
    profile: Dict,
    planet_positions: Optional[List[Dict]] = None,
) -> Dict:
    """
    Compute planetary declinations and find parallel / contra-parallel aspects.

    If pyswisseph is unavailable, approximates declinations from ecliptic
    longitude using the mean obliquity formula (accurate to ±2°).

    Args:
        profile: birth profile dict (date_of_birth, time_of_birth, timezone)
        planet_positions: optional pre-computed planet list from natal chart
                          (each dict has name + absolute_degree)

    Returns a dict with:
        - declinations: list of {name, declination, out_of_bounds}
        - parallels:    list of {planet_a, planet_b, type, orb}
    """
    from datetime import datetime as _dt

    from ..chart_service import HAS_SWISSEPH, _parse_datetime

    dob = profile["date_of_birth"]
    time_str = profile.get("time_of_birth")
    tz_str = profile.get("timezone", "UTC")

    dt = _parse_datetime(dob, time_str, tz_str)
    dt_utc = dt.astimezone(__import__("datetime").timezone.utc)

    declinations: List[Dict] = []

    if HAS_SWISSEPH:
        import swisseph as swe

        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )
        eps = _obliquity_deg(jd)

        for name, body_id in _PLANET_BODIES.items():
            try:
                # South Node has same position as North Node but opposite sign
                if name == "South Node":
                    res, _ = swe.calc_ut(jd, _PLANET_BODIES["North Node"])
                    lon = (res[0] + 180) % 360
                    lat = -res[1]
                else:
                    res, _ = swe.calc_ut(jd, body_id)
                    lon = res[0] % 360
                    lat = res[1]
                dec = _ecliptic_to_declination(lon, lat, eps)
                declinations.append(
                    {
                        "name": name,
                        "longitude": round(lon, 4),
                        "latitude": round(lat, 4),
                        "declination": round(dec, 4),
                        "out_of_bounds": abs(dec) > 23.44,  # beyond ecliptic tilt
                    }
                )
            except Exception:
                pass

    elif planet_positions:
        # Use ecliptic latitude from flatlib if present (Fix 3), otherwise 0
        days_from_2000 = (dt_utc.date() - _dt(2000, 1, 1).date()).days
        jd_approx = _J2000 + days_from_2000
        eps = _obliquity_deg(jd_approx)
        for p in planet_positions:
            lon = p.get("absolute_degree", 0.0)
            lat = p.get("ecliptic_latitude", 0.0)  # real lat when flatlib provided it
            dec = _ecliptic_to_declination(lon, lat, eps)
            declinations.append(
                {
                    "name": p["name"],
                    "longitude": round(lon, 4),
                    "latitude": round(lat, 4),
                    "declination": round(dec, 4),
                    "out_of_bounds": abs(dec) > 23.44,
                }
            )
    else:
        return {
            "declinations": [],
            "parallels": [],
            "note": "No position data available",
        }

    # Find parallels and contra-parallels
    parallels = []
    for i, a in enumerate(declinations):
        for b in declinations[i + 1 :]:
            dec_a = a["declination"]
            dec_b = b["declination"]
            # Parallel: same hemisphere, within orb
            parallel_orb = abs(abs(dec_a) - abs(dec_b))
            same_side = (dec_a > 0) == (dec_b > 0)
            if same_side and parallel_orb <= _PARALLEL_ORB:
                parallels.append(
                    {
                        "planet_a": a["name"],
                        "planet_b": b["name"],
                        "type": "parallel",
                        "orb": round(parallel_orb, 3),
                        "strength": round(1.0 - parallel_orb / _PARALLEL_ORB, 3),
                    }
                )
            # Contra-parallel: opposite hemispheres, similar absolute value
            elif not same_side and parallel_orb <= _PARALLEL_ORB:
                parallels.append(
                    {
                        "planet_a": a["name"],
                        "planet_b": b["name"],
                        "type": "contra_parallel",
                        "orb": round(parallel_orb, 3),
                        "strength": round(1.0 - parallel_orb / _PARALLEL_ORB, 3),
                    }
                )

    return {
        "declinations": declinations,
        "parallels": sorted(parallels, key=lambda x: x["orb"]),
    }


# ---------------------------------------------------------------------------
# FIXED STARS
# ---------------------------------------------------------------------------

# Tropical longitudes (degrees), precessed to 2025.0
# Base: J2000 values + (25 × 0.01396°) = +0.349°
# Stars selected for astrological significance.
FIXED_STARS = {
    "Algol": {
        "longitude": 56.51,
        "nature": "malefic",
        "keywords": "violence, loss, intensity, Medusa's head — powerful but dangerous energy",
    },
    "Alcyone": {
        "longitude": 60.32,
        "nature": "mixed",
        "keywords": "mysticism, grief, ambition, leadership of the Pleiades cluster",
    },
    "Aldebaran": {
        "longitude": 70.14,
        "nature": "benefic",
        "keywords": "success, honour, courage, integrity — Royal Star of the East",
    },
    "Rigel": {
        "longitude": 77.18,
        "nature": "benefic",
        "keywords": "ambition, education, wealth, mechanical skill",
    },
    "Betelgeuse": {
        "longitude": 89.10,
        "nature": "benefic",
        "keywords": "fame, military honour, fortune, great success",
    },
    "Sirius": {
        "longitude": 104.43,
        "nature": "benefic",
        "keywords": "fame, wealth, ambition, burning brightness — the Dog Star",
    },
    "Pollux": {
        "longitude": 113.57,
        "nature": "malefic",
        "keywords": "audacity, cruelty, poison, but also athleticism and prize-winning",
    },
    "Regulus": {
        "longitude": 150.35,
        "nature": "benefic",
        "keywords": "royalty, leadership, success — loses all if revenge is sought; Royal Star of the North",
    },
    "Spica": {
        "longitude": 204.18,
        "nature": "benefic",
        "keywords": "brilliance, artistic gifts, success in arts and sciences",
    },
    "Arcturus": {
        "longitude": 204.58,
        "nature": "benefic",
        "keywords": "pioneering spirit, wealth through journeys, renown",
    },
    "Antares": {
        "longitude": 250.12,
        "nature": "malefic",
        "keywords": "success but self-destruction, obsession, reckless courage — Royal Star of the West",
    },
    "Vega": {
        "longitude": 285.67,
        "nature": "benefic",
        "keywords": "artistic talent, idealism, luck, charisma",
    },
    "Deneb": {
        "longitude": 335.70,
        "nature": "benefic",
        "keywords": "intelligence, leadership, research, the bright tail of Cygnus",
    },
    "Fomalhaut": {
        "longitude": 334.22,
        "nature": "benefic",
        "keywords": "idealism, psychic ability, fame — Royal Star of the South",
    },
    "Scheat": {
        "longitude": 349.72,
        "nature": "malefic",
        "keywords": "misfortune, imprisonment, drowning, but also independent thought",
    },
}

_FIXED_STAR_ORB = 1.0  # degrees — tight orb for fixed star conjunctions


def find_fixed_star_conjunctions(
    planets: List[Dict],
    orb: float = _FIXED_STAR_ORB,
) -> List[Dict]:
    """
    Find conjunctions between natal planets/points and major fixed stars.

    Args:
        planets: list of dicts with 'name' and 'absolute_degree'
        orb:     maximum orb in degrees (default 1.0°)

    Returns list of {planet, star, orb, nature, keywords}
    """
    conjunctions = []
    for planet in planets:
        planet_lon = planet.get("absolute_degree", 0.0)
        planet_name = planet.get("name", "?")
        for star_name, star_data in FIXED_STARS.items():
            star_lon = star_data["longitude"]
            diff = abs((planet_lon - star_lon + 180) % 360 - 180)
            if diff <= orb:
                conjunctions.append(
                    {
                        "planet": planet_name,
                        "star": star_name,
                        "orb": round(diff, 3),
                        "nature": star_data["nature"],
                        "keywords": star_data["keywords"],
                        "interpretation": (
                            f"{planet_name} conjunct {star_name} (orb {diff:.2f}°): "
                            f"{star_data['keywords']}."
                        ),
                    }
                )
    return sorted(conjunctions, key=lambda x: x["orb"])
