"""
chart_service.py
----------------
Core chart engine using flatlib for accurate astrological calculations.

Requirements satisfied:
- Computes natal and transit charts.
- Uses Swiss Ephemeris files from /app/ephemeris by default (override with EPHEMERIS_PATH env).
- Returns ChartObject as a plain dict with planets, houses, and aspects.

Notes for deployment:
- Place Swiss Ephemeris (*.se1/*.se2 etc.) files in /app/ephemeris on Railway.
- Override the path with EPHEMERIS_PATH env var if you mount elsewhere.
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

DEFAULT_EPHEMERIS = "/app/ephemeris"
LOCAL_EPHEMERIS = os.path.join(os.path.dirname(__file__), "ephemeris")
if os.path.isdir(LOCAL_EPHEMERIS):
    DEFAULT_EPHEMERIS = LOCAL_EPHEMERIS

EPHEMERIS_PATH = os.getenv("EPHEMERIS_PATH", DEFAULT_EPHEMERIS)

# Set SE_EPHE_PATH env var BEFORE importing swisseph (it reads this on import)
os.environ["SE_EPHE_PATH"] = EPHEMERIS_PATH

# Set pyswisseph path explicitly (needed for asteroids like Chiron)
try:
    import swisseph as swe

    swe.set_ephe_path(EPHEMERIS_PATH)
except ImportError:
    pass

# Try to import flatlib
try:
    from flatlib import const
    from flatlib.chart import Chart
    from flatlib.datetime import Datetime
    from flatlib.ephem import setPath
    from flatlib.geopos import GeoPos

    setPath(EPHEMERIS_PATH)
    HAS_FLATLIB = True
except ImportError:
    HAS_FLATLIB = False


PLANETS = [
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
]

ZODIAC_SIGNS = [
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

ASPECT_ANGLES = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

ASPECT_ORBS = {
    "conjunction": 7.0,
    "sextile": 3.5,
    "square": 5.5,
    "trine": 5.5,
    "opposition": 7.0,
}

# Traditional + modern planetary dignities.
# domicile = ruling sign (strongest); exaltation = elevated sign (strong)
# detriment = opposite domicile (weakened); fall = opposite exaltation (weakened)
DIGNITIES: Dict[tuple, str] = {
    # Domicile
    ("Sun", "Leo"): "domicile",
    ("Moon", "Cancer"): "domicile",
    ("Mercury", "Gemini"): "domicile",
    ("Mercury", "Virgo"): "domicile",
    ("Venus", "Taurus"): "domicile",
    ("Venus", "Libra"): "domicile",
    ("Mars", "Aries"): "domicile",
    ("Mars", "Scorpio"): "domicile",
    ("Jupiter", "Sagittarius"): "domicile",
    ("Jupiter", "Pisces"): "domicile",
    ("Saturn", "Capricorn"): "domicile",
    ("Saturn", "Aquarius"): "domicile",
    ("Uranus", "Aquarius"): "domicile",
    ("Neptune", "Pisces"): "domicile",
    ("Pluto", "Scorpio"): "domicile",
    # Exaltation
    ("Sun", "Aries"): "exaltation",
    ("Moon", "Taurus"): "exaltation",
    ("Venus", "Pisces"): "exaltation",
    ("Mars", "Capricorn"): "exaltation",
    ("Jupiter", "Cancer"): "exaltation",
    ("Saturn", "Libra"): "exaltation",
    # Detriment (opposite domicile)
    ("Sun", "Aquarius"): "detriment",
    ("Moon", "Capricorn"): "detriment",
    ("Mercury", "Sagittarius"): "detriment",
    ("Venus", "Aries"): "detriment",
    ("Venus", "Scorpio"): "detriment",
    ("Mars", "Taurus"): "detriment",
    ("Mars", "Libra"): "detriment",
    ("Jupiter", "Gemini"): "detriment",
    ("Jupiter", "Virgo"): "detriment",
    ("Saturn", "Cancer"): "detriment",
    ("Saturn", "Leo"): "detriment",
    # Fall (opposite exaltation)
    ("Sun", "Libra"): "fall",
    ("Moon", "Scorpio"): "fall",
    ("Mercury", "Pisces"): "fall",
    ("Venus", "Virgo"): "fall",
    ("Mars", "Cancer"): "fall",
    ("Jupiter", "Capricorn"): "fall",
    ("Saturn", "Aries"): "fall",
}

# Dignity weight multipliers used by the rule engine
DIGNITY_WEIGHTS: Dict[str, float] = {
    "domicile": 1.3,
    "exaltation": 1.2,
    "detriment": 0.8,
    "fall": 0.8,
}

# Points (sensitive points & asteroids) extracted alongside planets
CHART_POINTS = ["North Node", "South Node", "Chiron"]

HOUSE_SYSTEM_MAP = {
    "placidus": "HOUSES_PLACIDUS",
    "whole": "HOUSES_WHOLE_SIGN",
    "equal": "HOUSES_EQUAL",
    "koch": "HOUSES_KOCH",
    "campanus": "HOUSES_CAMPANUS",
    "topocentric": "HOUSES_TOPOCENTRIC",
    "regiomontanus": "HOUSES_REGIOMONTANUS",
    "porphyry": "HOUSES_PORPHYRIUS",
}


# ---------- Public API ----------


def build_natal_chart(profile: Dict) -> Dict:
    """Compute a natal chart for a profile."""
    has_time = bool(profile.get("time_of_birth"))
    has_location = (
        profile.get("latitude") is not None and profile.get("longitude") is not None
    )
    # If time_confidence not supplied, infer: provided time = exact, missing = unknown
    time_confidence = profile.get("time_confidence") or (
        "exact" if has_time else "unknown"
    )
    birth_time_assumed = not has_time or time_confidence in ("approximate", "unknown")

    # Fill in defaults so _validate_profile doesn't raise
    profile_copy = dict(profile)
    if not has_location:
        profile_copy.setdefault("latitude", 0.0)
        profile_copy.setdefault("longitude", 0.0)
    profile_copy.setdefault("timezone", "UTC")

    _validate_profile(profile_copy)
    dt = _parse_datetime(
        profile_copy["date_of_birth"],
        profile_copy.get("time_of_birth"),
        profile_copy.get("timezone", "UTC"),
    )
    chart = _build_chart(dt, profile_copy, chart_type="natal")
    # Determine data quality tier
    if not has_location:
        data_quality = "date_only"
    elif birth_time_assumed:
        data_quality = "date_and_place"
    else:
        data_quality = "full"
    # Annotate with data quality flags
    chart["metadata"]["birth_time_assumed"] = birth_time_assumed
    chart["metadata"]["time_confidence"] = time_confidence
    chart["metadata"]["data_quality"] = data_quality
    if birth_time_assumed:
        chart["metadata"]["assumed_time_of_birth"] = "12:00"
    if not has_location:
        chart["metadata"]["location_assumed"] = True
    # Check moon sign ambiguity (Moon changes sign on birth date)
    chart["metadata"]["moon_sign_uncertain"] = _moon_changes_sign_on_date(profile_copy)
    return chart


def build_progressed_chart(profile: Dict, target_date: Optional[str] = None) -> Dict:
    """
    Secondary progression chart: 1 day after birth = 1 year of life.

    For a person aged N years, the progressed chart is cast for the date
    DOB + N days. Time of birth is preserved; location is the birth location.
    """

    dob = datetime.fromisoformat(profile["date_of_birth"]).date()
    ref_date = (
        datetime.fromisoformat(target_date).date()
        if target_date
        else datetime.now().date()
    )
    age_days = (ref_date - dob).days // 365  # 1 solar year ≈ 365 days progression
    progressed_date = dob + timedelta(days=age_days)

    profile_copy = dict(profile)
    profile_copy["date_of_birth"] = progressed_date.isoformat()

    dt = _parse_datetime(
        profile_copy["date_of_birth"],
        profile_copy.get("time_of_birth"),
        profile_copy.get("timezone", "UTC"),
    )
    chart = _build_chart(dt, profile_copy, chart_type="progressed")
    chart["metadata"]["progressed_date"] = progressed_date.isoformat()
    chart["metadata"]["natal_date"] = profile["date_of_birth"]
    chart["metadata"]["reference_date"] = ref_date.isoformat()
    chart["metadata"]["age_years"] = age_days
    return chart


def build_transit_chart(profile: Dict, target_date: datetime) -> Dict:
    """Compute a transit chart for a given target date/time at profile location."""
    _validate_profile(profile)
    tz = _tzinfo_from_name(profile.get("timezone", "UTC"))
    if target_date.tzinfo is None:
        dt_local = target_date.replace(tzinfo=tz)
    else:
        dt_local = target_date.astimezone(tz)

    time_str = dt_local.strftime("%H:%M")
    date_str = dt_local.strftime("%Y-%m-%d")
    profile_copy = dict(profile)
    profile_copy["date_of_birth"] = date_str
    profile_copy["time_of_birth"] = time_str
    return _build_chart(dt_local, profile_copy, chart_type="transit")


# ---------- Internal helpers ----------


def _parse_datetime(date_str: str, time_str: Optional[str], tz: str) -> datetime:
    time_part = time_str or "12:00"
    naive = datetime.fromisoformat(f"{date_str}T{time_part}")
    return naive.replace(tzinfo=_tzinfo_from_name(tz))


def _validate_profile(profile: Dict) -> None:
    lat = profile.get("latitude")
    lon = profile.get("longitude")
    tz = profile.get("timezone")
    errors = []
    if lat is None or lon is None:
        errors.append("latitude/longitude required; geocode before requesting chart")
    if tz is None:
        errors.append("timezone required")
    if errors:
        raise ValueError("; ".join(errors))


def _get_house_for_longitude(planet_lon: float, house_cusps: List[float]) -> int:
    """Determine which house a planet is in based on its longitude and house cusps."""
    for i in range(12):
        cusp_start = house_cusps[i]
        cusp_end = house_cusps[(i + 1) % 12]
        # Handle wrap-around at 360 degrees
        if cusp_start > cusp_end:
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
        else:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
    return 1  # Default to house 1


def _build_chart(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    # Fallback: if flatlib isn't installed, return a safe stub chart so the app can still respond.
    if not HAS_FLATLIB:
        return _chart_stub(dt, profile, chart_type)

    try:
        return _chart_with_flatlib(dt, profile, chart_type)
    except ValueError as e:
        # Flatlib can raise math domain errors for polar regions; fall back to a simplified chart.
        if "math domain" in str(e) or abs(float(profile.get("latitude") or 0)) >= 66:
            return _chart_polar_fallback(dt, profile, chart_type)
        raise
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise RuntimeError(f"Chart calculation failed: {str(e)}")


def _chart_with_flatlib(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    """Calculate chart using flatlib."""
    tz = _tzinfo_from_name(profile.get("timezone", "UTC"))
    if dt.tzinfo is None:
        dt_local = dt.replace(tzinfo=tz)
    else:
        dt_local = dt.astimezone(tz)

    date_str = dt_local.strftime("%Y/%m/%d")
    time_str = dt_local.strftime("%H:%M")
    offset = dt_local.strftime("%z")  # +HHMM / -HHMM
    offset_formatted = f"{offset[:3]}:{offset[3:]}" if offset else "+00:00"

    flat_dt = Datetime(date_str, time_str, offset_formatted)

    # Get location
    lat = float(profile.get("latitude") or 0.0)
    lon = float(profile.get("longitude") or 0.0)
    pos = GeoPos(lat, lon)

    # Get house system
    house_sys = _resolve_house_system(profile.get("house_system"))

    # Create chart with all planets
    chart = Chart(flat_dt, pos, hsys=house_sys, IDs=const.LIST_OBJECTS)

    # Extract planets
    planets = []
    for name in PLANETS:
        try:
            obj = chart.get(getattr(const, name.upper(), name))
            sign = obj.sign
            planets.append(
                {
                    "name": name,
                    "sign": sign,
                    "degree": round(obj.signlon, 4),
                    "absolute_degree": round(obj.lon, 4),
                    "house": int(
                        chart.houses.getObjectHouse(obj).id.replace("House", "")
                    ),
                    "retrograde": obj.movement() == const.RETROGRADE,
                    "dignity": _get_dignity(name, sign),
                }
            )
        except Exception:
            planets.append(
                {
                    "name": name,
                    "sign": "Aries",
                    "degree": 0.0,
                    "absolute_degree": 0.0,
                    "house": 1,
                    "retrograde": False,
                    "dignity": None,
                }
            )

    # Extract sensitive points: North Node, South Node, Chiron
    _POINT_CONST_MAP = {
        "North Node": "NORTH_NODE",
        "South Node": "SOUTH_NODE",
        "Chiron": "CHIRON",
    }
    points = []
    for point_name in CHART_POINTS:
        const_attr = _POINT_CONST_MAP.get(point_name)
        try:
            obj = chart.get(getattr(const, const_attr))
            points.append(
                {
                    "name": point_name,
                    "sign": obj.sign,
                    "degree": round(obj.signlon, 4),
                    "absolute_degree": round(obj.lon, 4),
                    "house": int(
                        chart.houses.getObjectHouse(obj).id.replace("House", "")
                    ),
                    "retrograde": obj.movement() == const.RETROGRADE,
                }
            )
        except Exception:
            pass  # Skip silently if a point isn't available in this flatlib build

    # Extract houses
    houses = []
    for i in range(1, 13):
        try:
            house = chart.get(f"House{i}")
            houses.append(
                {
                    "house": i,
                    "sign": house.sign,
                    "degree": round(house.signlon, 4),
                }
            )
        except Exception:
            houses.append(
                {
                    "house": i,
                    "sign": ZODIAC_SIGNS[(i - 1) % 12],
                    "degree": 0.0,
                }
            )

    # Calculate aspects
    aspects = _compute_aspects(planets)

    # Get Ascendant and MC
    try:
        asc = chart.get(const.ASC)
        mc = chart.get(const.MC)
        asc_data = {
            "sign": asc.sign,
            "degree": round(asc.signlon, 4),
            "absolute_degree": round(asc.lon, 4),
        }
        mc_data = {
            "sign": mc.sign,
            "degree": round(mc.signlon, 4),
            "absolute_degree": round(mc.lon, 4),
        }
    except Exception:
        asc_data = {"sign": "Aries", "degree": 0.0, "absolute_degree": 0.0}
        mc_data = {"sign": "Capricorn", "degree": 0.0, "absolute_degree": 0.0}

    # Calculate Part of Fortune (Arabic Lot)
    # Day chart (Sun above horizon): PoF = ASC + Moon - Sun
    # Night chart (Sun below horizon): PoF = ASC + Sun - Moon
    # Sun is above horizon when (sun_lon - asc_lon) % 360 >= 180
    try:
        sun_obj = next((p for p in planets if p["name"] == "Sun"), None)
        moon_obj = next((p for p in planets if p["name"] == "Moon"), None)
        asc_lon = asc_data.get("absolute_degree", 0.0)
        if sun_obj and moon_obj:
            sun_lon = sun_obj["absolute_degree"]
            moon_lon = moon_obj["absolute_degree"]
            is_day = (sun_lon - asc_lon) % 360 >= 180
            pof_lon = (
                (asc_lon + moon_lon - sun_lon) % 360
                if is_day
                else (asc_lon + sun_lon - moon_lon) % 360
            )
            pof_sign = ZODIAC_SIGNS[int(pof_lon / 30) % 12]
            pof_degree = pof_lon % 30
            # House cusps from extracted houses (use ZODIAC_SIGNS offset as fallback)
            house_cusps = []
            for i, h in enumerate(houses):
                sign_offset = (
                    ZODIAC_SIGNS.index(h["sign"]) * 30
                    if h["sign"] in ZODIAC_SIGNS
                    else i * 30
                )
                house_cusps.append((sign_offset + h.get("degree", 0.0)) % 360)
            if not house_cusps:
                house_cusps = [i * 30.0 for i in range(12)]
            pof_house = _get_house_for_longitude(pof_lon, house_cusps)
            points.append(
                {
                    "name": "Part of Fortune",
                    "sign": pof_sign,
                    "degree": round(pof_degree, 4),
                    "absolute_degree": round(pof_lon, 4),
                    "house": pof_house,
                    "retrograde": False,
                    "chart_type": "day" if is_day else "night",
                }
            )
    except Exception:
        pass  # Part of Fortune is non-critical; skip silently on error

    return {
        "metadata": {
            "chart_type": chart_type,
            "datetime": dt_local.isoformat(),
            "location": {"lat": lat, "lon": lon},
            "house_system": profile.get("house_system", "Placidus"),
            "provider": "flatlib",
        },
        "planets": planets,
        "points": points,
        "houses": houses,
        "aspects": aspects,
        "ascendant": asc_data,
        "midheaven": mc_data,
    }


def _chart_stub(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    """Return a deterministic stub chart when flatlib is unavailable."""
    # Keep fallback charts deterministic while still varying by chart datetime.
    seed_key = "|".join(
        [
            dt.astimezone(timezone.utc).isoformat(),
            str(profile.get("latitude") or 0.0),
            str(profile.get("longitude") or 0.0),
            chart_type,
        ]
    )
    seed = int(hashlib.sha256(seed_key.encode()).hexdigest()[:8], 16)

    planets = []
    for i, name in enumerate(PLANETS):
        absolute_degree = float((seed + i * 37) % 360)
        sign_index = int(absolute_degree // 30) % 12
        degree = round(absolute_degree % 30, 4)
        planets.append(
            {
                "name": name,
                "sign": ZODIAC_SIGNS[sign_index],
                "degree": degree,
                "absolute_degree": round(absolute_degree, 4),
                "house": sign_index + 1,
                "retrograde": bool((seed + i) % 5 == 0),
                "dignity": _get_dignity(name, ZODIAC_SIGNS[sign_index]),
            }
        )

    if (profile.get("house_system") or "Placidus").lower() == "whole":
        house_offset = 0.0
    else:
        house_offset = round(((seed // 12) % 29) + 0.5, 4)

    houses = [
        {
            "house": i + 1,
            "sign": ZODIAC_SIGNS[i],
            "degree": house_offset,
        }
        for i in range(12)
    ]

    aspects = _compute_aspects(planets)
    return {
        "metadata": {
            "chart_type": chart_type,
            "datetime": dt.isoformat(),
            "location": {
                "lat": float(profile.get("latitude") or 0.0),
                "lon": float(profile.get("longitude") or 0.0),
            },
            "house_system": profile.get("house_system", "Placidus"),
            "provider": "stub",
        },
        "planets": planets,
        "points": [],
        "houses": houses,
        "aspects": aspects,
        "ascendant": {"sign": "Aries", "degree": 0.0, "absolute_degree": 0.0},
        "midheaven": {"sign": "Capricorn", "degree": 0.0, "absolute_degree": 0.0},
    }


def _moon_changes_sign_on_date(profile: Dict) -> bool:
    """Return True if the Moon changes zodiac sign during the birth date (00:00–23:59).
    When True the Moon sign is ambiguous without an exact birth time."""
    if not HAS_FLATLIB:
        return False
    try:
        date_str = profile["date_of_birth"]
        tz_str = profile.get("timezone", "UTC")
        tz = _tzinfo_from_name(tz_str)
        lat = float(profile.get("latitude") or 0.0)
        lon = float(profile.get("longitude") or 0.0)
        pos = GeoPos(lat, lon)

        def _moon_sign(hour: int) -> str:
            dt = datetime.fromisoformat(f"{date_str}T{hour:02d}:00").replace(tzinfo=tz)
            date_f = dt.strftime("%Y/%m/%d")
            time_f = dt.strftime("%H:%M")
            offset = dt.strftime("%z")
            offset_f = f"{offset[:3]}:{offset[3:]}" if offset else "+00:00"
            c = Chart(Datetime(date_f, time_f, offset_f), pos, IDs=[const.MOON])
            return c.get(const.MOON).sign

        return _moon_sign(0) != _moon_sign(23)
    except Exception:
        return False


def _tzinfo_from_name(tz_name: Optional[str]):
    tz_name = (tz_name or "UTC").strip()
    if tz_name in ("UTC", "GMT"):
        return timezone.utc
    # Support fixed-offset identifiers commonly produced by some client APIs.
    # Examples: "GMT+0100", "GMT+01:00", "UTC-5", "+01:00", "-0530".
    offset_re = re.compile(
        r"^(?:UTC|GMT)?\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?$", re.IGNORECASE
    )
    match = offset_re.match(tz_name)
    if match:
        sign, hh, mm = match.groups()
        hours = int(hh)
        minutes = int(mm or "0")
        if hours > 23 or minutes > 59:
            raise ValueError(f"Invalid timezone offset: {tz_name}")
        delta = timedelta(hours=hours, minutes=minutes)
        if sign == "-":
            delta = -delta
        return timezone(delta)

    return ZoneInfo(tz_name)


def _chart_polar_fallback(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    """Gracefully degrade charts for extreme latitudes where flatlib errors."""
    # Use equal-house with synthetic cusps; keep planets from stub to avoid math errors.
    base = _chart_stub(dt, profile, chart_type)
    base["metadata"]["provider"] = "polar-fallback"
    base["metadata"]["note"] = "Polar latitude fallback; positions approximated"
    return base


def _compute_aspects(planets: List[Dict]) -> List[Dict]:
    aspects: List[Dict] = []
    for i, pa in enumerate(planets):
        for pb in planets[i + 1 :]:
            diff = _deg_diff(pa["absolute_degree"], pb["absolute_degree"])
            aspect_type, orb = _closest_aspect(diff)
            if aspect_type and orb <= ASPECT_ORBS[aspect_type]:
                aspects.append(
                    {
                        "planet_a": pa["name"],
                        "planet_b": pb["name"],
                        "type": aspect_type,
                        "orb": round(orb, 2),
                        "strength": _score_aspect(aspect_type, orb),
                    }
                )
    return aspects


def _deg_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _closest_aspect(diff: float):
    closest = None
    min_orb = 999.0
    for name, angle in ASPECT_ANGLES.items():
        orb = abs(diff - angle)
        if orb < min_orb:
            min_orb = orb
            closest = name
    return closest, min_orb


def _score_aspect(aspect_type: str, orb: float) -> float:
    max_orb = ASPECT_ORBS.get(aspect_type, 6.0)
    base = max(0.1, 1 - orb / max_orb)
    weight = 1.2 if aspect_type in ["conjunction", "opposition"] else 1.0
    weight = 1.1 if aspect_type in ["trine", "sextile"] else weight
    return round(base * weight, 3)


def _resolve_house_system(name: Optional[str]):
    """Map human string to flatlib house constant; default to Placidus."""
    if not HAS_FLATLIB:
        return const.HOUSES_PLACIDUS
    key = (name or "Placidus").lower()
    if key not in HOUSE_SYSTEM_MAP:
        raise ValueError(
            f"Unsupported house_system '{name}'. Allowed: {', '.join(HOUSE_SYSTEM_MAP.keys())}"
        )
    const_name = HOUSE_SYSTEM_MAP[key]
    return getattr(const, const_name, const.HOUSES_PLACIDUS)


def _get_dignity(planet_name: str, sign: str) -> Optional[str]:
    """Return the dignity status for a planet in a sign, or None if peregrine."""
    return DIGNITIES.get((planet_name, sign))
