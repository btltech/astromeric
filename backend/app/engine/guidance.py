"""
guidance.py
-----------
Daily actionable guidance engine: Avoid/Embrace activities, Power Hours, 
Retrograde Alerts, Void-of-Course Moon tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from .planetary_timing import (
    get_current_planetary_hour,
    get_power_hours,
    detect_retrogrades,
    calculate_void_of_course_moon,
)


def get_daily_guidance(
    natal_chart: Dict,
    transit_chart: Dict,
    numerology: Dict,
    scope: str = "daily",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: str = "UTC",
) -> Dict:
    """
    Generates comprehensive daily actionable guidance.
    
    Includes:
    - Numerology-based activities to avoid/embrace
    - Astrology-based guidance from transits
    - Color guidance based on Personal Day
    - Power Hour calculation (real planetary hours)
    - Retrograde alerts with personalized impacts
    - Void-of-Course Moon warnings
    """
    
    # 1. Numerology Guidance
    personal_day = numerology.get("cycles", {}).get("personal_day", {}).get("number")
    num_guidance = _get_numerology_guidance(personal_day)
    
    # 2. Astrology Guidance (Transits)
    astro_guidance = _get_astrology_guidance(natal_chart, transit_chart)
    
    # 3. Color Guidance
    color_guidance = _get_color_guidance(personal_day)
    
    # 4. Power Hour (real planetary hours calculation)
    power_hour = _calculate_power_hour(
        natal_chart, 
        transit_chart,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )
    
    # 5. Retrograde Alerts
    retrogrades = detect_retrogrades(transit_chart)
    retrograde_warnings = _format_retrograde_warnings(retrogrades)
    
    # 6. Void-of-Course Moon
    voc_moon = calculate_void_of_course_moon(transit_chart)
    
    # Merge retrograde activities into avoid/embrace
    avoid_activities = list(set(num_guidance["avoid"] + astro_guidance["avoid"]))
    embrace_activities = list(set(num_guidance["embrace"] + astro_guidance["embrace"]))
    
    for retro in retrogrades:
        avoid_activities.extend(retro.get("activities_avoid", [])[:2])  # Limit to 2 per planet
        embrace_activities.extend(retro.get("activities_embrace", [])[:2])
    
    # Add VOC Moon warning to avoid if applicable
    if voc_moon.get("is_void"):
        avoid_activities.append("Starting new projects")
        avoid_activities.append("Making major decisions")
        embrace_activities.append("Routine tasks")
        embrace_activities.append("Meditation")

    return {
        "avoid": {
            "activities": list(set(avoid_activities)),
            "colors": color_guidance["avoid"],
            "numbers": _get_challenge_numbers(numerology),
        },
        "embrace": {
            "activities": list(set(embrace_activities)),
            "colors": color_guidance["embrace"],
            "time": power_hour,
        },
        "retrogrades": retrograde_warnings,
        "void_of_course_moon": voc_moon,
        "current_planetary_hour": _get_current_hour_info(
            latitude, longitude, timezone
        ) if latitude and longitude else None,
    }


def _get_numerology_guidance(day_number: int) -> Dict[str, List[str]]:
    """Returns avoid/embrace lists based on Personal Day Number."""
    if not day_number:
        return {"avoid": [], "embrace": []}
        
    rules = {
        1: {
            "avoid": ["Hesitation", "Following the crowd", "Procrastination"],
            "embrace": ["Taking the lead", "Starting fresh", "Bold action"]
        },
        2: {
            "avoid": ["Conflict", "Isolation", "Rushing decisions"],
            "embrace": ["Cooperation", "Patience", "Diplomacy"]
        },
        3: {
            "avoid": ["Gossip", "Scattering energy", "Isolation"],
            "embrace": ["Self-expression", "Socializing", "Creativity"]
        },
        4: {
            "avoid": ["Laziness", "Shortcuts", "Disorganization"],
            "embrace": ["Hard work", "Planning", "Details"]
        },
        5: {
            "avoid": ["Rigidity", "Routine", "Long-term commitments"],
            "embrace": ["Change", "Adventure", "Flexibility"]
        },
        6: {
            "avoid": ["Neglect", "Selfishness", "Arguments at home"],
            "embrace": ["Family time", "Service", "Harmony"]
        },
        7: {
            "avoid": ["Noise", "Superficiality", "Crowds"],
            "embrace": ["Meditation", "Research", "Solitude"]
        },
        8: {
            "avoid": ["Overspending", "Power struggles", "Gambling"],
            "embrace": ["Business", "Financial planning", "Ambition"]
        },
        9: {
            "avoid": ["Holding grudges", "Starting new big projects", "Clutter"],
            "embrace": ["Letting go", "Charity", "Finishing tasks"]
        },
        11: {
            "avoid": ["Materialism", "Ignoring intuition"],
            "embrace": ["Inspiration", "Spiritual practice"]
        },
        22: {
            "avoid": ["Dreaming without doing", "Impracticality"],
            "embrace": ["Building", "Large-scale planning"]
        },
        33: {
            "avoid": ["Self-neglect", "Overgiving"],
            "embrace": ["Teaching", "Healing others"]
        },
    }
    return rules.get(day_number, {"avoid": [], "embrace": []})


def _get_astrology_guidance(natal: Dict, transit: Dict) -> Dict[str, List[str]]:
    """
    Analyzes transits to find specific warnings based on Moon sign
    and any challenging aspects.
    """
    avoid = []
    embrace = []
    
    transit_moon = next(
        (p for p in transit.get("planets", []) if p["name"] == "Moon"), 
        None
    )
    
    if transit_moon:
        sign = transit_moon.get("sign", "")
        if sign in ["Aries", "Leo", "Sagittarius"]:  # Fire Moons
            avoid.append("Impulsive anger")
            embrace.append("Physical activity")
        elif sign in ["Taurus", "Virgo", "Capricorn"]:  # Earth Moons
            avoid.append("Risky spending")
            embrace.append("Practical tasks")
        elif sign in ["Gemini", "Libra", "Aquarius"]:  # Air Moons
            avoid.append("Miscommunication")
            embrace.append("Socializing")
        elif sign in ["Cancer", "Scorpio", "Pisces"]:  # Water Moons
            avoid.append("Suppressing emotions")
            embrace.append("Self-care")
    
    # Check for challenging aspects in transit
    aspects = transit.get("aspects", [])
    for aspect in aspects:
        if aspect.get("type") == "square":
            avoid.append("Forcing outcomes")
        if aspect.get("type") == "opposition":
            embrace.append("Finding balance")
    
    return {"avoid": avoid, "embrace": embrace}


def _get_color_guidance(day_number: int) -> Dict[str, List[Dict[str, str]]]:
    """Returns lucky and avoid colors based on numerology with hex values."""
    # Color name to hex mapping for CSS compatibility
    COLOR_HEX = {
        "Red": "#E53935",
        "Gold": "#FFD700",
        "Black": "#1A1A1A",
        "Grey": "#808080",
        "White": "#FFFFFF",
        "Silver": "#C0C0C0",
        "Orange": "#FF9800",
        "Bright Orange": "#FF5722",
        "Yellow": "#FFEB3B",
        "Purple": "#9C27B0",
        "Dark Blue": "#1565C0",
        "Green": "#4CAF50",
        "Brown": "#795548",
        "Pastels": "#E1BEE7",  # Light lavender as representative pastel
        "Blue": "#2196F3",
        "Turquoise": "#00BCD4",
        "Heavy Black": "#0D0D0D",
        "Indigo": "#3F51B5",
        "Pink": "#E91E63",
        "Violet": "#7B1FA2",
        "Bright Yellow": "#FFFF00",
        "Dark Brown": "#4E342E",
        "Coral": "#FF7043",
        "Dark colors": "#37474F",  # Dark blue-grey as representative
    }
    
    def to_color_obj(name: str) -> Dict[str, str]:
        return {"name": name, "hex": COLOR_HEX.get(name, "#808080")}
    
    maps = {
        1: {"embrace": ["Red", "Gold"], "avoid": ["Black", "Grey"]},
        2: {"embrace": ["White", "Silver"], "avoid": ["Red", "Bright Orange"]},
        3: {"embrace": ["Yellow", "Purple"], "avoid": ["Dark Blue"]},
        4: {"embrace": ["Green", "Brown"], "avoid": ["White", "Pastels"]},
        5: {"embrace": ["Blue", "Turquoise"], "avoid": ["Heavy Black"]},
        6: {"embrace": ["Indigo", "Pink"], "avoid": ["Red"]},
        7: {"embrace": ["Violet", "Grey"], "avoid": ["Bright Yellow"]},
        8: {"embrace": ["Black", "Dark Blue"], "avoid": ["Pastels"]},
        9: {"embrace": ["Gold", "Pastels"], "avoid": ["Black"]},
        11: {"embrace": ["Silver", "White"], "avoid": ["Dark Brown"]},
        22: {"embrace": ["Gold", "Green"], "avoid": ["Grey"]},
        33: {"embrace": ["Turquoise", "Coral"], "avoid": ["Dark colors"]},
    }
    
    result = maps.get(day_number, {"embrace": ["Grey"], "avoid": []})
    return {
        "embrace": [to_color_obj(c) for c in result["embrace"]],
        "avoid": [to_color_obj(c) for c in result["avoid"]],
    }


def _get_challenge_numbers(numerology: Dict) -> List[int]:
    """Extracts challenge numbers from numerology profile."""
    challenges = numerology.get("challenges", [])
    return [c["number"] for c in challenges if isinstance(c, dict) and "number" in c]


def _calculate_power_hour(
    natal: Dict, 
    transit: Dict,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: str = "UTC",
) -> str:
    """
    Calculates the best 'Power Hour' for the day using planetary hours.
    Returns the first favorable hour (Sun, Jupiter, or Venus ruled).
    """
    if latitude is None or longitude is None:
        # Fallback: extract from chart metadata
        metadata = natal.get("metadata", {})
        location = metadata.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lon")
    
    if latitude is None or longitude is None:
        return "Check your location settings for accurate timing"
    
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        now = datetime.now()
    
    # Get all power hours for today
    power_hours = get_power_hours(
        now, latitude, longitude, timezone,
        favorable_planets=["Sun", "Jupiter", "Venus"]
    )
    
    # Find the next upcoming power hour
    for ph in power_hours:
        # Parse start time for comparison (simplified)
        if ph.get("is_day"):
            return f"{ph['start']} - {ph['end']} ({ph['planet']} hour)"
    
    # Return first power hour if none upcoming
    if power_hours:
        first = power_hours[0]
        return f"{first['start']} - {first['end']} ({first['planet']} hour)"
    
    return "Sunrise - 7:00 AM (Sun hour)"


def _get_current_hour_info(
    latitude: Optional[float],
    longitude: Optional[float],
    timezone: str,
) -> Optional[Dict]:
    """Get information about the current planetary hour."""
    if latitude is None or longitude is None:
        return None
    
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        now = datetime.now()
    
    current_hour = get_current_planetary_hour(now, latitude, longitude, timezone)
    
    # Add quality assessment
    planet = current_hour.get("planet", "")
    if planet in ["Sun", "Jupiter", "Venus"]:
        quality = "Favorable"
        suggestion = "Good time for important actions"
    elif planet in ["Saturn", "Mars"]:
        quality = "Challenging"
        suggestion = "Better for discipline and physical work"
    else:
        quality = "Neutral"
        suggestion = "Proceed with awareness"
    
    return {
        "planet": planet,
        "start": current_hour.get("start"),
        "end": current_hour.get("end"),
        "quality": quality,
        "suggestion": suggestion,
    }


def _format_retrograde_warnings(retrogrades: List[Dict]) -> List[Dict]:
    """Format retrograde information for frontend display."""
    if not retrogrades:
        return []
    
    formatted = []
    for retro in retrogrades:
        formatted.append({
            "planet": retro["planet"],
            "sign": retro.get("sign", "Unknown"),
            "impact": retro.get("general_impact", ""),
            "house_impact": retro.get("house_impact"),
            "avoid": retro.get("activities_avoid", [])[:3],
            "embrace": retro.get("activities_embrace", [])[:3],
        })
    
    return formatted
