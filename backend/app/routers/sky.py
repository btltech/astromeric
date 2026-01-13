from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..chart_service import PLANETS
from ..schemas import ApiResponse, ResponseStatus

try:
    import swisseph as swe
except ImportError:
    swe = None

router = APIRouter(prefix="/v2/sky", tags=["Sky"])

class PlanetPosition(BaseModel):
    name: str
    x: float
    y: float
    z: float
    distance: float  # in AU
    color: str

# Artistic colors for the planets in 3D
PLANET_COLORS = {
    "Sun": "#ffcc33",
    "Mercury": "#95a5a6",
    "Venus": "#e67e22",
    "Earth": "#3498db",
    "Moon": "#ecf0f1",
    "Mars": "#e74c3c",
    "Jupiter": "#f39c12",
    "Saturn": "#f1c40f",
    "Uranus": "#1abc9c",
    "Neptune": "#2980b9",
    "Pluto": "#7f8c8d",
}

# Swiss Ephemeris ID mappings
SWE_MAP = {
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
}

@router.get("/planets", response_model=ApiResponse[List[PlanetPosition]])
async def get_sky_planets(request: Request) -> ApiResponse[List[PlanetPosition]]:
    """
    Get current heliocentric positions of all planets for 3D visualization.
    Returns Cartesian (X, Y, Z) coordinates in astronomical units (AU).
    """
    request_id = request.state.request_id
    
    if not swe:
        return ApiResponse(
            status=ResponseStatus.ERROR,
            message="Swiss Ephemeris not available",
            request_id=request_id
        )

    now = datetime.now(timezone.utc)
    # Convert to Julian Day
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
    
    positions = []
    
    # We want Heliocentric positions for the 3D model (orbits around the sun)
    flags = swe.FLG_HELCTR | swe.FLG_XYZ
    
    for name in PLANETS:
        if name not in SWE_MAP:
            continue
            
        swe_id = SWE_MAP[name]
        try:
            # swe.calc_ut returns (res, flag)
            # res is [x, y, z, vx, vy, vz]
            res, _ = swe.calc_ut(jd, swe_id, flags)
            
            x, y, z = res[0], res[1], res[2]
            dist = (x**2 + y**2 + z**2)**0.5
            
            positions.append(PlanetPosition(
                name=name,
                x=float(x),
                y=float(y),
                z=float(z),
                distance=float(dist),
                color=PLANET_COLORS.get(name, "#ffffff")
            ))
        except Exception:
            continue
            
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=positions,
        message="Current planet positions retrieved",
        request_id=request_id
    )
