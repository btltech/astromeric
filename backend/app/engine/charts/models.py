from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Location:
    latitude: float
    longitude: float
    timezone: str


@dataclass
class PlanetPosition:
    name: str
    sign: str
    degree: float
    absolute_degree: float
    house: Optional[int] = None
    retrograde: bool = False
    speed: Optional[float] = None


@dataclass
class HouseCusp:
    house_number: int
    cusp_sign: str
    cusp_degree: float


@dataclass
class Aspect:
    planet_a: str
    planet_b: str
    aspect_type: str
    orb: float
    strength_score: float
    house_a: Optional[int] = None
    house_b: Optional[int] = None


@dataclass
class ChartRequest:
    chart_type: str  # natal | transit | progressed | return
    datetime: datetime
    location: Location
    house_system: str = "Placidus"
    reference_chart: Optional["Chart"] = None  # used for transit comparison


@dataclass
class Chart:
    chart_type: str
    datetime: datetime
    location: Location
    planets: List[PlanetPosition] = field(default_factory=list)
    houses: List[HouseCusp] = field(default_factory=list)
    aspects: List[Aspect] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
