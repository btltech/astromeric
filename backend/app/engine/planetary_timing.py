"""
planetary_timing.py
-------------------
Advanced timing calculations: Planetary Hours, Void-of-Course Moon, Retrograde detection.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from ..interpretation.translations import get_translation

# Chaldean order of planets (traditional planetary hours sequence)
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Day rulers: Sunday=Sun(3), Monday=Moon(6), Tuesday=Mars(2), etc.
DAY_RULERS = {
    0: 3,  # Monday -> Moon (index 6 in Chaldean)
    1: 2,  # Tuesday -> Mars
    2: 5,  # Wednesday -> Mercury
    3: 1,  # Thursday -> Jupiter
    4: 4,  # Friday -> Venus
    5: 0,  # Saturday -> Saturn
    6: 3,  # Sunday -> Sun
}

# Zodiac signs in order
ZODIAC_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Major aspects and their orbs for VOC calculation
MAJOR_ASPECTS = {
    0: 8,     # Conjunction
    60: 4,    # Sextile
    90: 6,    # Square
    120: 6,   # Trine
    180: 8,   # Opposition
}

# Planetary keywords for personalized retrograde impact
RETROGRADE_IMPACTS = {
    "Mercury": {
        "general": "Communication delays, tech issues, revisiting plans",
        "houses": {
            1: "Self-expression may be misunderstood",
            2: "Financial paperwork needs extra review",
            3: "Local travel snags, sibling miscommunication",
            4: "Home repairs delayed, family misunderstandings",
            5: "Creative blocks, dating confusion",
            6: "Health paperwork, work routine disruptions",
            7: "Partnership discussions need patience",
            8: "Tax/insurance delays, deep conversations stall",
            9: "Travel plans change, study delays",
            10: "Career communications need clarity",
            11: "Friend miscommunications, group project delays",
            12: "Hidden matters surface, dreams vivid",
        },
        "activities_avoid": ["Signing contracts", "Major purchases", "Starting new ventures"],
        "activities_embrace": ["Review past work", "Reconnect with old friends", "Edit and refine"],
    },
    "Venus": {
        "general": "Relationship reviews, beauty regrets, past lovers resurface",
        "houses": {
            1: "Self-image fluctuations",
            2: "Money values reassessed",
            3: "Harmony in communication tested",
            4: "Family love patterns examined",
            5: "Romance from past returns",
            6: "Workplace relationships reviewed",
            7: "Partnership commitments questioned",
            8: "Intimate sharing patterns examined",
            9: "Long-distance love tested",
            10: "Public image and likability reviewed",
            11: "Friendships re-evaluated",
            12: "Hidden affections surface",
        },
        "activities_avoid": ["Major beauty changes", "New relationships", "Luxury purchases"],
        "activities_embrace": ["Reconnect with exes (if healthy)", "Reassess values", "Self-love practices"],
    },
    "Mars": {
        "general": "Energy dips, frustration, revisiting old conflicts",
        "houses": {
            1: "Personal drive fluctuates",
            2: "Income efforts stall",
            3: "Communication aggression reviewed",
            4: "Home conflicts resurface",
            5: "Creative drive inconsistent",
            6: "Work energy variable",
            7: "Partner conflicts revisited",
            8: "Power struggles examined",
            9: "Adventure plans delayed",
            10: "Career ambition reviewed",
            11: "Group dynamics tested",
            12: "Subconscious anger surfaces",
        },
        "activities_avoid": ["Starting conflicts", "Major physical endeavors", "Impulsive actions"],
        "activities_embrace": ["Finish old projects", "Strategic planning", "Physical rest"],
    },
    "Jupiter": {
        "general": "Growth slows, internal expansion, reviewing beliefs",
        "activities_avoid": ["Major expansions", "Legal matters", "Over-promising"],
        "activities_embrace": ["Internal growth", "Studying philosophy", "Gratitude practices"],
    },
    "Saturn": {
        "general": "Structure review, past karma resurfaces, delayed results",
        "activities_avoid": ["Major commitments", "New responsibilities"],
        "activities_embrace": ["Completing old obligations", "Reviewing boundaries"],
    },
}


def calculate_sunrise_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
) -> Tuple[datetime, datetime]:
    """
    Calculate sunrise and sunset for a given date and location.
    Uses astronomical algorithms for accuracy.
    """
    try:
        from astral import LocationInfo
        from astral.sun import sun
        
        location = LocationInfo(
            name="Location",
            region="",
            timezone=timezone,
            latitude=latitude,
            longitude=longitude
        )
        
        s = sun(location.observer, date=date.date(), tzinfo=ZoneInfo(timezone))
        return s["sunrise"], s["sunset"]
    except ImportError:
        # Fallback: approximate sunrise/sunset (6 AM / 6 PM)
        tz = ZoneInfo(timezone) if timezone else None
        sunrise = datetime(date.year, date.month, date.day, 6, 0, tzinfo=tz)
        sunset = datetime(date.year, date.month, date.day, 18, 0, tzinfo=tz)
        return sunrise, sunset
    except Exception:
        # Any other error, use defaults
        tz = ZoneInfo(timezone) if timezone else None
        sunrise = datetime(date.year, date.month, date.day, 6, 0, tzinfo=tz)
        sunset = datetime(date.year, date.month, date.day, 18, 0, tzinfo=tz)
        return sunrise, sunset


def calculate_planetary_hours(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
) -> List[Dict]:
    """
    Calculate all 24 planetary hours for a given day.
    Returns list of dicts with start, end, planet, and whether it's a day/night hour.
    """
    sunrise, sunset = calculate_sunrise_sunset(date, latitude, longitude, timezone)
    
    # Calculate next day's sunrise for night hours
    next_day = date + timedelta(days=1)
    next_sunrise, _ = calculate_sunrise_sunset(next_day, latitude, longitude, timezone)
    
    # Day length and night length
    day_length = (sunset - sunrise).total_seconds()
    night_length = (next_sunrise - sunset).total_seconds()
    
    # Each day/night hour duration
    day_hour_length = day_length / 12
    night_hour_length = night_length / 12
    
    # Get day ruler (starting planet for the day)
    weekday = date.weekday()
    start_index = DAY_RULERS.get(weekday, 3)  # Default to Sun
    
    hours = []
    
    # Calculate 12 day hours
    for i in range(12):
        planet_index = (start_index + i) % 7
        planet = CHALDEAN_ORDER[planet_index]
        start = sunrise + timedelta(seconds=i * day_hour_length)
        end = sunrise + timedelta(seconds=(i + 1) * day_hour_length)
        hours.append({
            "hour_number": i + 1,
            "planet": planet,
            "start": start.strftime("%I:%M %p"),
            "end": end.strftime("%I:%M %p"),
            "start_dt": start,
            "end_dt": end,
            "is_day": True,
        })
    
    # Calculate 12 night hours (continue from where day left off)
    for i in range(12):
        planet_index = (start_index + 12 + i) % 7
        planet = CHALDEAN_ORDER[planet_index]
        start = sunset + timedelta(seconds=i * night_hour_length)
        end = sunset + timedelta(seconds=(i + 1) * night_hour_length)
        hours.append({
            "hour_number": i + 13,
            "planet": planet,
            "start": start.strftime("%I:%M %p"),
            "end": end.strftime("%I:%M %p"),
            "start_dt": start,
            "end_dt": end,
            "is_day": False,
        })
    
    return hours


def get_current_planetary_hour(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
) -> Dict:
    """Get the current planetary hour for the given datetime."""
    hours = calculate_planetary_hours(date, latitude, longitude, timezone)
    
    # Make date timezone-aware if not already
    if date.tzinfo is None:
        date = date.replace(tzinfo=ZoneInfo(timezone))
    
    for hour in hours:
        if hour["start_dt"] <= date < hour["end_dt"]:
            return {
                "planet": hour["planet"],
                "start": hour["start"],
                "end": hour["end"],
                "is_day": hour["is_day"],
            }
    
    # Default to first hour if not found
    return {
        "planet": hours[0]["planet"] if hours else "Sun",
        "start": hours[0]["start"] if hours else "6:00 AM",
        "end": hours[0]["end"] if hours else "7:00 AM",
        "is_day": True,
    }


def get_power_hours(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str = "UTC",
    favorable_planets: Optional[List[str]] = None
) -> List[Dict]:
    """
    Get the 'power hours' for the day - hours ruled by favorable planets.
    Default favorable planets: Sun, Jupiter, Venus (benefics and luminary)
    """
    if favorable_planets is None:
        favorable_planets = ["Sun", "Jupiter", "Venus"]
    
    hours = calculate_planetary_hours(date, latitude, longitude, timezone)
    
    power_hours = [
        {
            "planet": h["planet"],
            "start": h["start"],
            "end": h["end"],
            "is_day": h["is_day"],
        }
        for h in hours
        if h["planet"] in favorable_planets
    ]
    
    return power_hours


def detect_retrogrades(transit_chart: Dict, lang: str = "en") -> List[Dict]:
    """
    Detect retrograde planets from transit chart data.
    Returns list of retrograde planet info with personalized impacts.
    """
    retrogrades = []
    
    planets = transit_chart.get("planets", [])
    for planet in planets:
        if planet.get("retrograde", False):
            name = planet["name"]
            impact_data = RETROGRADE_IMPACTS.get(name, {})
            
            # Localize general impact
            general_key = f"retro_{name.lower()}_general"
            general_trans = get_translation(lang, general_key)
            general_impact = general_trans[0] if general_trans else impact_data.get("general", f"{name} energy turned inward")
            
            # Localize avoid/embrace
            avoid_key = f"retro_{name.lower()}_avoid"
            embrace_key = f"retro_{name.lower()}_embrace"
            
            avoid_trans = get_translation(lang, avoid_key)
            embrace_trans = get_translation(lang, embrace_key)
            
            activities_avoid = avoid_trans if avoid_trans else impact_data.get("activities_avoid", [])
            activities_embrace = embrace_trans if embrace_trans else impact_data.get("activities_embrace", [])
            
            retrograde_info = {
                "planet": name,
                "sign": planet.get("sign", "Unknown"),
                "degree": planet.get("degree", 0),
                "general_impact": general_impact,
                "activities_avoid": activities_avoid,
                "activities_embrace": activities_embrace,
            }
            
            # Add house-specific impact if available
            house = planet.get("house")
            if house:
                house_impact = None
                # Try translation first
                house_key = f"retro_{name.lower()}_house_{house}"
                house_trans = get_translation(lang, house_key)
                
                if house_trans:
                    house_impact = house_trans[0]
                elif "houses" in impact_data:
                    house_impact = impact_data["houses"].get(house)
                
                if house_impact:
                    retrograde_info["house_impact"] = house_impact
                    retrograde_info["house"] = house
            
            retrogrades.append(retrograde_info)
    
    return retrogrades


def calculate_void_of_course_moon(transit_chart: Dict, lang: str = "en") -> Dict:
    """
    Calculate if the Moon is void-of-course (VOC).
    Moon is VOC when it makes no major applying aspects before leaving its current sign.
    
    Returns:
        - is_void: bool
        - current_sign: str
        - last_aspect: dict (if any)
        - void_until: approximate time when Moon enters next sign (if calculable)
        - advice: str
    """
    planets = transit_chart.get("planets", [])
    moon = next((p for p in planets if p["name"] == "Moon"), None)
    
    if not moon:
        return {
            "is_void": False,
            "current_sign": "Unknown",
            "advice": "Moon position unavailable",
        }
    
    moon_sign = moon.get("sign", "Aries")
    moon_degree = moon.get("absolute_degree", 0)
    moon_sign_degree = moon.get("degree", 0)  # Degree within sign (0-30)
    
    # Check for applying aspects (Moon is faster than all other planets)
    # An aspect is "applying" if the Moon hasn't yet reached the exact aspect angle
    applying_aspects = []
    
    for planet in planets:
        if planet["name"] == "Moon":
            continue
        
        planet_degree = planet.get("absolute_degree", 0)
        
        # Calculate angular difference
        diff = (planet_degree - moon_degree) % 360
        if diff > 180:
            diff = 360 - diff
        
        # Check if Moon is approaching any major aspect
        for aspect_angle, orb in MAJOR_ASPECTS.items():
            distance_to_aspect = abs(diff - aspect_angle)
            
            # Moon applies if it's within orb and moving toward the aspect
            # Since Moon is always faster, we check if the aspect is "ahead" of the Moon
            if distance_to_aspect <= orb:
                # This is a current aspect, check if it's applying or separating
                # For simplicity, if Moon degree within sign is < 28, likely has applying aspects
                if moon_sign_degree < 28:
                    applying_aspects.append({
                        "planet": planet["name"],
                        "aspect": _aspect_name(aspect_angle),
                        "orb": round(distance_to_aspect, 2),
                    })
    
    # Moon is void if no applying aspects AND Moon is in late degrees of sign
    is_void = len(applying_aspects) == 0 and moon_sign_degree >= 28
    
    # Estimate void duration (rough: Moon moves ~12-15 degrees per day)
    degrees_left = 30 - moon_sign_degree
    hours_until_sign_change = (degrees_left / 0.5)  # Moon moves ~0.5 degree per hour
    
    next_sign_index = (ZODIAC_ORDER.index(moon_sign) + 1) % 12
    next_sign = ZODIAC_ORDER[next_sign_index]
    
    if is_void:
        advice_key = "voc_advice_void"
        advice_trans = get_translation(lang, advice_key)
        if advice_trans:
            advice = advice_trans[0].format(sign=moon_sign)
        else:
            advice = (
                f"Moon is void-of-course in late {moon_sign}. "
                f"Avoid starting new projects, signing contracts, or making major decisions. "
                f"Good for: routine tasks, rest, meditation, finishing existing work."
            )
    else:
        advice_key = "voc_advice_active"
        advice_trans = get_translation(lang, advice_key)
        if advice_trans:
            advice = advice_trans[0].format(sign=moon_sign)
        else:
            advice = f"Moon is active in {moon_sign} with applying aspects."
    
    return {
        "is_void": is_void,
        "current_sign": moon_sign,
        "moon_degree": round(moon_sign_degree, 2),
        "applying_aspects": applying_aspects[:3],  # Top 3 applying aspects
        "next_sign": next_sign,
        "hours_until_sign_change": round(hours_until_sign_change, 1) if is_void else None,
        "advice": advice,
    }


def _aspect_name(angle: int) -> str:
    """Convert aspect angle to name."""
    names = {
        0: "conjunction",
        60: "sextile",
        90: "square",
        120: "trine",
        180: "opposition",
    }
    return names.get(angle, "aspect")
