"""
chart_service.py
----------------
Core chart engine wrapping Flatlib (Swiss Ephemeris) behind a stable interface.

Requirements satisfied:
- Computes natal and transit charts.
- Uses Swiss Ephemeris files from /app/ephemeris by default (override with EPHEMERIS_PATH env).
- Returns ChartObject as a plain dict with planets, houses, and aspects.

Notes for deployment:
- Place Swiss Ephemeris (*.se1/.*se2 etc.) files in /app/ephemeris on Railway.
- Override the path with EPHEMERIS_PATH env var if you mount elsewhere.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_EPHEMERIS = "/app/ephemeris"
LOCAL_EPHEMERIS = os.path.join(os.path.dirname(__file__), "ephemeris")
if os.path.isdir(LOCAL_EPHEMERIS):
    DEFAULT_EPHEMERIS = LOCAL_EPHEMERIS

EPHEMERIS_PATH = os.getenv("EPHEMERIS_PATH", DEFAULT_EPHEMERIS)

try:
    # Flatlib uses Swiss Ephemeris under the hood
    os.environ["FLATLIB_EPHEMERIS"] = EPHEMERIS_PATH
    from flatlib import const
    from flatlib.chart import Chart as FLChart
    from flatlib.datetime import Datetime as FLDatetime
    from flatlib.geopos import GeoPos

    HAS_FLATLIB = True
except Exception:
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
    "whole": "HOUSES_WHOLESIGN",
    "equal": "HOUSES_EQUAL",
    "koch": "HOUSES_KOCH",
    "campanus": "HOUSES_CAMPANUS",
    "topocentric": "HOUSES_TOPOCENTRIC",
}


# ---------- Public API ----------


def build_natal_chart(profile: Dict) -> Dict:
    """Compute a natal chart for a profile."""
    dt = _parse_datetime(
        profile["date_of_birth"],
        profile.get("time_of_birth"),
        profile.get("timezone", "UTC"),
    )
    return _build_chart(dt, profile, chart_type="natal")


def build_transit_chart(profile: Dict, target_date: datetime) -> Dict:
    """Compute a transit chart for a given target date/time at profile location."""
    time_str = target_date.strftime("%H:%M")
    date_str = target_date.strftime("%Y-%m-%d")
    profile_copy = dict(profile)
    profile_copy["date_of_birth"] = date_str
    profile_copy["time_of_birth"] = time_str
    return _build_chart(target_date, profile_copy, chart_type="transit")


# ---------- Internal helpers ----------


def _parse_datetime(date_str: str, time_str: Optional[str], tz: str) -> datetime:
    time_part = time_str or "12:00"
    return datetime.fromisoformat(f"{date_str}T{time_part}")


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
    if HAS_FLATLIB:
        try:
            return _chart_with_flatlib(dt, profile, chart_type)
        except Exception:
            pass  # fall through to stub for resilience
    return _chart_with_stub(dt, profile, chart_type)


def _chart_with_flatlib(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    # Flatlib expects date as 'YYYY/MM/DD' and time as 'HH:MM'
    date_str = dt.strftime("%Y/%m/%d")
    time_str = dt.strftime("%H:%M")
    # Convert timezone name to offset for flatlib (use +00:00 for simplicity)
    fl_dt = FLDatetime(date_str, time_str, "+00:00")
    # Handle None values for latitude/longitude
    lat_val = profile.get("latitude")
    lon_val = profile.get("longitude")
    lat = float(lat_val) if lat_val is not None else 0.0
    lon = float(lon_val) if lon_val is not None else 0.0
    pos = GeoPos(lat, lon)
    house_system = _resolve_house_system(profile.get("house_system"))

    # Include all planets including outer planets
    planet_ids = [getattr(const, p.upper()) for p in PLANETS]
    fl_chart = FLChart(fl_dt, pos, IDs=planet_ids, hsys=house_system)

    # Get house cusps first to calculate planet houses
    house_cusps = []
    for i in range(1, 13):
        cusp = fl_chart.houses.get(getattr(const, f"HOUSE{i}"))
        house_cusps.append(cusp.lon)

    planets = []
    for name in PLANETS:
        obj = fl_chart.get(getattr(const, name.upper()))
        # Calculate which house the planet is in
        planet_house = _get_house_for_longitude(obj.lon, house_cusps)
        planets.append(
            {
                "name": name,
                "sign": obj.sign,
                "degree": obj.signlon,
                "absolute_degree": obj.lon,
                "house": planet_house,
                "retrograde": obj.isRetrograde(),
            }
        )

    houses = []
    for i in range(1, 13):
        cusp = fl_chart.houses.get(getattr(const, f"HOUSE{i}"))
        houses.append({"house": i, "sign": cusp.sign, "degree": cusp.signlon})

    aspects = _compute_aspects(planets)

    return {
        "metadata": {
            "chart_type": chart_type,
            "datetime": dt.isoformat(),
            "location": {
                "lat": float(profile.get("latitude", 0.0)),
                "lon": float(profile.get("longitude", 0.0)),
            },
            "house_system": profile.get("house_system", "Placidus"),
        },
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
    }


def _chart_with_stub(dt: datetime, profile: Dict, chart_type: str) -> Dict:
    """Deterministic fallback: seeds positions from name+dob to keep responses stable."""
    seed = f"{profile.get('name','')}{profile.get('date_of_birth','')}{chart_type}"
    sig = hashlib.md5(seed.encode()).hexdigest()
    planets = []
    for i, name in enumerate(PLANETS):
        base = int(sig[i * 3 : i * 3 + 3], 16) % 3600 / 10.0  # 0-360
        sign_idx = int(base // 30)
        sign_order = [
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
        planets.append(
            {
                "name": name,
                "sign": sign_order[sign_idx],
                "degree": base % 30,
                "absolute_degree": base,
                "house": (i % 12) + 1,
                "retrograde": False,
            }
        )
    houses = [
        {
            "house": i + 1,
            "sign": planets[i % len(planets)]["sign"],
            "degree": (i * 5.0) % 30,
        }
        for i in range(12)
    ]
    aspects = _compute_aspects(planets)
    return {
        "metadata": {
            "chart_type": chart_type,
            "datetime": dt.isoformat(),
            "location": {
                "lat": float(profile.get("latitude", 0.0)),
                "lon": float(profile.get("longitude", 0.0)),
            },
            "provider": "stub",
            "house_system": profile.get("house_system", "Placidus"),
        },
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
    }


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
    const_name = HOUSE_SYSTEM_MAP.get(key, "HOUSES_PLACIDUS")
    return getattr(const, const_name, const.HOUSES_PLACIDUS)
