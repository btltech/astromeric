"""
Relationship Timeline Engine

Provides timeline analysis for relationships including:
- Key dates and periods (Venus/Mars transits, eclipses)
- Best and challenging periods
- Relationship phases and milestones
- Synastry transit forecasting
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


# Venus and Mars sign changes for 2024-2025 (approximate dates)
# These are major relationship transits
VENUS_INGRESSES_2024_2025 = [
    {"date": "2024-01-23", "sign": "Capricorn", "end": "2024-02-16"},
    {"date": "2024-02-16", "sign": "Aquarius", "end": "2024-03-11"},
    {"date": "2024-03-11", "sign": "Pisces", "end": "2024-04-05"},
    {"date": "2024-04-05", "sign": "Aries", "end": "2024-04-29"},
    {"date": "2024-04-29", "sign": "Taurus", "end": "2024-05-23"},
    {"date": "2024-05-23", "sign": "Gemini", "end": "2024-06-17"},
    {"date": "2024-06-17", "sign": "Cancer", "end": "2024-07-11"},
    {"date": "2024-07-11", "sign": "Leo", "end": "2024-08-05"},
    {"date": "2024-08-05", "sign": "Virgo", "end": "2024-08-29"},
    {"date": "2024-08-29", "sign": "Libra", "end": "2024-09-22"},
    {"date": "2024-09-22", "sign": "Scorpio", "end": "2024-10-17"},
    {"date": "2024-10-17", "sign": "Sagittarius", "end": "2024-11-11"},
    {"date": "2024-11-11", "sign": "Capricorn", "end": "2024-12-07"},
    {"date": "2024-12-07", "sign": "Aquarius", "end": "2025-01-03"},
    {"date": "2025-01-03", "sign": "Pisces", "end": "2025-02-04"},
    {"date": "2025-02-04", "sign": "Aries", "end": "2025-03-27"},
    {"date": "2025-03-27", "sign": "Pisces", "end": "2025-04-30"},  # Retrograde
    {"date": "2025-04-30", "sign": "Aries", "end": "2025-06-06"},
    {"date": "2025-06-06", "sign": "Taurus", "end": "2025-07-05"},
    {"date": "2025-07-05", "sign": "Gemini", "end": "2025-07-30"},
    {"date": "2025-07-30", "sign": "Cancer", "end": "2025-08-24"},
    {"date": "2025-08-24", "sign": "Leo", "end": "2025-09-17"},
    {"date": "2025-09-17", "sign": "Virgo", "end": "2025-10-11"},
    {"date": "2025-10-11", "sign": "Libra", "end": "2025-11-05"},
    {"date": "2025-11-05", "sign": "Scorpio", "end": "2025-11-30"},
    {"date": "2025-11-30", "sign": "Sagittarius", "end": "2025-12-24"},
    {"date": "2025-12-24", "sign": "Capricorn", "end": "2026-01-18"},
]

MARS_INGRESSES_2024_2025 = [
    {"date": "2024-01-04", "sign": "Capricorn", "end": "2024-02-13"},
    {"date": "2024-02-13", "sign": "Aquarius", "end": "2024-03-22"},
    {"date": "2024-03-22", "sign": "Pisces", "end": "2024-04-30"},
    {"date": "2024-04-30", "sign": "Aries", "end": "2024-06-09"},
    {"date": "2024-06-09", "sign": "Taurus", "end": "2024-07-20"},
    {"date": "2024-07-20", "sign": "Gemini", "end": "2024-09-04"},
    {"date": "2024-09-04", "sign": "Cancer", "end": "2024-11-03"},
    {"date": "2024-11-03", "sign": "Leo", "end": "2025-01-06"},
    {"date": "2025-01-06", "sign": "Cancer", "end": "2025-04-18"},  # Retrograde
    {"date": "2025-04-18", "sign": "Leo", "end": "2025-06-17"},
    {"date": "2025-06-17", "sign": "Virgo", "end": "2025-08-06"},
    {"date": "2025-08-06", "sign": "Libra", "end": "2025-09-22"},
    {"date": "2025-09-22", "sign": "Scorpio", "end": "2025-11-04"},
    {"date": "2025-11-04", "sign": "Sagittarius", "end": "2025-12-15"},
    {"date": "2025-12-15", "sign": "Capricorn", "end": "2026-01-24"},
]

# Venus retrograde periods (challenging for new relationships)
VENUS_RETROGRADES = [
    {"start": "2025-03-01", "end": "2025-04-12", "sign": "Aries/Pisces"},
]

# Relationship-focused eclipses
RELATIONSHIP_ECLIPSES = [
    {"date": "2024-03-25", "type": "Lunar", "sign": "Libra", "impact": "Partnership revelations"},
    {"date": "2024-10-02", "type": "Solar", "sign": "Libra", "impact": "New relationship beginnings"},
    {"date": "2025-03-14", "type": "Lunar", "sign": "Virgo", "impact": "Service in relationships"},
    {"date": "2025-03-29", "type": "Solar", "sign": "Aries", "impact": "Individual identity in partnership"},
    {"date": "2025-09-07", "type": "Lunar", "sign": "Pisces", "impact": "Spiritual connection"},
    {"date": "2025-09-21", "type": "Solar", "sign": "Virgo", "impact": "Practical relationship matters"},
]

# Sign compatibility for relationship guidance
SIGN_RELATIONSHIP_THEMES = {
    "Aries": {
        "love_style": "Passionate and direct",
        "needs": "Independence and adventure",
        "growth_area": "Patience and compromise",
        "best_dates": "Mars transit through fire signs"
    },
    "Taurus": {
        "love_style": "Sensual and devoted",
        "needs": "Security and consistency",
        "growth_area": "Flexibility and change",
        "best_dates": "Venus transit through earth signs"
    },
    "Gemini": {
        "love_style": "Communicative and playful",
        "needs": "Mental stimulation and variety",
        "growth_area": "Emotional depth",
        "best_dates": "Venus transit through air signs"
    },
    "Cancer": {
        "love_style": "Nurturing and protective",
        "needs": "Emotional security and home",
        "growth_area": "Independence",
        "best_dates": "Moon in water signs"
    },
    "Leo": {
        "love_style": "Generous and dramatic",
        "needs": "Appreciation and loyalty",
        "growth_area": "Sharing spotlight",
        "best_dates": "Venus transit through Leo"
    },
    "Virgo": {
        "love_style": "Devoted and practical",
        "needs": "Order and appreciation",
        "growth_area": "Accepting imperfection",
        "best_dates": "Venus transit through earth signs"
    },
    "Libra": {
        "love_style": "Romantic and harmonious",
        "needs": "Partnership and beauty",
        "growth_area": "Decisiveness",
        "best_dates": "Venus transit through Libra"
    },
    "Scorpio": {
        "love_style": "Intense and transformative",
        "needs": "Depth and loyalty",
        "growth_area": "Trust and vulnerability",
        "best_dates": "Mars transit through water signs"
    },
    "Sagittarius": {
        "love_style": "Adventurous and optimistic",
        "needs": "Freedom and exploration",
        "growth_area": "Commitment",
        "best_dates": "Venus transit through fire signs"
    },
    "Capricorn": {
        "love_style": "Committed and ambitious",
        "needs": "Respect and achievement",
        "growth_area": "Emotional expression",
        "best_dates": "Venus transit through earth signs"
    },
    "Aquarius": {
        "love_style": "Unconventional and intellectual",
        "needs": "Independence and friendship",
        "growth_area": "Emotional intimacy",
        "best_dates": "Venus transit through air signs"
    },
    "Pisces": {
        "love_style": "Romantic and compassionate",
        "needs": "Spiritual connection and romance",
        "growth_area": "Boundaries",
        "best_dates": "Venus transit through water signs"
    },
}

# Relationship phase themes by house
RELATIONSHIP_HOUSE_PHASES = {
    5: {"theme": "Romance & Dating", "description": "Creative self-expression, fun, flirtation"},
    7: {"theme": "Committed Partnership", "description": "Marriage, long-term commitment, balance"},
    8: {"theme": "Deep Intimacy", "description": "Transformation, shared resources, emotional depth"},
    4: {"theme": "Building Home", "description": "Family, domestic life, emotional foundation"},
    11: {"theme": "Friendship & Community", "description": "Shared ideals, social connections"},
}


def get_venus_transit(date: datetime) -> Optional[Dict[str, Any]]:
    """
    Get the current Venus transit for a date.
    
    Args:
        date: Date to check
        
    Returns:
        Dict with Venus sign and dates, or None if not found
    """
    date_str = date.strftime("%Y-%m-%d")
    
    for ingress in VENUS_INGRESSES_2024_2025:
        if ingress["date"] <= date_str <= ingress["end"]:
            return {
                "sign": ingress["sign"],
                "start": ingress["date"],
                "end": ingress["end"],
                "planet": "Venus",
                "emoji": "💕"
            }
    return None


def get_mars_transit(date: datetime) -> Optional[Dict[str, Any]]:
    """
    Get the current Mars transit for a date.
    
    Args:
        date: Date to check
        
    Returns:
        Dict with Mars sign and dates, or None if not found
    """
    date_str = date.strftime("%Y-%m-%d")
    
    for ingress in MARS_INGRESSES_2024_2025:
        if ingress["date"] <= date_str <= ingress["end"]:
            return {
                "sign": ingress["sign"],
                "start": ingress["date"],
                "end": ingress["end"],
                "planet": "Mars",
                "emoji": "🔥"
            }
    return None


def is_venus_retrograde(date: datetime) -> Dict[str, Any]:
    """
    Check if Venus is retrograde on a date.
    
    Args:
        date: Date to check
        
    Returns:
        Dict with retrograde status and details
    """
    date_str = date.strftime("%Y-%m-%d")
    
    for retrograde in VENUS_RETROGRADES:
        if retrograde["start"] <= date_str <= retrograde["end"]:
            start_dt = datetime.strptime(retrograde["start"], "%Y-%m-%d")
            end_dt = datetime.strptime(retrograde["end"], "%Y-%m-%d")
            days_remaining = (end_dt - date).days
            
            return {
                "is_retrograde": True,
                "sign": retrograde["sign"],
                "start": retrograde["start"],
                "end": retrograde["end"],
                "days_remaining": max(0, days_remaining),
                "warning": "Venus retrograde is not ideal for starting new relationships or making major romantic decisions. Focus on reflection and reconnecting.",
                "emoji": "💔↩️"
            }
    
    return {
        "is_retrograde": False,
        "message": "Venus is direct - favorable for love and relationships",
        "emoji": "💕✨"
    }


def get_upcoming_relationship_dates(
    start_date: datetime,
    days_ahead: int = 90,
    sun_sign: str = None
) -> List[Dict[str, Any]]:
    """
    Get upcoming important dates for relationships.
    
    Args:
        start_date: Starting date
        days_ahead: How many days ahead to look
        sun_sign: Optional natal sun sign for personalized events
        
    Returns:
        List of relationship events sorted by date
    """
    events = []
    end_date = start_date + timedelta(days=days_ahead)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Add Venus ingresses
    for ingress in VENUS_INGRESSES_2024_2025:
        if start_str <= ingress["date"] <= end_str:
            is_personal = sun_sign and ingress["sign"] == sun_sign
            events.append({
                "date": ingress["date"],
                "type": "venus_ingress",
                "title": f"Venus enters {ingress['sign']}",
                "emoji": "💕",
                "impact": "love_focus",
                "is_personal": is_personal,
                "description": f"Love and attraction take on {ingress['sign']} qualities. "
                             f"{'This is your sign - expect increased charm and romantic opportunities!' if is_personal else 'Good for relationships.'}",
                "rating": 5 if is_personal else 4
            })
    
    # Add Mars ingresses
    for ingress in MARS_INGRESSES_2024_2025:
        if start_str <= ingress["date"] <= end_str:
            events.append({
                "date": ingress["date"],
                "type": "mars_ingress",
                "title": f"Mars enters {ingress['sign']}",
                "emoji": "🔥",
                "impact": "passion_focus",
                "is_personal": False,
                "description": f"Passion and desire express through {ingress['sign']} energy. "
                             f"Channel energy constructively.",
                "rating": 3
            })
    
    # Add Venus retrogrades
    for retrograde in VENUS_RETROGRADES:
        if start_str <= retrograde["start"] <= end_str:
            events.append({
                "date": retrograde["start"],
                "type": "venus_retrograde_start",
                "title": "Venus Retrograde Begins",
                "emoji": "💔↩️",
                "impact": "caution",
                "is_personal": False,
                "description": "Not ideal for starting new relationships. Past lovers may reappear. Reflect on love patterns.",
                "rating": 2
            })
        if start_str <= retrograde["end"] <= end_str:
            events.append({
                "date": retrograde["end"],
                "type": "venus_retrograde_end",
                "title": "Venus Retrograde Ends",
                "emoji": "💕✨",
                "impact": "positive",
                "is_personal": False,
                "description": "Venus goes direct! Love matters clarify and relationships can move forward.",
                "rating": 5
            })
    
    # Add relationship eclipses
    for eclipse in RELATIONSHIP_ECLIPSES:
        if start_str <= eclipse["date"] <= end_str:
            events.append({
                "date": eclipse["date"],
                "type": "eclipse",
                "title": f"{eclipse['type']} Eclipse in {eclipse['sign']}",
                "emoji": "🌑" if eclipse["type"] == "Solar" else "🌕",
                "impact": "transformative",
                "is_personal": sun_sign and eclipse["sign"] == sun_sign,
                "description": eclipse["impact"] + ". Major relationship shifts possible.",
                "rating": 4
            })
    
    # Sort by date
    events.sort(key=lambda x: x["date"])
    
    return events


def analyze_relationship_timing(
    date: datetime,
    person1_sign: str,
    person2_sign: str = None
) -> Dict[str, Any]:
    """
    Analyze relationship timing for a date.
    
    Args:
        date: Date to analyze
        person1_sign: First person's sun sign
        person2_sign: Second person's sun sign (optional)
        
    Returns:
        Dict with timing analysis
    """
    venus = get_venus_transit(date)
    mars = get_mars_transit(date)
    venus_rx = is_venus_retrograde(date)
    
    # Calculate timing score
    score = 50  # Base score
    factors = []
    warnings = []
    recommendations = []
    
    # Venus retrograde is a major factor
    if venus_rx.get("is_retrograde"):
        score -= 20
        warnings.append("Venus retrograde - not ideal for new romantic beginnings")
        factors.append({"factor": "Venus Retrograde", "impact": -20, "emoji": "💔"})
    else:
        factors.append({"factor": "Venus Direct", "impact": 10, "emoji": "💕"})
        score += 10
    
    # Venus in compatible sign
    if venus:
        venus_sign = venus["sign"]
        themes = SIGN_RELATIONSHIP_THEMES.get(person1_sign, {})
        
        # Check if Venus is in person's sign
        if venus_sign == person1_sign:
            score += 15
            factors.append({"factor": f"Venus in your sign ({person1_sign})", "impact": 15, "emoji": "⭐"})
            recommendations.append(f"Venus in {person1_sign} enhances your natural charm and attractiveness!")
        
        # Check element compatibility with Venus
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]
        
        person_element = None
        venus_element = None
        
        for elem, signs in [("Fire", fire_signs), ("Earth", earth_signs), 
                            ("Air", air_signs), ("Water", water_signs)]:
            if person1_sign in signs:
                person_element = elem
            if venus_sign in signs:
                venus_element = elem
        
        if person_element and venus_element:
            compatible_elements = {
                "Fire": ["Fire", "Air"],
                "Earth": ["Earth", "Water"],
                "Air": ["Air", "Fire"],
                "Water": ["Water", "Earth"]
            }
            if venus_element in compatible_elements.get(person_element, []):
                score += 10
                factors.append({"factor": f"Venus in compatible {venus_element} element", "impact": 10, "emoji": "✨"})
    
    # Mars energy
    if mars:
        mars_sign = mars["sign"]
        if mars_sign in ["Aries", "Scorpio"]:  # Mars rules these
            score += 5
            factors.append({"factor": f"Mars strong in {mars_sign}", "impact": 5, "emoji": "🔥"})
            recommendations.append("Passion and initiative are heightened - take action!")
    
    # Calculate rating
    if score >= 80:
        rating = "Excellent"
        rating_emoji = "💖💖💖"
    elif score >= 65:
        rating = "Good"
        rating_emoji = "💕💕"
    elif score >= 50:
        rating = "Moderate"
        rating_emoji = "💗"
    elif score >= 35:
        rating = "Challenging"
        rating_emoji = "💔"
    else:
        rating = "Difficult"
        rating_emoji = "⚠️"
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "score": min(100, max(0, score)),
        "rating": rating,
        "rating_emoji": rating_emoji,
        "venus_transit": venus,
        "mars_transit": mars,
        "venus_retrograde": venus_rx,
        "factors": factors,
        "warnings": warnings,
        "recommendations": recommendations,
        "person1_sign": person1_sign,
        "person2_sign": person2_sign,
        "love_themes": SIGN_RELATIONSHIP_THEMES.get(person1_sign, {})
    }


def get_best_relationship_days(
    start_date: datetime,
    sun_sign: str,
    days_ahead: int = 30
) -> List[Dict[str, Any]]:
    """
    Find the best days for relationship activities in a period.
    
    Args:
        start_date: Starting date
        sun_sign: Person's sun sign
        days_ahead: How many days ahead to check
        
    Returns:
        List of days sorted by relationship score
    """
    days = []
    
    for i in range(days_ahead):
        check_date = start_date + timedelta(days=i)
        analysis = analyze_relationship_timing(check_date, sun_sign)
        
        days.append({
            "date": analysis["date"],
            "weekday": check_date.strftime("%A"),
            "score": analysis["score"],
            "rating": analysis["rating"],
            "rating_emoji": analysis["rating_emoji"],
            "is_today": i == 0,
            "days_away": i,
            "key_factor": analysis["factors"][0]["factor"] if analysis["factors"] else None,
            "warnings": analysis["warnings"],
        })
    
    # Sort by score descending
    days.sort(key=lambda x: x["score"], reverse=True)
    
    return days


def build_relationship_timeline(
    sun_sign: str,
    partner_sign: str = None,
    start_date: datetime = None,
    months_ahead: int = 6
) -> Dict[str, Any]:
    """
    Build a comprehensive relationship timeline.
    
    Args:
        sun_sign: Person's sun sign
        partner_sign: Partner's sun sign (optional)
        start_date: Starting date (defaults to today)
        months_ahead: How many months ahead to forecast
        
    Returns:
        Complete relationship timeline
    """
    if start_date is None:
        start_date = datetime.now()
    
    days_ahead = months_ahead * 30
    
    # Get today's analysis
    today_analysis = analyze_relationship_timing(start_date, sun_sign, partner_sign)
    
    # Get upcoming events
    events = get_upcoming_relationship_dates(start_date, days_ahead, sun_sign)
    
    # Get best days in next 30 days
    best_days = get_best_relationship_days(start_date, sun_sign, 30)[:5]
    
    # Group events by month
    events_by_month = defaultdict(list)
    for event in events:
        month_key = event["date"][:7]  # YYYY-MM
        events_by_month[month_key].append(event)
    
    # Calculate overall period score
    period_scores = [analyze_relationship_timing(start_date + timedelta(days=i), sun_sign)["score"] 
                     for i in range(0, days_ahead, 7)]
    avg_score = sum(period_scores) / len(period_scores) if period_scores else 50
    
    # Get love themes for sign
    love_themes = SIGN_RELATIONSHIP_THEMES.get(sun_sign, {})
    
    return {
        "generated_at": datetime.now().isoformat(),
        "sun_sign": sun_sign,
        "partner_sign": partner_sign,
        "period": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": (start_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d"),
            "months": months_ahead
        },
        "today": today_analysis,
        "period_score": round(avg_score, 1),
        "period_outlook": (
            "Excellent period for love!" if avg_score >= 70 else
            "Good romantic potential ahead." if avg_score >= 55 else
            "Mixed influences - choose timing carefully." if avg_score >= 40 else
            "Challenging period - focus on self-love and reflection."
        ),
        "best_upcoming_days": best_days,
        "events": events,
        "events_by_month": dict(events_by_month),
        "love_themes": love_themes,
        "total_events": len(events),
        "personal_events": len([e for e in events if e.get("is_personal")])
    }


def get_relationship_phases() -> Dict[str, Any]:
    """
    Get information about relationship phases and their astrological houses.
    
    Returns:
        Dict with relationship phase information
    """
    return {
        "phases": RELATIONSHIP_HOUSE_PHASES,
        "house_order": [5, 7, 8, 4, 11],
        "description": "Relationships typically evolve through these astrological phases, "
                      "though the journey is unique for each couple."
    }
