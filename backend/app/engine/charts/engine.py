from __future__ import annotations

import hashlib
import os
from typing import Dict, List, Optional, Tuple

from ..astrology import get_zodiac_sign
from .models import Aspect, Chart, ChartRequest, HouseCusp, PlanetPosition

try:
    from flatlib import const as fl_const
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

# Degrees and labels for classic Ptolemaic aspects
ASPECT_ANGLES: Dict[str, float] = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}

# Max orb per aspect type (can be tuned or externalised later)
ASPECT_ORBS: Dict[str, float] = {
    "conjunction": 7.0,
    "sextile": 3.5,
    "square": 5.5,
    "trine": 5.5,
    "opposition": 7.0,
}


def _deg_diff(a: float, b: float) -> float:
    """Smallest angular distance between two absolute degrees."""
    diff = abs((a - b + 180) % 360 - 180)
    return diff


class ChartEngine:
    """Facade for computing charts with a pluggable ephemeris provider."""

    def __init__(self, prefer_external: bool = True, force_stub: Optional[bool] = None):
        env_force_stub = os.getenv("ASTRO_USE_STUB", "").lower() in ["1", "true", "yes"]
        self.use_flatlib = prefer_external and HAS_FLATLIB and not env_force_stub

    def compute_chart(self, request: ChartRequest) -> Chart:
        if self.use_flatlib:
            try:
                return self._compute_with_flatlib(request)
            except Exception:
                # Fall back gracefully rather than fail the request.
                pass
        return self._compute_with_stub(request)

    def _compute_with_flatlib(self, request: ChartRequest) -> Chart:
        fl_dt = FLDatetime(
            request.datetime.year,
            request.datetime.month,
            request.datetime.day,
            request.datetime.hour,
            request.datetime.minute,
            request.datetime.second,
            request.location.timezone,
        )
        fl_pos = GeoPos(str(request.location.latitude), str(request.location.longitude))
        fl_chart = FLChart(fl_dt, fl_pos, hsys=request.house_system)

        planets: List[PlanetPosition] = []
        for planet_name in PLANETS:
            obj = fl_chart.get(getattr(fl_const, planet_name.upper()))
            planets.append(
                PlanetPosition(
                    name=planet_name,
                    sign=obj.sign,
                    degree=obj.signlon,
                    absolute_degree=obj.lon,
                    house=int(obj.house),
                    retrograde=obj.speed < 0,
                    speed=obj.speed,
                )
            )

        houses: List[HouseCusp] = []
        for i in range(1, 13):
            cusp = fl_chart.houses.get(i)
            houses.append(
                HouseCusp(
                    house_number=i,
                    cusp_sign=cusp.sign,
                    cusp_degree=cusp.signlon,
                )
            )

        aspects = self._compute_aspects(planets)

        return Chart(
            chart_type=request.chart_type,
            datetime=request.datetime,
            location=request.location,
            planets=planets,
            houses=houses,
            aspects=aspects,
            metadata={"provider": "flatlib"},
        )

    def _compute_with_stub(self, request: ChartRequest) -> Chart:
        """Deterministic fallback when no external ephemeris is available."""
        seed = self._make_seed(request)
        sign = get_zodiac_sign(request.datetime.date().isoformat())

        planets: List[PlanetPosition] = []
        for idx, planet in enumerate(PLANETS):
            hashed = int(hashlib.md5(f"{seed}{planet}".encode()).hexdigest(), 16)
            degree = (hashed % 3000) / 10.0  # 0-300 degrees
            absolute_degree = degree % 360
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
            sign_idx = int(absolute_degree // 30) % 12
            planet_sign = sign_order[sign_idx]
            house = (idx % 12) + 1
            planets.append(
                PlanetPosition(
                    name=planet,
                    sign=planet_sign,
                    degree=absolute_degree % 30,
                    absolute_degree=absolute_degree,
                    house=house,
                    retrograde=False,
                )
            )

        houses = [
            HouseCusp(
                house_number=i,
                cusp_sign=sign,
                cusp_degree=((i - 1) * 5.0) % 30,
            )
            for i in range(1, 13)
        ]

        aspects = self._compute_aspects(planets)

        return Chart(
            chart_type=request.chart_type,
            datetime=request.datetime,
            location=request.location,
            planets=planets,
            houses=houses,
            aspects=aspects,
            metadata={"provider": "stub"},
        )

    def build_synastry(self, chart_a: Chart, chart_b: Chart) -> List[Aspect]:
        """Cross-aspects between two charts."""
        synastry: List[Aspect] = []
        for pa in chart_a.planets:
            for pb in chart_b.planets:
                diff = _deg_diff(pa.absolute_degree, pb.absolute_degree)
                closest_aspect, orb = self._closest_aspect(diff)
                if closest_aspect and orb <= ASPECT_ORBS[closest_aspect]:
                    synastry.append(
                        Aspect(
                            planet_a=pa.name,
                            planet_b=pb.name,
                            aspect_type=closest_aspect,
                            orb=round(orb, 2),
                            strength_score=self._score_aspect(closest_aspect, orb),
                            house_a=pa.house,
                            house_b=pb.house,
                        )
                    )
        return synastry

    def _compute_aspects(self, planets: List[PlanetPosition]) -> List[Aspect]:
        aspects: List[Aspect] = []
        for i, pa in enumerate(planets):
            for pb in planets[i + 1 :]:
                diff = _deg_diff(pa.absolute_degree, pb.absolute_degree)
                aspect_type, orb = self._closest_aspect(diff)
                if aspect_type and orb <= ASPECT_ORBS[aspect_type]:
                    aspects.append(
                        Aspect(
                            planet_a=pa.name,
                            planet_b=pb.name,
                            aspect_type=aspect_type,
                            orb=round(orb, 2),
                            strength_score=self._score_aspect(aspect_type, orb),
                            house_a=pa.house,
                            house_b=pb.house,
                        )
                    )
        return aspects

    def _closest_aspect(self, diff: float) -> Tuple[Optional[str], float]:
        closest = None
        min_orb = 999.0
        for aspect_name, exact in ASPECT_ANGLES.items():
            orb = abs(diff - exact)
            if orb < min_orb:
                min_orb = orb
                closest = aspect_name
        return closest, min_orb

    def _score_aspect(self, aspect_type: str, orb: float) -> float:
        max_orb = ASPECT_ORBS.get(aspect_type, 6.0)
        base = 1.0 - min(orb / max_orb, 1.0)
        weight = 1.2 if aspect_type in ["trine", "sextile"] else 1.0
        weight = 1.3 if aspect_type in ["conjunction", "opposition"] else weight
        return round(base * weight, 3)

    def _make_seed(self, request: ChartRequest) -> str:
        loc = request.location
        return f"{request.chart_type}-{request.datetime.isoformat()}-{loc.latitude}-{loc.longitude}"
