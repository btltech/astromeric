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
from ..interpretation.translations import get_translation


def get_daily_guidance(
    natal_chart: Dict,
    transit_chart: Dict,
    numerology: Dict,
    scope: str = "daily",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: str = "UTC",
    lang: str = "en",
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
    num_guidance = _get_numerology_guidance(personal_day, lang=lang)
    
    # 2. Astrology Guidance (Transits)
    astro_guidance = _get_astrology_guidance(natal_chart, transit_chart, lang=lang)
    
    # 3. Color Guidance
    color_guidance = _get_color_guidance(personal_day, lang=lang)
    
    # 4. Power Hour (real planetary hours calculation)
    power_hour = _calculate_power_hour(
        natal_chart, 
        transit_chart,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        lang=lang
    )
    
    # 5. Retrograde Alerts
    retrogrades = detect_retrogrades(transit_chart)
    retrograde_warnings = _format_retrograde_warnings(retrogrades, lang)
    
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
        voc_avoid = get_translation(lang, "voc_avoid") if lang != "en" else ["Starting new projects", "Making major decisions"]
        voc_embrace = get_translation(lang, "voc_embrace") if lang != "en" else ["Routine tasks", "Meditation"]
        if voc_avoid:
            avoid_activities.extend(voc_avoid)
        if voc_embrace:
            embrace_activities.extend(voc_embrace)

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
            latitude, longitude, timezone, lang
        ) if latitude and longitude else None,
    }


def _get_numerology_guidance(day_number: int, lang: str = "en") -> Dict[str, List[str]]:
    """Returns avoid/embrace lists based on Personal Day Number."""
    if not day_number:
        return {"avoid": [], "embrace": []}
        
    # Use translation system if available, otherwise fallback to English defaults
    avoid_key = f"num_{day_number}_avoid"
    embrace_key = f"num_{day_number}_embrace"
    
    avoid = get_translation(lang, avoid_key)
    embrace = get_translation(lang, embrace_key)
    
    # Fallback for English if translation returns empty (or if keys missing)
    if not avoid and lang == "en":
        defaults = {
            1: ["Hesitation", "Following the crowd", "Procrastination"],
            2: ["Conflict", "Isolation", "Rushing decisions"],
            3: ["Gossip", "Scattering energy", "Isolation"],
            4: ["Laziness", "Shortcuts", "Disorganization"],
            5: ["Rigidity", "Routine", "Long-term commitments"],
            6: ["Neglect", "Selfishness", "Arguments at home"],
            7: ["Noise", "Superficiality", "Crowds"],
            8: ["Overspending", "Power struggles", "Gambling"],
            9: ["Holding grudges", "Starting new big projects", "Clutter"],
            11: ["Materialism", "Ignoring intuition"],
            22: ["Dreaming without doing", "Impracticality"],
            33: ["Self-neglect", "Overgiving"],
        }
        avoid = defaults.get(day_number, [])

    if not embrace and lang == "en":
        defaults = {
            1: ["Taking the lead", "Starting fresh", "Bold action"],
            2: ["Cooperation", "Patience", "Diplomacy"],
            3: ["Self-expression", "Socializing", "Creativity"],
            4: ["Hard work", "Planning", "Details"],
            5: ["Change", "Adventure", "Flexibility"],
            6: ["Family time", "Service", "Harmony"],
            7: ["Meditation", "Research", "Solitude"],
            8: ["Business", "Financial planning", "Ambition"],
            9: ["Letting go", "Charity", "Finishing tasks"],
            11: ["Inspiration", "Spiritual practice"],
            22: ["Building", "Large-scale planning"],
            33: ["Teaching", "Healing others"],
        }
        embrace = defaults.get(day_number, [])
        
    return {"avoid": avoid or [], "embrace": embrace or []}


def _get_astrology_guidance(natal: Dict, transit: Dict, lang: str = "en") -> Dict[str, List[str]]:
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
        element = ""
        if sign in ["Aries", "Leo", "Sagittarius"]:  # Fire Moons
            element = "fire"
        elif sign in ["Taurus", "Virgo", "Capricorn"]:  # Earth Moons
            element = "earth"
        elif sign in ["Gemini", "Libra", "Aquarius"]:  # Air Moons
            element = "air"
        elif sign in ["Cancer", "Scorpio", "Pisces"]:  # Water Moons
            element = "water"
            
        if element:
            avoid_key = f"moon_{element}_avoid"
            embrace_key = f"moon_{element}_embrace"
            
            moon_avoid = get_translation(lang, avoid_key)
            moon_embrace = get_translation(lang, embrace_key)
            
            if moon_avoid:
                avoid.extend(moon_avoid)
            elif lang == "en": # Fallback
                if element == "fire": avoid.append("Impulsive anger")
                elif element == "earth": avoid.append("Risky spending")
                elif element == "air": avoid.append("Miscommunication")
                elif element == "water": avoid.append("Suppressing emotions")
                
            if moon_embrace:
                embrace.extend(moon_embrace)
            elif lang == "en": # Fallback
                if element == "fire": embrace.append("Physical activity")
                elif element == "earth": embrace.append("Practical tasks")
                elif element == "air": embrace.append("Socializing")
                elif element == "water": embrace.append("Self-care")
    
    # Check for challenging aspects in transit
    aspects = transit.get("aspects", [])
    for aspect in aspects:
        if aspect.get("type") == "square":
            msg = get_translation(lang, "aspect_square_avoid")
            avoid.append(msg[0] if msg else "Forcing outcomes")
        if aspect.get("type") == "opposition":
            msg = get_translation(lang, "aspect_opposition_embrace")
            embrace.append(msg[0] if msg else "Finding balance")
    
    return {"avoid": list(set(avoid)), "embrace": list(set(embrace))}


def _get_color_guidance(day_number: int, lang: str = "en") -> Dict[str, List[Dict[str, str]]]:
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
        key = f"color_{name.lower().replace(' ', '_')}"
        trans = get_translation(lang, key)
        display_name = trans[0] if trans else name
        return {"name": display_name, "hex": COLOR_HEX.get(name, "#808080")}
    
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
    lang: str = "en",
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
        msg = get_translation(lang, "ph_location_error")
        return msg[0] if msg else "Check your location settings for accurate timing"
    
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        now = datetime.now()
    
    # Get all power hours for today
    power_hours = get_power_hours(
        now, latitude, longitude, timezone,
        favorable_planets=["Sun", "Jupiter", "Venus"]
    )
    
    hour_label = "hour" # Default
    if lang != "en":
        # Simple mapping for "hour" word if needed, or rely on full string translation
        # For now, we'll keep the structure simple
        pass

    # Find the next upcoming power hour
    for ph in power_hours:
        # Parse start time for comparison (simplified)
        if ph.get("is_day"):
            planet_name = ph['planet']
            # Ideally translate planet name here if we had a mapping
            return f"{ph['start']} - {ph['end']} ({planet_name} {hour_label})"
    
    # Return first power hour if none upcoming
    if power_hours:
        first = power_hours[0]
        planet_name = first['planet']
        return f"{first['start']} - {first['end']} ({planet_name} {hour_label})"
    
    msg = get_translation(lang, "ph_sunrise")
    return msg[0] if msg else "Sunrise - 7:00 AM (Sun hour)"


def _get_current_hour_info(
    latitude: Optional[float],
    longitude: Optional[float],
    timezone: str,
    lang: str = "en",
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
    
    quality_key = "neutral"
    suggestion_key = "neutral"
    
    if planet in ["Sun", "Jupiter", "Venus"]:
        quality_key = "favorable"
        suggestion_key = "favorable"
    elif planet in ["Saturn", "Mars"]:
        quality_key = "challenging"
        suggestion_key = "challenging"
        
    # Get translations
    quality_trans = get_translation(lang, f"ph_quality_{quality_key}")
    suggestion_trans = get_translation(lang, f"ph_suggestion_{suggestion_key}")
    
    quality = quality_trans[0] if quality_trans else ("Favorable" if quality_key == "favorable" else "Challenging" if quality_key == "challenging" else "Neutral")
    suggestion = suggestion_trans[0] if suggestion_trans else ("Good time for important actions" if suggestion_key == "favorable" else "Better for discipline and physical work" if suggestion_key == "challenging" else "Proceed with awareness")

    return {
        "planet": planet,
        "start": current_hour.get("start"),
        "end": current_hour.get("end"),
        "quality": quality,
        "suggestion": suggestion,
    }


def _format_retrograde_warnings(retrogrades: List[Dict], lang: str = "en") -> List[Dict]:
    """Format retrograde information for frontend display."""
    if not retrogrades:
        return []
    
    formatted = []
    for retro in retrogrades:
        # Here we would ideally translate the impact text if we had keys for it
        # For now we pass through the generated text
        formatted.append({
            "planet": retro["planet"],
            "sign": retro.get("sign", "Unknown"),
            "impact": retro.get("general_impact", ""),
            "house_impact": retro.get("house_impact"),
            "avoid": retro.get("activities_avoid", [])[:3],
            "embrace": retro.get("activities_embrace", [])[:3],
        })
    
    return formatted
