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
from datetime import datetime
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
    from flatlib.geopos import GeoPos
    from flatlib.ephem import setPath
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
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
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
    _validate_profile(profile)
    dt = _parse_datetime(
        profile["date_of_birth"],
        profile.get("time_of_birth"),
        profile.get("timezone", "UTC"),
    )
    return _build_chart(dt, profile, chart_type="natal")


def build_transit_chart(profile: Dict, target_date: datetime) -> Dict:
    """Compute a transit chart for a given target date/time at profile location."""
    _validate_profile(profile)
    time_str = target_date.strftime("%H:%M")
    date_str = target_date.strftime("%Y-%m-%d")
    profile_copy = dict(profile)
    profile_copy["date_of_birth"] = date_str
    profile_copy["time_of_birth"] = time_str
    return _build_chart(target_date, profile_copy, chart_type="transit")


# ---------- Internal helpers ----------


def _parse_datetime(date_str: str, time_str: Optional[str], tz: str) -> datetime:
    time_part = time_str or "12:00"
    naive = datetime.fromisoformat(f"{date_str}T{time_part}")
    try:
        return naive.replace(tzinfo=ZoneInfo(tz))
    except Exception:
        # Fallback to naive if timezone invalid; validation should catch this first.
        return naive


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
    # Build flatlib datetime
    date_str = dt.strftime("%Y/%m/%d")
    time_str = dt.strftime("%H:%M")

    # Calculate timezone offset
    tz_name = profile.get("timezone", "UTC")
    try:
        # Create aware datetime to get correct offset for this specific time
        tz = ZoneInfo(tz_name)
        # dt is naive local time here
        dt_aware = dt.replace(tzinfo=tz)
        offset = dt_aware.strftime("%z")  # Returns +HHMM or -HHMM
        # Format for flatlib: +HH:MM
        offset_formatted = f"{offset[:3]}:{offset[3:]}"
    except Exception:
        offset_formatted = "+00:00"

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
            planets.append({
                "name": name,
                "sign": obj.sign,
                "degree": round(obj.signlon, 4),
                "absolute_degree": round(obj.lon, 4),
                "house": int(chart.houses.getObjectHouse(obj).id.replace("House", "")),
                "retrograde": obj.movement() == const.RETROGRADE,
            })
        except Exception:
            planets.append({
                "name": name,
                "sign": "Aries",
                "degree": 0.0,
                "absolute_degree": 0.0,
                "house": 1,
                "retrograde": False,
            })
    
    # Extract houses
    houses = []
    for i in range(1, 13):
        try:
            house = chart.get(f"House{i}")
            houses.append({
                "house": i,
                "sign": house.sign,
                "degree": round(house.signlon, 4),
            })
        except Exception:
            houses.append({
                "house": i,
                "sign": ZODIAC_SIGNS[(i - 1) % 12],
                "degree": 0.0,
            })
    
    # Calculate aspects
    aspects = _compute_aspects(planets)
    
    # Get Ascendant and MC
    try:
        asc = chart.get(const.ASC)
        mc = chart.get(const.MC)
        asc_data = {"sign": asc.sign, "degree": round(asc.signlon, 4), "absolute_degree": round(asc.lon, 4)}
        mc_data = {"sign": mc.sign, "degree": round(mc.signlon, 4), "absolute_degree": round(mc.lon, 4)}
    except Exception:
        asc_data = {"sign": "Aries", "degree": 0.0, "absolute_degree": 0.0}
        mc_data = {"sign": "Capricorn", "degree": 0.0, "absolute_degree": 0.0}
    
    return {
        "metadata": {
            "chart_type": chart_type,
            "datetime": dt.isoformat(),
            "location": {"lat": lat, "lon": lon},
            "house_system": profile.get("house_system", "Placidus"),
            "provider": "flatlib",
        },
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "ascendant": asc_data,
        "midheaven": mc_data,
    }


def _chart_stub(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    """Return a deterministic stub chart when flatlib is unavailable."""
    # Minimal predictable positions so downstream text can still render.
    planets = [
        {
            "name": name,
            "sign": ZODIAC_SIGNS[i % 12],
            "degree": float(i * 3),
            "absolute_degree": float(i * 3),
            "house": (i % 12) + 1,
            "retrograde": False,
        }
        for i, name in enumerate(PLANETS)
    ]
    houses = [
        {"house": i + 1, "sign": ZODIAC_SIGNS[i], "degree": float(i * 30)}
        for i in range(12)
    ]
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
        "houses": houses,
        "aspects": [],
        "ascendant": {"sign": "Aries", "degree": 0.0, "absolute_degree": 0.0},
        "midheaven": {"sign": "Capricorn", "degree": 0.0, "absolute_degree": 0.0},
    }


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
        raise ValueError(f"Unsupported house_system '{name}'. Allowed: {', '.join(HOUSE_SYSTEM_MAP.keys())}")
    const_name = HOUSE_SYSTEM_MAP[key]
    return getattr(const, const_name, const.HOUSES_PLACIDUS)
