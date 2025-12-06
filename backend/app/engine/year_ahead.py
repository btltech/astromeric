"""
year_ahead.py
-------------
Year-Ahead Forecast: Monthly breakdowns with Solar Return, eclipses, 
major transits, and personalized themes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

# Zodiac signs in order
ZODIAC_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Months data
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# 2025-2026 Eclipse data (pre-computed)
ECLIPSES_2025_2026 = [
    # 2025 Eclipses
    {"date": "2025-03-14", "type": "Total Lunar Eclipse", "sign": "Virgo", "degree": 23.9},
    {"date": "2025-03-29", "type": "Partial Solar Eclipse", "sign": "Aries", "degree": 8.8},
    {"date": "2025-09-07", "type": "Total Lunar Eclipse", "sign": "Pisces", "degree": 15.2},
    {"date": "2025-09-21", "type": "Partial Solar Eclipse", "sign": "Virgo", "degree": 28.8},
    # 2026 Eclipses
    {"date": "2026-02-17", "type": "Annular Solar Eclipse", "sign": "Aquarius", "degree": 28.1},
    {"date": "2026-03-03", "type": "Total Lunar Eclipse", "sign": "Virgo", "degree": 12.4},
    {"date": "2026-08-12", "type": "Partial Solar Eclipse", "sign": "Leo", "degree": 19.2},
    {"date": "2026-08-28", "type": "Partial Lunar Eclipse", "sign": "Pisces", "degree": 5.1},
]

# Slow planet ingress data 2025-2026
MAJOR_INGRESSES = [
    {"date": "2025-03-30", "planet": "Neptune", "sign": "Aries", "impact": "Collective spiritual awakening"},
    {"date": "2025-05-25", "planet": "Saturn", "sign": "Aries", "impact": "New structures and responsibilities begin"},
    {"date": "2025-06-09", "planet": "Uranus", "sign": "Gemini", "impact": "Revolution in communication and ideas"},
    {"date": "2025-07-07", "planet": "Jupiter", "sign": "Cancer", "impact": "Expansion in home and family matters"},
    {"date": "2026-02-14", "planet": "Saturn", "sign": "Aries", "impact": "Saturn settles into Aries themes"},
]

# Monthly themes based on Sun's sign
MONTHLY_THEMES = {
    1: {"season": "Capricorn→Aquarius", "focus": "Restructuring and innovation", "element": "Earth/Air"},
    2: {"season": "Aquarius→Pisces", "focus": "Community and spiritual growth", "element": "Air/Water"},
    3: {"season": "Pisces→Aries", "focus": "Endings and new beginnings", "element": "Water/Fire"},
    4: {"season": "Aries→Taurus", "focus": "Initiative and grounding", "element": "Fire/Earth"},
    5: {"season": "Taurus→Gemini", "focus": "Stability and communication", "element": "Earth/Air"},
    6: {"season": "Gemini→Cancer", "focus": "Learning and nurturing", "element": "Air/Water"},
    7: {"season": "Cancer→Leo", "focus": "Home and self-expression", "element": "Water/Fire"},
    8: {"season": "Leo→Virgo", "focus": "Creativity and analysis", "element": "Fire/Earth"},
    9: {"season": "Virgo→Libra", "focus": "Organization and balance", "element": "Earth/Air"},
    10: {"season": "Libra→Scorpio", "focus": "Relationships and transformation", "element": "Air/Water"},
    11: {"season": "Scorpio→Sagittarius", "focus": "Depth and expansion", "element": "Water/Fire"},
    12: {"season": "Sagittarius→Capricorn", "focus": "Adventure and achievement", "element": "Fire/Earth"},
}

# Numerology Universal Year themes
UNIVERSAL_YEAR_THEMES = {
    1: "New beginnings and fresh starts",
    2: "Partnership and diplomacy",
    3: "Creativity and self-expression",
    4: "Building foundations",
    5: "Change and freedom",
    6: "Responsibility and love",
    7: "Introspection and spirituality",
    8: "Power and achievement",
    9: "Completion and humanitarianism",
}


def calculate_solar_return_date(birth_date: str, year: int) -> datetime:
    """
    Calculate the approximate Solar Return date for a given year.
    Solar Return occurs when Sun returns to exact natal position.
    """
    parts = birth_date.split("-")
    birth_month, birth_day = int(parts[1]), int(parts[2])
    
    # Solar return is approximately on birthday (±1 day due to leap years)
    return datetime(year, birth_month, birth_day)


def get_personal_year_number(birth_date: str, year: int) -> int:
    """Calculate Personal Year number for numerology."""
    parts = birth_date.split("-")
    birth_month, birth_day = int(parts[1]), int(parts[2])
    
    # Personal Year = birth month + birth day + current year (reduced)
    total = birth_month + birth_day + sum(int(d) for d in str(year))
    
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(d) for d in str(total))
    
    return total


def get_universal_year_number(year: int) -> int:
    """Calculate Universal Year number."""
    total = sum(int(d) for d in str(year))
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


def get_eclipses_for_year(year: int) -> List[Dict]:
    """Get eclipses for a specific year."""
    return [e for e in ECLIPSES_2025_2026 if e["date"].startswith(str(year))]


def get_ingresses_for_year(year: int) -> List[Dict]:
    """Get major planetary ingresses for a specific year."""
    return [i for i in MAJOR_INGRESSES if i["date"].startswith(str(year))]


def calculate_eclipse_impact(eclipse: Dict, natal_chart: Dict) -> Optional[Dict]:
    """
    Calculate if an eclipse impacts the natal chart.
    Returns impact info if eclipse conjuncts a natal planet or angle.
    """
    eclipse_degree = eclipse.get("degree", 0)
    eclipse_sign = eclipse.get("sign", "")
    eclipse_sign_idx = ZODIAC_ORDER.index(eclipse_sign) if eclipse_sign in ZODIAC_ORDER else 0
    eclipse_absolute = eclipse_sign_idx * 30 + eclipse_degree
    
    impacts = []
    orb = 5  # Orb for eclipse impact
    
    # Check planets
    for planet in natal_chart.get("planets", []):
        planet_absolute = planet.get("absolute_degree", 0)
        diff = abs(eclipse_absolute - planet_absolute)
        if diff > 180:
            diff = 360 - diff
        
        if diff <= orb:
            impacts.append({
                "type": "planet",
                "name": planet["name"],
                "aspect": "conjunction" if diff < 3 else "close",
                "orb": round(diff, 1),
            })
    
    # Check Ascendant and MC if available
    for angle_key, angle_name in [("ascendant", "Ascendant"), ("mc", "Midheaven")]:
        if angle_key in natal_chart:
            angle_data = natal_chart[angle_key]
            if isinstance(angle_data, dict):
                angle_degree = angle_data.get("absolute_degree", angle_data.get("degree", 0))
            else:
                angle_degree = 0
            
            diff = abs(eclipse_absolute - angle_degree)
            if diff > 180:
                diff = 360 - diff
            
            if diff <= orb:
                impacts.append({
                    "type": "angle",
                    "name": angle_name,
                    "aspect": "conjunction" if diff < 3 else "close",
                    "orb": round(diff, 1),
                })
    
    if impacts:
        return {
            "eclipse": eclipse,
            "impacts": impacts,
            "significance": _get_eclipse_significance(eclipse, impacts),
        }
    
    return None


def _get_eclipse_significance(eclipse: Dict, impacts: List[Dict]) -> str:
    """Generate significance description for eclipse impact."""
    eclipse_type = eclipse.get("type", "Eclipse")
    impacted = [i["name"] for i in impacts]
    
    if "Sun" in impacted:
        return f"{eclipse_type} highlights your core identity and life direction"
    if "Moon" in impacted:
        return f"{eclipse_type} stirs emotional changes and home life"
    if "Ascendant" in impacted:
        return f"{eclipse_type} marks a significant personal transformation"
    if "Midheaven" in impacted:
        return f"{eclipse_type} triggers career and public life shifts"
    if "Mercury" in impacted:
        return f"{eclipse_type} activates communication and thinking patterns"
    if "Venus" in impacted:
        return f"{eclipse_type} brings relationship and value shifts"
    if "Mars" in impacted:
        return f"{eclipse_type} energizes action and assertion"
    if "Jupiter" in impacted:
        return f"{eclipse_type} expands opportunities and beliefs"
    if "Saturn" in impacted:
        return f"{eclipse_type} restructures responsibilities and boundaries"
    
    return f"{eclipse_type} has a subtle influence on your chart"


def build_monthly_forecast(
    month: int,
    year: int,
    natal_chart: Dict,
    personal_year: int,
) -> Dict:
    """Build forecast for a specific month."""
    month_theme = MONTHLY_THEMES.get(month, {})
    
    # Get eclipses this month
    month_str = f"{year}-{month:02d}"
    month_eclipses = [e for e in ECLIPSES_2025_2026 if e["date"].startswith(month_str)]
    
    # Get ingresses this month
    month_ingresses = [i for i in MAJOR_INGRESSES if i["date"].startswith(month_str)]
    
    # Calculate personal month number
    personal_month = (personal_year + month) % 9 or 9
    
    # Generate month highlights
    highlights = []
    
    if month_eclipses:
        for ecl in month_eclipses:
            highlights.append(f"{ecl['type']} in {ecl['sign']} on {ecl['date']}")
    
    if month_ingresses:
        for ing in month_ingresses:
            highlights.append(f"{ing['planet']} enters {ing['sign']} on {ing['date']}")
    
    # Add numerology insight
    highlights.append(f"Personal Month {personal_month}: {_get_personal_month_focus(personal_month)}")
    
    return {
        "month": month,
        "month_name": MONTH_NAMES[month - 1],
        "year": year,
        "season": month_theme.get("season", ""),
        "focus": month_theme.get("focus", ""),
        "element": month_theme.get("element", ""),
        "personal_month": personal_month,
        "eclipses": month_eclipses,
        "ingresses": month_ingresses,
        "highlights": highlights,
    }


def _get_personal_month_focus(num: int) -> str:
    """Get focus description for personal month number."""
    focuses = {
        1: "Initiative and new starts",
        2: "Patience and cooperation",
        3: "Expression and socializing",
        4: "Hard work and organization",
        5: "Change and flexibility",
        6: "Family and responsibility",
        7: "Reflection and analysis",
        8: "Business and finances",
        9: "Completion and letting go",
    }
    return focuses.get(num, "General flow")


def build_year_ahead_forecast(
    profile: Dict,
    natal_chart: Dict,
    year: Optional[int] = None,
) -> Dict:
    """
    Build comprehensive year-ahead forecast.
    
    Returns:
        - Solar Return date and themes
        - Personal Year number and meaning
        - Universal Year context
        - 12 monthly forecasts
        - Eclipse impacts (personalized)
        - Major ingresses
        - Key themes and advice
    """
    if year is None:
        year = datetime.now().year
    
    birth_date = profile.get("date_of_birth", "2000-01-01")
    
    # Calculate key numbers
    personal_year = get_personal_year_number(birth_date, year)
    universal_year = get_universal_year_number(year)
    solar_return_date = calculate_solar_return_date(birth_date, year)
    
    # Get eclipses and calculate personal impacts
    year_eclipses = get_eclipses_for_year(year)
    eclipse_impacts = []
    for eclipse in year_eclipses:
        impact = calculate_eclipse_impact(eclipse, natal_chart)
        if impact:
            eclipse_impacts.append(impact)
    
    # Get ingresses
    year_ingresses = get_ingresses_for_year(year)
    
    # Build monthly forecasts
    monthly_forecasts = []
    for month in range(1, 13):
        monthly = build_monthly_forecast(month, year, natal_chart, personal_year)
        monthly_forecasts.append(monthly)
    
    # Generate key themes
    key_themes = _generate_key_themes(
        personal_year, 
        universal_year, 
        eclipse_impacts, 
        year_ingresses,
        natal_chart,
    )
    
    # Generate advice
    advice = _generate_year_advice(personal_year, eclipse_impacts)
    
    return {
        "year": year,
        "personal_year": {
            "number": personal_year,
            "theme": _get_personal_year_theme(personal_year),
            "description": _get_personal_year_description(personal_year),
        },
        "universal_year": {
            "number": universal_year,
            "theme": UNIVERSAL_YEAR_THEMES.get(universal_year, "Transition"),
        },
        "solar_return": {
            "date": solar_return_date.strftime("%Y-%m-%d"),
            "description": f"Your personal new year begins around {solar_return_date.strftime('%B %d')}",
        },
        "eclipses": {
            "all": year_eclipses,
            "personal_impacts": eclipse_impacts,
        },
        "ingresses": year_ingresses,
        "monthly_forecasts": monthly_forecasts,
        "key_themes": key_themes,
        "advice": advice,
    }


def _get_personal_year_theme(num: int) -> str:
    """Get theme for personal year."""
    themes = {
        1: "New Beginnings",
        2: "Partnership",
        3: "Creativity",
        4: "Foundation",
        5: "Change",
        6: "Responsibility",
        7: "Reflection",
        8: "Achievement",
        9: "Completion",
        11: "Spiritual Awakening",
        22: "Master Building",
        33: "Master Teaching",
    }
    return themes.get(num, "Transition")


def _get_personal_year_description(num: int) -> str:
    """Get detailed description for personal year."""
    descriptions = {
        1: "This is your year of new beginnings. Plant seeds for the future, take initiative, and don't be afraid to lead. Independence is key.",
        2: "Focus on relationships, patience, and diplomacy. Partnerships flourish when you give them attention. Avoid rushing.",
        3: "Express yourself creatively this year. Socialize, communicate, and let your talents shine. Joy and optimism are your allies.",
        4: "Time to build solid foundations. Work hard, organize, and create structure. Practical matters take priority.",
        5: "Embrace change and adventure. Freedom calls, and unexpected opportunities arise. Stay flexible and open.",
        6: "Family and responsibilities take center stage. Nurture loved ones, beautify your surroundings, and serve others.",
        7: "A year for inner work, study, and spiritual development. Take time for solitude and reflection. Trust your intuition.",
        8: "Achievement and material success are possible. Focus on career, finances, and personal power. Think big.",
        9: "Complete cycles and release the old. Forgiveness, humanitarianism, and endings make way for new beginnings next year.",
        11: "Heightened intuition and spiritual insights. You may inspire others. Stay grounded while reaching for higher truths.",
        22: "Master builder energy. Turn big dreams into reality through practical action. The world is your canvas.",
        33: "Master teacher vibration. Compassion and healing are your gifts to share. Balance giving with self-care.",
    }
    return descriptions.get(num, "A year of personal evolution and growth.")


def _generate_key_themes(
    personal_year: int,
    universal_year: int,
    eclipse_impacts: List[Dict],
    ingresses: List[Dict],
    natal_chart: Dict,
) -> List[str]:
    """Generate key themes for the year."""
    themes = []
    
    # Personal year theme
    themes.append(f"Personal Year {personal_year}: {_get_personal_year_theme(personal_year)}")
    
    # Eclipse themes
    if eclipse_impacts:
        themes.append(f"{len(eclipse_impacts)} eclipses activate your chart - significant shifts ahead")
    
    # Major ingress themes
    for ing in ingresses:
        themes.append(f"{ing['planet']} in {ing['sign']}: {ing['impact']}")
    
    # Universal year context
    themes.append(f"Universal Year {universal_year}: Collective focus on {UNIVERSAL_YEAR_THEMES.get(universal_year, 'evolution')}")
    
    return themes[:6]  # Limit to 6 themes


def _generate_year_advice(personal_year: int, eclipse_impacts: List[Dict]) -> List[str]:
    """Generate advice for the year."""
    advice = []
    
    # Personal year advice
    py_advice = {
        1: "Take bold action on new ideas",
        2: "Practice patience in partnerships",
        3: "Share your creativity with the world",
        4: "Focus on building lasting structures",
        5: "Stay adaptable to changing circumstances",
        6: "Prioritize home and family harmony",
        7: "Dedicate time to inner exploration",
        8: "Pursue ambitious financial goals",
        9: "Complete unfinished business gracefully",
    }
    advice.append(py_advice.get(personal_year, "Trust your personal journey"))
    
    # Eclipse-based advice
    if eclipse_impacts:
        advice.append("Pay attention to eclipse windows - they bring pivotal moments")
    
    # General wisdom
    advice.append("Track Moon phases for optimal timing")
    advice.append("Review during retrograde periods, launch during direct motion")
    
    return advice
