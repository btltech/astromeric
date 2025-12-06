"""
timing_advisor.py
-----------------
Best Day/Time Finder: Analyzes multiple factors to recommend optimal timing
for specific activities (meetings, travel, romance, signing contracts, etc.)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from .planetary_timing import (
    calculate_planetary_hours,
    get_current_planetary_hour,
    detect_retrogrades,
    calculate_void_of_course_moon,
    CHALDEAN_ORDER,
)
from .moon_phases import calculate_moon_phase, estimate_moon_sign


# Activity categories and their favorable conditions
ACTIVITY_PROFILES = {
    "business_meeting": {
        "name": "Business Meeting",
        "favorable_planets": ["Jupiter", "Sun", "Mercury"],
        "unfavorable_planets": ["Saturn", "Mars"],
        "favorable_moon_phases": ["First Quarter", "Waxing Gibbous", "Full Moon"],
        "unfavorable_moon_phases": ["Waning Crescent", "New Moon"],
        "favorable_moon_signs": ["Capricorn", "Virgo", "Libra", "Leo"],
        "avoid_retrograde": ["Mercury"],
        "avoid_voc_moon": True,
        "best_personal_days": [1, 4, 8],
        "avoid_personal_days": [7, 9],
        "weight_factors": {"planet": 0.3, "moon_phase": 0.2, "moon_sign": 0.2, "retrograde": 0.15, "voc": 0.15},
    },
    "travel": {
        "name": "Travel",
        "favorable_planets": ["Jupiter", "Mercury", "Venus"],
        "unfavorable_planets": ["Saturn"],
        "favorable_moon_phases": ["Waxing Crescent", "First Quarter", "Waxing Gibbous"],
        "unfavorable_moon_phases": ["Waning Crescent", "Last Quarter"],
        "favorable_moon_signs": ["Sagittarius", "Gemini", "Aquarius", "Aries"],
        "avoid_retrograde": ["Mercury"],
        "avoid_voc_moon": True,
        "best_personal_days": [3, 5, 9],
        "avoid_personal_days": [4, 7],
        "weight_factors": {"planet": 0.25, "moon_phase": 0.2, "moon_sign": 0.2, "retrograde": 0.2, "voc": 0.15},
    },
    "romance_date": {
        "name": "Romantic Date",
        "favorable_planets": ["Venus", "Moon", "Jupiter"],
        "unfavorable_planets": ["Saturn", "Mars"],
        "favorable_moon_phases": ["Waxing Crescent", "Waxing Gibbous", "Full Moon"],
        "unfavorable_moon_phases": ["Waning Crescent", "Last Quarter"],
        "favorable_moon_signs": ["Taurus", "Libra", "Cancer", "Pisces", "Leo"],
        "avoid_retrograde": ["Venus"],
        "avoid_voc_moon": True,
        "best_personal_days": [2, 3, 6],
        "avoid_personal_days": [4, 8],
        "weight_factors": {"planet": 0.2, "moon_phase": 0.3, "moon_sign": 0.25, "retrograde": 0.15, "voc": 0.1},
    },
    "signing_contracts": {
        "name": "Signing Contracts",
        "favorable_planets": ["Jupiter", "Sun", "Mercury"],
        "unfavorable_planets": ["Neptune", "Mars"],
        "favorable_moon_phases": ["First Quarter", "Full Moon", "Waxing Gibbous"],
        "unfavorable_moon_phases": ["New Moon", "Waning Crescent"],
        "favorable_moon_signs": ["Capricorn", "Virgo", "Taurus", "Libra"],
        "avoid_retrograde": ["Mercury"],
        "avoid_voc_moon": True,
        "best_personal_days": [1, 4, 8],
        "avoid_personal_days": [5, 9],
        "weight_factors": {"planet": 0.25, "moon_phase": 0.2, "moon_sign": 0.15, "retrograde": 0.25, "voc": 0.15},
    },
    "job_interview": {
        "name": "Job Interview",
        "favorable_planets": ["Jupiter", "Sun", "Mercury"],
        "unfavorable_planets": ["Saturn", "Neptune"],
        "favorable_moon_phases": ["First Quarter", "Waxing Gibbous", "Full Moon"],
        "unfavorable_moon_phases": ["Waning Crescent", "New Moon"],
        "favorable_moon_signs": ["Leo", "Capricorn", "Virgo", "Libra"],
        "avoid_retrograde": ["Mercury"],
        "avoid_voc_moon": True,
        "best_personal_days": [1, 3, 8],
        "avoid_personal_days": [7, 9],
        "weight_factors": {"planet": 0.3, "moon_phase": 0.2, "moon_sign": 0.2, "retrograde": 0.15, "voc": 0.15},
    },
    "creative_work": {
        "name": "Creative Work",
        "favorable_planets": ["Venus", "Moon", "Neptune"],
        "unfavorable_planets": ["Saturn"],
        "favorable_moon_phases": ["Waxing Crescent", "First Quarter", "Full Moon"],
        "unfavorable_moon_phases": ["Last Quarter"],
        "favorable_moon_signs": ["Pisces", "Leo", "Cancer", "Libra", "Aquarius"],
        "avoid_retrograde": [],  # Retrogrades can actually help creativity
        "avoid_voc_moon": False,  # VOC Moon can be good for creative flow
        "best_personal_days": [3, 5, 9],
        "avoid_personal_days": [4, 8],
        "weight_factors": {"planet": 0.25, "moon_phase": 0.3, "moon_sign": 0.3, "retrograde": 0.05, "voc": 0.1},
    },
    "starting_project": {
        "name": "Starting New Project",
        "favorable_planets": ["Sun", "Jupiter", "Mars"],
        "unfavorable_planets": ["Saturn"],
        "favorable_moon_phases": ["New Moon", "Waxing Crescent", "First Quarter"],
        "unfavorable_moon_phases": ["Waning Gibbous", "Last Quarter", "Waning Crescent"],
        "favorable_moon_signs": ["Aries", "Leo", "Sagittarius", "Capricorn"],
        "avoid_retrograde": ["Mercury", "Mars"],
        "avoid_voc_moon": True,
        "best_personal_days": [1, 3, 5],
        "avoid_personal_days": [7, 9],
        "weight_factors": {"planet": 0.2, "moon_phase": 0.35, "moon_sign": 0.2, "retrograde": 0.15, "voc": 0.1},
    },
    "medical_procedure": {
        "name": "Medical Procedure",
        "favorable_planets": ["Jupiter", "Sun"],
        "unfavorable_planets": ["Mars", "Saturn"],
        "favorable_moon_phases": ["Waning Gibbous", "Last Quarter", "Waning Crescent"],  # Waning for healing
        "unfavorable_moon_phases": ["Full Moon"],  # Avoid surgery on Full Moon
        "favorable_moon_signs": ["Virgo", "Capricorn", "Aquarius"],
        "avoid_retrograde": ["Mercury"],
        "avoid_voc_moon": True,
        "best_personal_days": [4, 6, 7],
        "avoid_personal_days": [5],
        "weight_factors": {"planet": 0.2, "moon_phase": 0.35, "moon_sign": 0.2, "retrograde": 0.1, "voc": 0.15},
    },
    "financial_decision": {
        "name": "Financial Decision",
        "favorable_planets": ["Jupiter", "Venus", "Saturn"],
        "unfavorable_planets": ["Neptune", "Mars"],
        "favorable_moon_phases": ["First Quarter", "Waxing Gibbous", "Full Moon"],
        "unfavorable_moon_phases": ["Waning Crescent"],
        "favorable_moon_signs": ["Taurus", "Capricorn", "Virgo", "Scorpio"],
        "avoid_retrograde": ["Mercury", "Venus"],
        "avoid_voc_moon": True,
        "best_personal_days": [4, 8],
        "avoid_personal_days": [5, 9],
        "weight_factors": {"planet": 0.25, "moon_phase": 0.2, "moon_sign": 0.2, "retrograde": 0.2, "voc": 0.15},
    },
    "meditation_spiritual": {
        "name": "Meditation & Spiritual Practice",
        "favorable_planets": ["Moon", "Neptune", "Jupiter"],
        "unfavorable_planets": ["Mars"],
        "favorable_moon_phases": ["Full Moon", "New Moon", "Waning Crescent"],
        "unfavorable_moon_phases": [],
        "favorable_moon_signs": ["Pisces", "Cancer", "Scorpio", "Aquarius"],
        "avoid_retrograde": [],
        "avoid_voc_moon": False,  # VOC Moon is excellent for meditation
        "best_personal_days": [7, 9, 11],
        "avoid_personal_days": [],
        "weight_factors": {"planet": 0.2, "moon_phase": 0.4, "moon_sign": 0.3, "retrograde": 0.0, "voc": 0.1},
    },
}


def calculate_timing_score(
    activity: str,
    date: datetime,
    transit_chart: Dict,
    latitude: float,
    longitude: float,
    timezone: str = "UTC",
    personal_day: Optional[int] = None,
) -> Dict:
    """
    Calculate a timing score (0-100) for a specific activity on a given date.
    
    Returns:
        - score: Overall score (0-100)
        - breakdown: Individual factor scores
        - warnings: List of timing concerns
        - recommendations: Suggested adjustments
    """
    profile = ACTIVITY_PROFILES.get(activity, ACTIVITY_PROFILES["business_meeting"])
    weights = profile["weight_factors"]
    
    scores = {}
    warnings = []
    recommendations = []
    
    # 1. Planetary Hour Score
    hours = calculate_planetary_hours(date, latitude, longitude, timezone)
    favorable_hours = [h for h in hours if h["planet"] in profile["favorable_planets"]]
    unfavorable_hours = [h for h in hours if h["planet"] in profile["unfavorable_planets"]]
    
    # Find best hours
    best_hours = []
    for h in favorable_hours:
        if h["is_day"]:  # Prioritize day hours
            best_hours.append(h)
    
    if favorable_hours:
        planet_score = 100 if best_hours else 70
    else:
        planet_score = 50
    
    # Current hour check
    current_hour = get_current_planetary_hour(date, latitude, longitude, timezone)
    if current_hour["planet"] in profile["favorable_planets"]:
        planet_score += 10
        recommendations.append(f"Current {current_hour['planet']} hour is favorable")
    elif current_hour["planet"] in profile["unfavorable_planets"]:
        planet_score -= 20
        warnings.append(f"Current {current_hour['planet']} hour is challenging for this activity")
    
    planet_score = max(0, min(100, planet_score))
    scores["planetary_hour"] = planet_score
    
    # 2. Moon Phase Score
    phase = calculate_moon_phase(date)
    phase_name = phase["phase_name"]
    
    if phase_name in profile["favorable_moon_phases"]:
        moon_phase_score = 90
        recommendations.append(f"{phase_name} supports this activity")
    elif phase_name in profile["unfavorable_moon_phases"]:
        moon_phase_score = 30
        warnings.append(f"{phase_name} is not ideal for this activity")
    else:
        moon_phase_score = 60
    
    scores["moon_phase"] = moon_phase_score
    
    # 3. Moon Sign Score
    moon_sign = estimate_moon_sign(date)
    
    if moon_sign in profile["favorable_moon_signs"]:
        moon_sign_score = 90
        recommendations.append(f"Moon in {moon_sign} enhances success")
    elif moon_sign in ["Scorpio", "Capricorn"] and activity not in ["romance_date", "creative_work"]:
        moon_sign_score = 50  # Neutral-challenging
    else:
        moon_sign_score = 60
    
    scores["moon_sign"] = moon_sign_score
    
    # 4. Retrograde Check
    retrogrades = detect_retrogrades(transit_chart)
    retrograde_planets = [r["planet"] for r in retrogrades]
    problematic_retrogrades = [p for p in retrograde_planets if p in profile["avoid_retrograde"]]
    
    if problematic_retrogrades:
        retrograde_score = 20
        for p in problematic_retrogrades:
            warnings.append(f"{p} retrograde: Review carefully, expect delays")
    elif retrogrades:
        retrograde_score = 70
    else:
        retrograde_score = 100
    
    scores["retrograde"] = retrograde_score
    
    # 5. Void-of-Course Moon Check
    voc = calculate_void_of_course_moon(transit_chart)
    
    if voc["is_void"] and profile["avoid_voc_moon"]:
        voc_score = 20
        warnings.append("Moon is void-of-course - avoid starting new ventures")
        if voc.get("hours_until_sign_change"):
            recommendations.append(f"Wait {voc['hours_until_sign_change']}h for Moon to enter {voc.get('next_sign', 'next sign')}")
    else:
        voc_score = 100
    
    scores["voc_moon"] = voc_score
    
    # 6. Personal Day Check (if provided)
    if personal_day:
        if personal_day in profile["best_personal_days"]:
            personal_day_score = 90
            recommendations.append(f"Personal Day {personal_day} aligns well with this activity")
        elif personal_day in profile["avoid_personal_days"]:
            personal_day_score = 40
            warnings.append(f"Personal Day {personal_day} may create resistance")
        else:
            personal_day_score = 60
        scores["personal_day"] = personal_day_score
    
    # Calculate weighted overall score
    total_weight = sum(weights.values())
    overall_score = (
        scores["planetary_hour"] * weights["planet"] +
        scores["moon_phase"] * weights["moon_phase"] +
        scores["moon_sign"] * weights["moon_sign"] +
        scores["retrograde"] * weights["retrograde"] +
        scores["voc_moon"] * weights["voc"]
    ) / total_weight
    
    # Round and clamp
    overall_score = max(0, min(100, round(overall_score)))
    
    # Generate rating
    if overall_score >= 80:
        rating = "Excellent"
        emoji = "✨"
    elif overall_score >= 65:
        rating = "Good"
        emoji = "👍"
    elif overall_score >= 50:
        rating = "Moderate"
        emoji = "⚠️"
    else:
        rating = "Challenging"
        emoji = "🚫"
    
    return {
        "activity": profile["name"],
        "date": date.strftime("%Y-%m-%d"),
        "score": overall_score,
        "rating": rating,
        "emoji": emoji,
        "breakdown": scores,
        "current_phase": phase["phase_name"],
        "moon_sign": moon_sign,
        "warnings": warnings,
        "recommendations": recommendations,
        "best_hours": [
            {"start": h["start"], "end": h["end"], "planet": h["planet"]}
            for h in best_hours[:3]  # Top 3 hours
        ],
    }


def find_best_days(
    activity: str,
    transit_chart: Dict,
    latitude: float,
    longitude: float,
    timezone: str = "UTC",
    days_ahead: int = 7,
    personal_day_cycle: Optional[int] = None,  # Personal Year number
) -> List[Dict]:
    """
    Find the best days for an activity in the next N days.
    
    Returns sorted list of days with their scores.
    """
    results = []
    now = datetime.now(ZoneInfo(timezone))
    
    for i in range(days_ahead):
        check_date = now + timedelta(days=i)
        
        # Calculate personal day if cycle provided
        personal_day = None
        if personal_day_cycle:
            # Personal Day = Personal Year + Month + Day (reduced)
            day_sum = personal_day_cycle + check_date.month + check_date.day
            while day_sum > 9 and day_sum not in [11, 22]:
                day_sum = sum(int(d) for d in str(day_sum))
            personal_day = day_sum
        
        score = calculate_timing_score(
            activity,
            check_date,
            transit_chart,
            latitude,
            longitude,
            timezone,
            personal_day,
        )
        
        score["weekday"] = check_date.strftime("%A")
        results.append(score)
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results


def get_timing_advice(
    activity: str,
    transit_chart: Dict,
    latitude: float,
    longitude: float,
    timezone: str = "UTC",
    personal_day: Optional[int] = None,
) -> Dict:
    """
    Get timing advice for an activity, including today's score and best upcoming day.
    """
    now = datetime.now(ZoneInfo(timezone))
    
    # Today's score
    today = calculate_timing_score(
        activity, now, transit_chart, latitude, longitude, timezone, personal_day
    )
    today["weekday"] = now.strftime("%A")
    
    # Find best day in next 7 days
    upcoming = find_best_days(
        activity, transit_chart, latitude, longitude, timezone, 7
    )
    
    # Best day
    best_day = upcoming[0] if upcoming else today
    
    # Is today the best?
    today_is_best = best_day["date"] == today["date"]
    
    return {
        "activity": ACTIVITY_PROFILES.get(activity, {}).get("name", activity),
        "today": today,
        "best_upcoming": best_day,
        "today_is_best": today_is_best,
        "all_days": upcoming[:5],  # Top 5 days
        "advice": _generate_timing_advice(today, best_day, today_is_best),
    }


def _generate_timing_advice(today: Dict, best: Dict, is_best: bool) -> str:
    """Generate human-readable timing advice."""
    if is_best:
        if today["score"] >= 80:
            return "Today is excellent for this activity! The cosmos align in your favor."
        elif today["score"] >= 65:
            return "Today is a good day for this. Proceed with confidence."
        else:
            return "Today is the best of the upcoming days, though timing could be better."
    else:
        if today["score"] >= 65:
            return f"Today is good ({today['score']}), but {best['weekday']} scores even higher ({best['score']})."
        elif today["score"] >= 50:
            return f"Consider waiting until {best['weekday']} for better cosmic support."
        else:
            return f"Today's timing is challenging. {best['weekday']} offers much better conditions."


def get_available_activities() -> List[Dict]:
    """Return list of available activity types for timing analysis."""
    return [
        {"id": k, "name": v["name"]}
        for k, v in ACTIVITY_PROFILES.items()
    ]
