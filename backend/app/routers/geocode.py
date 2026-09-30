"""
API v2 - Geocoding helpers
The IANA timezone for a birthplace, so birth times are read in local time.
"""

from fastapi import APIRouter, Query
from starlette.concurrency import run_in_threadpool

from ..geocode_service import estimate_timezone_from_longitude, fetch_iana_timezone

router = APIRouter(prefix="/v2/geocode", tags=["Geocode"])

# Answers for places already looked up. Only real answers are kept, so a
# brief outage of the lookup service is never remembered.
_cache: dict[tuple[float, float], str] = {}
_CACHE_LIMIT = 5000


@router.get("/timezone")
async def timezone_for_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """IANA timezone (for example "Africa/Lagos") for a point.

    ``estimated`` is true when the lookup service couldn't answer and the
    zone was guessed from longitude (no daylight saving).
    """
    # About 1 km: never changes the answer in practice, and repeat lookups
    # for a city come from the cache.
    key = (round(lat, 2), round(lon, 2))
    tz = _cache.get(key)
    if tz is None:
        tz = await run_in_threadpool(fetch_iana_timezone, *key)
        if tz and len(_cache) < _CACHE_LIMIT:
            _cache[key] = tz
    if tz:
        return {"latitude": lat, "longitude": lon, "timezone": tz, "estimated": False}
    return {
        "latitude": lat,
        "longitude": lon,
        "timezone": estimate_timezone_from_longitude(lon),
        "estimated": True,
    }
