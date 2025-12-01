"""
geocode_service.py
------------------
Location geocoding and timezone lookup using free APIs.
- Nominatim (OpenStreetMap) for geocoding
- TimeZoneDB or calculation for timezone
"""
from __future__ import annotations

import httpx

# Free timezone API (optional, requires API key)
TIMEZONEDB_API_KEY = None  # Set via env if you have one


def estimate_timezone_from_longitude(lon: float) -> str:
    """
    Estimate timezone from longitude.
    Each 15° of longitude = 1 hour offset from UTC.
    """
    offset_hours = round(lon / 15)
    if offset_hours == 0:
        return "UTC"
    return f"Etc/GMT{'+' if offset_hours < 0 else '-'}{abs(offset_hours)}"


def get_iana_timezone(lat: float, lon: float) -> str:
    """
    Get IANA timezone from coordinates.
    Uses timeapi.io (free, no key required) or falls back to estimation.
    """
    try:
        # Try free timeapi.io
        url = (
            f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}"
        )
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("timeZone", estimate_timezone_from_longitude(lon))
    except Exception:
        pass

    # Fallback to longitude-based estimation
    return estimate_timezone_from_longitude(lon)


async def search_locations(query: str, limit: int = 5) -> list[dict]:
    """
    Search for locations using Nominatim (OpenStreetMap).
    Returns list of locations with lat, lon, display_name.
    """
    if len(query) < 2:
        return []

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": "1",
        "limit": str(limit),
        "accept-language": "en",
    }
    headers = {"User-Agent": "AstroNumerology/1.0 (contact@example.com)"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        results = resp.json()

    locations = []
    for r in results:
        addr = r.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or ""
        country = addr.get("country", "")

        locations.append(
            {
                "display_name": r.get("display_name", ""),
                "city": city,
                "country": country,
                "latitude": float(r.get("lat", 0)),
                "longitude": float(r.get("lon", 0)),
            }
        )

    return locations


def geocode_sync(query: str, limit: int = 5) -> list[dict]:
    """Synchronous version of location search."""
    if len(query) < 2:
        return []

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": "1",
        "limit": str(limit),
        "accept-language": "en",
    }
    headers = {"User-Agent": "AstroNumerology/1.0"}

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        results = resp.json()

    locations = []
    for r in results:
        addr = r.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or ""
        country = addr.get("country", "")
        lat = float(r.get("lat", 0))
        lon = float(r.get("lon", 0))

        locations.append(
            {
                "display_name": r.get("display_name", ""),
                "city": city,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "timezone": get_iana_timezone(lat, lon),
            }
        )

    return locations
