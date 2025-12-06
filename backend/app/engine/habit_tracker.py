"""
Habit Tracker with Lunar Cycles Engine

Track habits aligned with moon phases for optimal timing and success.
Supports habit creation, logging, and lunar-aware analytics.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Literal
from collections import defaultdict


# Moon phase recommendations for habits
LUNAR_HABIT_GUIDANCE = {
    "new_moon": {
        "phase_name": "New Moon",
        "emoji": "🌑",
        "theme": "New Beginnings",
        "best_for": [
            "Starting new habits",
            "Setting intentions",
            "Planting seeds for change",
            "Rest and reflection"
        ],
        "avoid": [
            "Major launches",
            "High-intensity workouts",
            "Overcommitting"
        ],
        "energy": "Low, introspective",
        "ideal_habits": ["meditation", "journaling", "planning", "rest"],
        "power_score_modifier": 1.2  # Boost for starting habits
    },
    "waxing_crescent": {
        "phase_name": "Waxing Crescent",
        "emoji": "🌒",
        "theme": "Building Momentum",
        "best_for": [
            "Taking first steps",
            "Building routines",
            "Learning new skills",
            "Gentle exercise"
        ],
        "avoid": [
            "Giving up early",
            "Overanalyzing"
        ],
        "energy": "Increasing, hopeful",
        "ideal_habits": ["exercise", "learning", "creative", "social"],
        "power_score_modifier": 1.1
    },
    "first_quarter": {
        "phase_name": "First Quarter",
        "emoji": "🌓",
        "theme": "Taking Action",
        "best_for": [
            "Pushing through challenges",
            "Making decisions",
            "Physical activity",
            "Confronting obstacles"
        ],
        "avoid": [
            "Procrastination",
            "Being too cautious"
        ],
        "energy": "Active, dynamic",
        "ideal_habits": ["exercise", "productivity", "challenge", "habit_building"],
        "power_score_modifier": 1.15
    },
    "waxing_gibbous": {
        "phase_name": "Waxing Gibbous",
        "emoji": "🌔",
        "theme": "Refinement",
        "best_for": [
            "Fine-tuning habits",
            "Preparing for results",
            "Adjusting routines",
            "Building consistency"
        ],
        "avoid": [
            "Making major changes",
            "Starting over"
        ],
        "energy": "High, anticipatory",
        "ideal_habits": ["exercise", "learning", "creative", "meditation"],
        "power_score_modifier": 1.1
    },
    "full_moon": {
        "phase_name": "Full Moon",
        "emoji": "🌕",
        "theme": "Peak & Celebration",
        "best_for": [
            "Celebrating progress",
            "High-energy activities",
            "Social habits",
            "Completing cycles"
        ],
        "avoid": [
            "Starting brand new habits",
            "Rash decisions"
        ],
        "energy": "Peak, intense",
        "ideal_habits": ["exercise", "social", "celebration", "review"],
        "power_score_modifier": 1.0
    },
    "waning_gibbous": {
        "phase_name": "Waning Gibbous",
        "emoji": "🌖",
        "theme": "Gratitude & Sharing",
        "best_for": [
            "Teaching others",
            "Sharing knowledge",
            "Reviewing progress",
            "Giving back"
        ],
        "avoid": [
            "Overextending",
            "Ignoring rest needs"
        ],
        "energy": "Decreasing, grateful",
        "ideal_habits": ["journaling", "social", "review", "meditation"],
        "power_score_modifier": 0.95
    },
    "last_quarter": {
        "phase_name": "Last Quarter",
        "emoji": "🌗",
        "theme": "Release & Let Go",
        "best_for": [
            "Breaking bad habits",
            "Releasing what doesn't serve",
            "Reflection",
            "Gentle exercise"
        ],
        "avoid": [
            "Starting new projects",
            "Clinging to old patterns"
        ],
        "energy": "Releasing, introspective",
        "ideal_habits": ["meditation", "declutter", "rest", "reflection"],
        "power_score_modifier": 0.9
    },
    "waning_crescent": {
        "phase_name": "Waning Crescent",
        "emoji": "🌘",
        "theme": "Rest & Surrender",
        "best_for": [
            "Rest and recovery",
            "Gentle practices",
            "Preparing for new cycle",
            "Dream work"
        ],
        "avoid": [
            "Pushing too hard",
            "Major new initiatives"
        ],
        "energy": "Low, surrendering",
        "ideal_habits": ["rest", "meditation", "journaling", "sleep"],
        "power_score_modifier": 0.85
    }
}

# Habit categories with their characteristics
HABIT_CATEGORIES = {
    "exercise": {
        "name": "Exercise & Movement",
        "emoji": "🏃",
        "description": "Physical activity and fitness",
        "best_phases": ["first_quarter", "waxing_gibbous", "full_moon"],
        "avoid_phases": ["waning_crescent", "new_moon"]
    },
    "meditation": {
        "name": "Meditation & Mindfulness",
        "emoji": "🧘",
        "description": "Mental wellness and awareness",
        "best_phases": ["new_moon", "waning_gibbous", "waning_crescent"],
        "avoid_phases": []
    },
    "learning": {
        "name": "Learning & Study",
        "emoji": "📚",
        "description": "Education and skill building",
        "best_phases": ["waxing_crescent", "first_quarter", "waxing_gibbous"],
        "avoid_phases": ["waning_crescent"]
    },
    "creative": {
        "name": "Creative Expression",
        "emoji": "🎨",
        "description": "Art, writing, music, creation",
        "best_phases": ["waxing_crescent", "waxing_gibbous", "full_moon"],
        "avoid_phases": ["last_quarter"]
    },
    "social": {
        "name": "Social Connection",
        "emoji": "👥",
        "description": "Relationships and communication",
        "best_phases": ["full_moon", "waxing_gibbous", "waning_gibbous"],
        "avoid_phases": ["new_moon", "waning_crescent"]
    },
    "productivity": {
        "name": "Work & Productivity",
        "emoji": "💼",
        "description": "Tasks, goals, and accomplishments",
        "best_phases": ["first_quarter", "waxing_gibbous", "waxing_crescent"],
        "avoid_phases": ["waning_crescent"]
    },
    "health": {
        "name": "Health & Nutrition",
        "emoji": "🥗",
        "description": "Diet, supplements, self-care",
        "best_phases": ["new_moon", "waxing_crescent", "first_quarter"],
        "avoid_phases": []
    },
    "rest": {
        "name": "Rest & Recovery",
        "emoji": "😴",
        "description": "Sleep, relaxation, downtime",
        "best_phases": ["new_moon", "waning_crescent", "last_quarter"],
        "avoid_phases": ["full_moon", "first_quarter"]
    },
    "financial": {
        "name": "Financial Habits",
        "emoji": "💰",
        "description": "Saving, investing, budgeting",
        "best_phases": ["new_moon", "waxing_crescent", "first_quarter"],
        "avoid_phases": ["full_moon"]  # Avoid impulse decisions
    },
    "spiritual": {
        "name": "Spiritual Practice",
        "emoji": "✨",
        "description": "Prayer, ritual, connection",
        "best_phases": ["new_moon", "full_moon", "waning_crescent"],
        "avoid_phases": []
    }
}


def get_moon_phase_name(illumination: float, is_waxing: bool) -> str:
    """
    Get the moon phase name based on illumination and waxing/waning.
    
    Args:
        illumination: Moon illumination percentage (0-100)
        is_waxing: Whether the moon is waxing (growing)
        
    Returns:
        Phase name key for LUNAR_HABIT_GUIDANCE
    """
    if illumination < 3:
        return "new_moon"
    elif illumination < 50:
        return "waxing_crescent" if is_waxing else "waning_crescent"
    elif illumination < 55:
        return "first_quarter" if is_waxing else "last_quarter"
    elif illumination < 97:
        return "waxing_gibbous" if is_waxing else "waning_gibbous"
    else:
        return "full_moon"


def create_habit(
    name: str,
    category: str,
    frequency: Literal["daily", "weekly", "lunar_cycle"] = "daily",
    target_count: int = 1,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new habit definition.
    
    Args:
        name: Habit name
        category: Category key from HABIT_CATEGORIES
        frequency: How often (daily, weekly, or per lunar cycle)
        target_count: Target completions per period
        description: Optional description
        
    Returns:
        Habit definition dict
    """
    cat_info = HABIT_CATEGORIES.get(category, HABIT_CATEGORIES["health"])
    
    return {
        "id": None,  # To be set by database
        "name": name,
        "category": category,
        "category_name": cat_info["name"],
        "category_emoji": cat_info["emoji"],
        "frequency": frequency,
        "target_count": target_count,
        "description": description,
        "best_phases": cat_info["best_phases"],
        "avoid_phases": cat_info["avoid_phases"],
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }


def log_habit_completion(
    habit_id: int,
    completed_at: datetime = None,
    moon_phase: str = None,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Log a habit completion.
    
    Args:
        habit_id: ID of the habit
        completed_at: When completed (defaults to now)
        moon_phase: Current moon phase (optional)
        notes: Optional notes
        
    Returns:
        Completion log dict
    """
    completed = completed_at or datetime.now()
    
    return {
        "habit_id": habit_id,
        "completed_at": completed.isoformat(),
        "date": completed.strftime("%Y-%m-%d"),
        "weekday": completed.strftime("%A"),
        "moon_phase": moon_phase,
        "notes": notes
    }


def calculate_lunar_alignment_score(
    habit_category: str,
    moon_phase: str
) -> Dict[str, Any]:
    """
    Calculate how well a habit aligns with the current moon phase.
    
    Args:
        habit_category: Habit category key
        moon_phase: Current moon phase key
        
    Returns:
        Dict with alignment score and guidance
    """
    cat_info = HABIT_CATEGORIES.get(habit_category, {})
    phase_info = LUNAR_HABIT_GUIDANCE.get(moon_phase, {})
    
    # Calculate base score
    score = 50  # Neutral
    
    # Check if this phase is ideal for this habit
    best_phases = cat_info.get("best_phases", [])
    avoid_phases = cat_info.get("avoid_phases", [])
    
    if moon_phase in best_phases:
        score = 85
        alignment = "Excellent"
        message = f"The {phase_info.get('phase_name', moon_phase)} is ideal for {cat_info.get('name', habit_category)}!"
    elif moon_phase in avoid_phases:
        score = 35
        alignment = "Challenging"
        message = f"This moon phase isn't optimal for {cat_info.get('name', habit_category)}. Consider gentler practices."
    else:
        score = 60
        alignment = "Moderate"
        message = f"Neutral energy for {cat_info.get('name', habit_category)}. Trust your personal rhythm."
    
    # Apply phase modifier
    modifier = phase_info.get("power_score_modifier", 1.0)
    adjusted_score = min(100, int(score * modifier))
    
    return {
        "score": adjusted_score,
        "alignment": alignment,
        "habit_category": habit_category,
        "moon_phase": moon_phase,
        "phase_name": phase_info.get("phase_name", ""),
        "phase_emoji": phase_info.get("emoji", "🌙"),
        "message": message,
        "phase_theme": phase_info.get("theme", ""),
        "phase_energy": phase_info.get("energy", ""),
        "phase_best_for": phase_info.get("best_for", []),
        "is_optimal": moon_phase in best_phases
    }


def get_habit_streak(
    completions: List[Dict[str, Any]],
    frequency: str = "daily"
) -> Dict[str, Any]:
    """
    Calculate habit streak from completions.
    
    Args:
        completions: List of completion dicts with 'date' field
        frequency: Habit frequency (daily, weekly, lunar_cycle)
        
    Returns:
        Dict with streak information
    """
    if not completions:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_completions": 0,
            "streak_message": "Start your streak today! 🌱",
            "streak_emoji": "🌱"
        }
    
    # Sort by date descending
    sorted_completions = sorted(
        completions,
        key=lambda x: x.get("date", ""),
        reverse=True
    )
    
    # Get unique dates
    unique_dates = sorted(set(c.get("date", "") for c in sorted_completions), reverse=True)
    
    if frequency == "daily":
        # Calculate daily streak
        today = datetime.now().date()
        current_streak = 0
        expected_date = today
        
        for date_str in unique_dates:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date == expected_date:
                    current_streak += 1
                    expected_date = expected_date - timedelta(days=1)
                elif date == expected_date - timedelta(days=1):
                    # Allow one day gap
                    current_streak += 1
                    expected_date = date - timedelta(days=1)
                else:
                    break
            except ValueError:
                continue
        
        # Calculate longest streak
        longest = 0
        current = 0
        prev_date = None
        
        for date_str in sorted(unique_dates):
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if prev_date is None or (date - prev_date).days <= 1:
                    current += 1
                else:
                    current = 1
                longest = max(longest, current)
                prev_date = date
            except ValueError:
                continue
        
    elif frequency == "weekly":
        # Calculate weekly streak (at least 1 completion per week)
        weeks_completed = set()
        for c in sorted_completions:
            try:
                date = datetime.strptime(c.get("date", ""), "%Y-%m-%d")
                week_key = f"{date.year}-W{date.isocalendar()[1]:02d}"
                weeks_completed.add(week_key)
            except ValueError:
                continue
        
        current_streak = len(weeks_completed)  # Simplified
        longest = current_streak
        
    else:
        # Lunar cycle (approximately monthly)
        current_streak = len(unique_dates) // 4 if unique_dates else 0
        longest = current_streak
    
    # Generate message
    if current_streak == 0:
        message = "Start your streak today! 🌱"
    elif current_streak == 1:
        message = "Great start! Keep the momentum going! ⭐"
    elif current_streak < 7:
        message = f"Building momentum! {current_streak} days strong! 🔥"
    elif current_streak < 21:
        message = f"Incredible! {current_streak} days - you're forming a real habit! 💪"
    elif current_streak < 30:
        message = f"Almost a full lunar cycle! {current_streak} days! 🌙"
    else:
        message = f"Master level! {current_streak} days - you've transcended! 🏆✨"
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest,
        "total_completions": len(sorted_completions),
        "last_completion": unique_dates[0] if unique_dates else None,
        "streak_message": message,
        "streak_emoji": (
            "🏆" if current_streak >= 30 else
            "🔥" if current_streak >= 7 else
            "⭐" if current_streak >= 1 else
            "🌱"
        )
    }


def get_lunar_habit_recommendations(
    moon_phase: str,
    existing_habits: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get habit recommendations based on current moon phase.
    
    Args:
        moon_phase: Current moon phase key
        existing_habits: User's existing habits to personalize
        
    Returns:
        Dict with recommendations
    """
    phase_info = LUNAR_HABIT_GUIDANCE.get(moon_phase, {})
    ideal_categories = phase_info.get("ideal_habits", [])
    
    # Find matching categories
    recommended = []
    for cat_key in ideal_categories:
        if cat_key in HABIT_CATEGORIES:
            cat = HABIT_CATEGORIES[cat_key]
            recommended.append({
                "category": cat_key,
                "name": cat["name"],
                "emoji": cat["emoji"],
                "description": cat["description"],
                "why": f"Aligned with {phase_info.get('theme', 'this phase')} energy"
            })
    
    # Check existing habits alignment
    aligned_existing = []
    if existing_habits:
        for habit in existing_habits:
            cat = habit.get("category", "")
            if cat in ideal_categories:
                aligned_existing.append({
                    "habit_name": habit.get("name"),
                    "category": cat,
                    "message": "Great time to focus on this habit!"
                })
    
    return {
        "moon_phase": moon_phase,
        "phase_info": phase_info,
        "recommended_categories": recommended,
        "aligned_existing_habits": aligned_existing,
        "phase_best_for": phase_info.get("best_for", []),
        "phase_avoid": phase_info.get("avoid", []),
        "power_tip": f"During the {phase_info.get('phase_name', '')}, "
                    f"focus on {phase_info.get('theme', 'your practice').lower()}."
    }


def calculate_habit_analytics(
    habit: Dict[str, Any],
    completions: List[Dict[str, Any]],
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Calculate analytics for a habit over a period.
    
    Args:
        habit: Habit definition dict
        completions: List of completion dicts
        period_days: Number of days to analyze
        
    Returns:
        Dict with analytics
    """
    if not completions:
        return {
            "completion_rate": 0.0,
            "total_completions": 0,
            "by_phase": {},
            "by_weekday": {},
            "best_phase": None,
            "best_day": None,
            "insights": ["Start tracking to discover your patterns!"]
        }
    
    # Filter to period
    cutoff = (datetime.now() - timedelta(days=period_days)).isoformat()
    period_completions = [
        c for c in completions
        if c.get("completed_at", c.get("date", "")) >= cutoff
    ]
    
    # Calculate completion rate
    frequency = habit.get("frequency", "daily")
    target = habit.get("target_count", 1)
    
    if frequency == "daily":
        expected = period_days * target
    elif frequency == "weekly":
        expected = (period_days // 7) * target
    else:
        expected = target  # Lunar cycle
    
    completion_rate = min(100, (len(period_completions) / max(1, expected)) * 100)
    
    # Analyze by moon phase
    by_phase = defaultdict(int)
    for c in period_completions:
        phase = c.get("moon_phase")
        if phase:
            by_phase[phase] += 1
    
    # Analyze by weekday
    by_weekday = defaultdict(int)
    for c in period_completions:
        weekday = c.get("weekday")
        if weekday:
            by_weekday[weekday] += 1
    
    # Find best phase and day
    best_phase = max(by_phase.keys(), key=lambda k: by_phase[k]) if by_phase else None
    best_day = max(by_weekday.keys(), key=lambda k: by_weekday[k]) if by_weekday else None
    
    # Generate insights
    insights = []
    
    if completion_rate >= 80:
        insights.append("🏆 Excellent consistency! You're mastering this habit.")
    elif completion_rate >= 60:
        insights.append("👍 Good progress! Keep building on your momentum.")
    elif completion_rate >= 40:
        insights.append("📈 Making progress. Try aligning with optimal moon phases.")
    else:
        insights.append("💪 Room to grow. Start small and build consistency.")
    
    if best_phase:
        phase_name = LUNAR_HABIT_GUIDANCE.get(best_phase, {}).get("phase_name", best_phase)
        insights.append(f"🌙 You perform best during the {phase_name}.")
    
    if best_day:
        insights.append(f"📅 {best_day} is your strongest day for this habit.")
    
    return {
        "completion_rate": round(completion_rate, 1),
        "total_completions": len(period_completions),
        "period_days": period_days,
        "by_phase": dict(by_phase),
        "by_weekday": dict(by_weekday),
        "best_phase": best_phase,
        "best_day": best_day,
        "target_per_period": expected,
        "insights": insights
    }


def get_today_habit_forecast(
    habits: List[Dict[str, Any]],
    moon_phase: str,
    completions_today: List[int] = None
) -> Dict[str, Any]:
    """
    Get today's habit forecast with lunar guidance.
    
    Args:
        habits: List of user's habits
        moon_phase: Current moon phase
        completions_today: List of habit IDs completed today
        
    Returns:
        Dict with today's forecast
    """
    completed_ids = set(completions_today or [])
    phase_info = LUNAR_HABIT_GUIDANCE.get(moon_phase, {})
    ideal_categories = phase_info.get("ideal_habits", [])
    
    habit_forecasts = []
    for habit in habits:
        if not habit.get("is_active", True):
            continue
        
        cat = habit.get("category", "")
        alignment = calculate_lunar_alignment_score(cat, moon_phase)
        
        habit_forecasts.append({
            "habit_id": habit.get("id"),
            "name": habit.get("name"),
            "category": cat,
            "category_emoji": habit.get("category_emoji", "✨"),
            "is_completed": habit.get("id") in completed_ids,
            "alignment_score": alignment["score"],
            "alignment": alignment["alignment"],
            "is_optimal_phase": alignment["is_optimal"],
            "tip": alignment["message"]
        })
    
    # Sort by alignment score
    habit_forecasts.sort(key=lambda x: x["alignment_score"], reverse=True)
    
    # Calculate overall score
    total_habits = len(habit_forecasts)
    completed = len(completed_ids)
    optimal_count = sum(1 for h in habit_forecasts if h["is_optimal_phase"])
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "moon_phase": moon_phase,
        "phase_info": {
            "name": phase_info.get("phase_name", ""),
            "emoji": phase_info.get("emoji", "🌙"),
            "theme": phase_info.get("theme", ""),
            "energy": phase_info.get("energy", "")
        },
        "habits": habit_forecasts,
        "summary": {
            "total_habits": total_habits,
            "completed": completed,
            "completion_rate": round((completed / max(1, total_habits)) * 100, 1),
            "optimal_today": optimal_count
        },
        "daily_tip": phase_info.get("best_for", ["Focus on what matters most"])[0]
    }


def get_lunar_cycle_report(
    habits: List[Dict[str, Any]],
    completions: List[Dict[str, Any]],
    cycle_days: int = 29
) -> Dict[str, Any]:
    """
    Generate a report for a complete lunar cycle.
    
    Args:
        habits: List of user's habits
        completions: All completions in the cycle
        cycle_days: Length of lunar cycle (default 29 days)
        
    Returns:
        Dict with lunar cycle report
    """
    # Group completions by habit
    habit_completions = defaultdict(list)
    for c in completions:
        habit_completions[c.get("habit_id")].append(c)
    
    # Analyze each habit
    habit_reports = []
    for habit in habits:
        habit_id = habit.get("id")
        h_completions = habit_completions.get(habit_id, [])
        
        analytics = calculate_habit_analytics(habit, h_completions, cycle_days)
        streak = get_habit_streak(h_completions, habit.get("frequency", "daily"))
        
        habit_reports.append({
            "habit_id": habit_id,
            "name": habit.get("name"),
            "category": habit.get("category"),
            "completion_rate": analytics["completion_rate"],
            "total_completions": analytics["total_completions"],
            "current_streak": streak["current_streak"],
            "best_phase": analytics["best_phase"],
            "best_day": analytics["best_day"],
            "insights": analytics["insights"]
        })
    
    # Overall stats
    total_completions = sum(h["total_completions"] for h in habit_reports)
    avg_rate = sum(h["completion_rate"] for h in habit_reports) / max(1, len(habit_reports))
    
    # Phase distribution
    phase_totals = defaultdict(int)
    for c in completions:
        phase = c.get("moon_phase")
        if phase:
            phase_totals[phase] += 1
    
    return {
        "cycle_days": cycle_days,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_habits": len(habits),
            "total_completions": total_completions,
            "average_completion_rate": round(avg_rate, 1),
            "best_performing_habit": max(habit_reports, key=lambda x: x["completion_rate"])["name"] if habit_reports else None
        },
        "habits": habit_reports,
        "phase_distribution": dict(phase_totals),
        "moon_wisdom": (
            "You've completed a full lunar cycle of habit tracking! "
            "Notice which phases feel most natural for your practices."
        )
    }
