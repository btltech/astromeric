"""
Journal & Accountability Engine

Tracks prediction outcomes, analyzes accuracy, and provides insights
on which types of predictions resonate most with the user.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
from collections import defaultdict
import json


# Outcome types for tracking prediction accuracy
OutcomeType = Literal["yes", "no", "partial", "pending"]


# Reading categories for accuracy tracking
READING_CATEGORIES = {
    "transits": "Planetary Transits",
    "moon_phases": "Moon Phases",
    "retrogrades": "Retrograde Periods",
    "aspects": "Planetary Aspects",
    "houses": "House Activations",
    "numerology": "Numerology",
    "compatibility": "Relationship",
    "career": "Career & Finance",
    "health": "Health & Wellness",
    "general": "General Guidance"
}


# Feedback emoji mapping
FEEDBACK_EMOJI = {
    "yes": "✅",
    "no": "❌", 
    "partial": "🔶",
    "pending": "⏳",
    "neutral": "➖"
}


def add_journal_entry(
    reading_id: int,
    entry: str,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Add a journal entry to a reading.
    
    Args:
        reading_id: The reading to attach the journal to
        entry: The journal text
        timestamp: When the entry was made (defaults to now)
        
    Returns:
        Dict with entry metadata
    """
    ts = timestamp or datetime.now()
    
    return {
        "reading_id": reading_id,
        "entry": entry,
        "timestamp": ts.isoformat(),
        "word_count": len(entry.split()),
        "character_count": len(entry)
    }


def record_outcome(
    reading_id: int,
    outcome: OutcomeType,
    categories: List[str] = None,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Record whether a prediction came true.
    
    Args:
        reading_id: The reading being evaluated
        outcome: Whether prediction was accurate (yes/no/partial/pending)
        categories: Which categories of the reading to evaluate
        notes: Optional notes about the outcome
        
    Returns:
        Dict with outcome record
    """
    return {
        "reading_id": reading_id,
        "outcome": outcome,
        "outcome_emoji": FEEDBACK_EMOJI.get(outcome, "❓"),
        "categories": categories or ["general"],
        "notes": notes,
        "recorded_at": datetime.now().isoformat()
    }


def calculate_accuracy_stats(
    readings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate prediction accuracy statistics from a list of readings with feedback.
    
    Args:
        readings: List of reading dicts with 'feedback' and optionally 'scope' fields
        
    Returns:
        Dict with accuracy statistics
    """
    if not readings:
        return {
            "total_readings": 0,
            "rated_readings": 0,
            "accuracy_rate": 0.0,
            "by_outcome": {},
            "by_scope": {},
            "trend": "neutral",
            "trend_emoji": "➖",
            "message": "No readings to analyze yet. Keep logging your experiences!"
        }
    
    total = len(readings)
    rated = 0
    outcome_counts = defaultdict(int)
    scope_accuracy = defaultdict(lambda: {"yes": 0, "no": 0, "partial": 0, "neutral": 0, "total": 0})
    
    # Recent vs older accuracy for trend
    recent_accurate = 0
    recent_total = 0
    older_accurate = 0
    older_total = 0
    
    # Sort by date if available
    sorted_readings = sorted(
        readings,
        key=lambda r: r.get("date", r.get("created_at", "")),
        reverse=True
    )
    midpoint = len(sorted_readings) // 2
    
    for i, reading in enumerate(sorted_readings):
        feedback = reading.get("feedback")
        scope = reading.get("scope", "general")
        
        if feedback and feedback in ["yes", "no", "partial", "neutral"]:
            rated += 1
            outcome_counts[feedback] += 1
            scope_accuracy[scope][feedback] += 1
            scope_accuracy[scope]["total"] += 1
            
            # Track for trend analysis
            is_accurate = feedback == "yes" or feedback == "partial"
            if i < midpoint:
                recent_total += 1
                if is_accurate:
                    recent_accurate += 1
            else:
                older_total += 1
                if is_accurate:
                    older_accurate += 1
    
    # Calculate overall accuracy rate
    positive = outcome_counts.get("yes", 0) + outcome_counts.get("partial", 0) * 0.5
    accuracy_rate = (positive / rated * 100) if rated > 0 else 0.0
    
    # Calculate scope-level accuracy
    scope_stats = {}
    for scope, counts in scope_accuracy.items():
        scope_total = counts["total"]
        if scope_total > 0:
            scope_pos = counts["yes"] + counts["partial"] * 0.5
            scope_stats[scope] = {
                "accuracy": round(scope_pos / scope_total * 100, 1),
                "total": scope_total,
                "yes": counts["yes"],
                "no": counts["no"],
                "partial": counts["partial"]
            }
    
    # Determine trend
    if recent_total > 0 and older_total > 0:
        recent_rate = recent_accurate / recent_total
        older_rate = older_accurate / older_total
        if recent_rate > older_rate + 0.1:
            trend = "improving"
            trend_emoji = "📈"
        elif recent_rate < older_rate - 0.1:
            trend = "declining"
            trend_emoji = "📉"
        else:
            trend = "stable"
            trend_emoji = "➡️"
    else:
        trend = "neutral"
        trend_emoji = "➖"
    
    # Generate message based on accuracy
    if accuracy_rate >= 75:
        message = "Excellent! Your readings have been highly accurate. Trust the cosmic guidance."
    elif accuracy_rate >= 50:
        message = "Good alignment! Your readings are resonating well with your experiences."
    elif accuracy_rate >= 25:
        message = "Some hits, some misses. Consider how you interpret the guidance."
    elif rated > 0:
        message = "Challenging period. Remember, readings show potential, not destiny."
    else:
        message = "Start rating your readings to track accuracy over time!"
    
    return {
        "total_readings": total,
        "rated_readings": rated,
        "unrated_readings": total - rated,
        "accuracy_rate": round(accuracy_rate, 1),
        "by_outcome": dict(outcome_counts),
        "by_scope": scope_stats,
        "trend": trend,
        "trend_emoji": trend_emoji,
        "message": message
    }


def get_reading_insights(
    readings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze readings to find patterns and insights.
    
    Args:
        readings: List of reading dicts with feedback and journals
        
    Returns:
        Dict with insights about reading patterns
    """
    if not readings:
        return {
            "total_journals": 0,
            "best_scope": None,
            "worst_scope": None,
            "journaling_streak": 0,
            "insights": ["Start journaling to discover your cosmic patterns!"]
        }
    
    # Count journals and feedback
    journal_count = sum(1 for r in readings if r.get("journal"))
    stats = calculate_accuracy_stats(readings)
    scope_stats = stats.get("by_scope", {})
    
    # Find best and worst performing scopes
    best_scope = None
    worst_scope = None
    best_accuracy = 0
    worst_accuracy = 100
    
    for scope, data in scope_stats.items():
        if data["total"] >= 3:  # Minimum sample size
            if data["accuracy"] > best_accuracy:
                best_accuracy = data["accuracy"]
                best_scope = scope
            if data["accuracy"] < worst_accuracy:
                worst_accuracy = data["accuracy"]
                worst_scope = scope
    
    # Calculate journaling streak
    sorted_readings = sorted(
        [r for r in readings if r.get("journal")],
        key=lambda r: r.get("date", r.get("created_at", "")),
        reverse=True
    )
    
    streak = 0
    today = datetime.now().date()
    
    for reading in sorted_readings:
        reading_date = reading.get("date", "")
        if reading_date:
            try:
                rd = datetime.fromisoformat(reading_date.replace("Z", "+00:00")).date()
                expected_date = today - timedelta(days=streak)
                if rd == expected_date:
                    streak += 1
                else:
                    break
            except ValueError:
                break
    
    # Generate insights
    insights = []
    
    if best_scope and best_accuracy > 60:
        insights.append(
            f"Your {best_scope} readings are most accurate ({best_accuracy:.0f}%). "
            f"Pay extra attention to these forecasts!"
        )
    
    if worst_scope and worst_accuracy < 40 and stats["rated_readings"] >= 5:
        insights.append(
            f"Your {worst_scope} readings may need different interpretation. "
            f"Consider journaling more to understand the messages."
        )
    
    if stats["trend"] == "improving":
        insights.append(
            "Your accuracy is improving! You're getting better at receiving cosmic messages."
        )
    elif stats["trend"] == "declining":
        insights.append(
            "Recent readings haven't matched as well. Times of change can affect clarity."
        )
    
    if journal_count > 0:
        journal_rate = journal_count / len(readings) * 100
        if journal_rate >= 80:
            insights.append(
                "Excellent journaling habit! Writing helps integrate cosmic guidance."
            )
        elif journal_rate < 30:
            insights.append(
                "Try journaling more often to deepen your connection with readings."
            )
    
    if streak >= 7:
        insights.append(
            f"🔥 {streak}-day journaling streak! Your consistency is paying off."
        )
    elif streak >= 3:
        insights.append(
            f"Nice! {streak}-day streak. Keep the momentum going!"
        )
    
    if not insights:
        insights.append("Keep tracking your readings to unlock personalized insights!")
    
    return {
        "total_journals": journal_count,
        "best_scope": best_scope,
        "best_scope_accuracy": best_accuracy if best_scope else None,
        "worst_scope": worst_scope,
        "worst_scope_accuracy": worst_accuracy if worst_scope else None,
        "journaling_streak": streak,
        "insights": insights
    }


def analyze_prediction_patterns(
    readings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze patterns in prediction accuracy over time and categories.
    
    Args:
        readings: List of readings with feedback
        
    Returns:
        Dict with pattern analysis
    """
    if not readings or len(readings) < 3:
        return {
            "patterns_found": False,
            "message": "Need at least 3 rated readings to find patterns."
        }
    
    # Group readings by day of week
    day_accuracy = defaultdict(lambda: {"accurate": 0, "total": 0})
    
    for reading in readings:
        feedback = reading.get("feedback")
        date_str = reading.get("date", "")
        
        if feedback and date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                day_name = dt.strftime("%A")
                day_accuracy[day_name]["total"] += 1
                if feedback in ["yes", "partial"]:
                    day_accuracy[day_name]["accurate"] += 1
            except ValueError:
                pass
    
    # Find best and worst days
    day_rates = {}
    for day, counts in day_accuracy.items():
        if counts["total"] >= 2:
            day_rates[day] = counts["accurate"] / counts["total"] * 100
    
    best_day = max(day_rates, key=day_rates.get) if day_rates else None
    worst_day = min(day_rates, key=day_rates.get) if day_rates else None
    
    # Monthly patterns
    month_accuracy = defaultdict(lambda: {"accurate": 0, "total": 0})
    
    for reading in readings:
        feedback = reading.get("feedback")
        date_str = reading.get("date", "")
        
        if feedback and date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                month = dt.strftime("%B")
                month_accuracy[month]["total"] += 1
                if feedback in ["yes", "partial"]:
                    month_accuracy[month]["accurate"] += 1
            except ValueError:
                pass
    
    patterns = []
    
    if best_day and day_rates.get(best_day, 0) > 70:
        patterns.append({
            "type": "best_day",
            "value": best_day,
            "accuracy": round(day_rates[best_day], 1),
            "insight": f"{best_day} readings tend to be most accurate for you."
        })
    
    if worst_day and best_day != worst_day and day_rates.get(worst_day, 100) < 40:
        patterns.append({
            "type": "challenging_day",
            "value": worst_day,
            "accuracy": round(day_rates[worst_day], 1),
            "insight": f"{worst_day} readings may need extra reflection."
        })
    
    return {
        "patterns_found": len(patterns) > 0,
        "patterns": patterns,
        "by_day": {d: round(r, 1) for d, r in day_rates.items()},
        "sample_size": len([r for r in readings if r.get("feedback")])
    }


def get_journal_prompts(
    scope: str = "daily",
    reading_themes: List[str] = None
) -> List[Dict[str, str]]:
    """
    Generate journal prompts based on reading scope and themes.
    
    Args:
        scope: daily, weekly, or monthly
        reading_themes: Themes from the reading to reflect on
        
    Returns:
        List of prompt dicts with text and category
    """
    base_prompts = {
        "daily": [
            {
                "text": "What energy did you notice most today?",
                "category": "awareness"
            },
            {
                "text": "Did anything in today's reading resonate with you? Why?",
                "category": "reflection"
            },
            {
                "text": "What's one action you can take tomorrow based on today's guidance?",
                "category": "action"
            }
        ],
        "weekly": [
            {
                "text": "What was the theme of your week? How does it relate to the reading?",
                "category": "reflection"
            },
            {
                "text": "What challenges did you face, and how did cosmic energy influence them?",
                "category": "growth"
            },
            {
                "text": "What are you grateful for this week?",
                "category": "gratitude"
            }
        ],
        "monthly": [
            {
                "text": "What major shifts did you experience this month?",
                "category": "reflection"
            },
            {
                "text": "Which predictions came true? Which didn't? What might that mean?",
                "category": "accuracy"
            },
            {
                "text": "What intentions do you want to set for next month?",
                "category": "intention"
            }
        ]
    }
    
    prompts = base_prompts.get(scope, base_prompts["daily"]).copy()
    
    # Add theme-specific prompts
    if reading_themes:
        for theme in reading_themes[:3]:  # Limit to 3 themes
            if theme.lower() in ["love", "romance", "relationships"]:
                prompts.append({
                    "text": "How have your relationships evolved with this cosmic energy?",
                    "category": "relationships"
                })
            elif theme.lower() in ["career", "work", "money", "finance"]:
                prompts.append({
                    "text": "What opportunities or challenges showed up in your work life?",
                    "category": "career"
                })
            elif theme.lower() in ["health", "wellness", "energy"]:
                prompts.append({
                    "text": "How has your physical and emotional energy been this period?",
                    "category": "wellness"
                })
            elif theme.lower() in ["creativity", "inspiration", "ideas"]:
                prompts.append({
                    "text": "What creative insights or inspirations came to you?",
                    "category": "creativity"
                })
    
    return prompts


def create_accountability_report(
    readings: List[Dict[str, Any]],
    period: str = "month"
) -> Dict[str, Any]:
    """
    Create a comprehensive accountability report for a period.
    
    Args:
        readings: All readings for the period
        period: week, month, or year
        
    Returns:
        Dict with full accountability report
    """
    stats = calculate_accuracy_stats(readings)
    insights = get_reading_insights(readings)
    patterns = analyze_prediction_patterns(readings)
    
    # Count entries and activity
    total_readings = len(readings)
    readings_with_feedback = len([r for r in readings if r.get("feedback")])
    readings_with_journal = len([r for r in readings if r.get("journal")])
    
    # Engagement score (0-100)
    engagement = 0
    if total_readings > 0:
        feedback_rate = readings_with_feedback / total_readings
        journal_rate = readings_with_journal / total_readings
        engagement = round((feedback_rate * 50 + journal_rate * 50), 1)
    
    # Generate recommendations
    recommendations = []
    
    if engagement < 30:
        recommendations.append({
            "type": "engagement",
            "text": "Try tracking more readings to get better insights into your cosmic patterns."
        })
    
    if stats["accuracy_rate"] > 0 and stats["accuracy_rate"] < 40:
        recommendations.append({
            "type": "interpretation",
            "text": "Consider journaling about how you interpret readings to find what resonates."
        })
    
    if insights["journaling_streak"] == 0 and readings_with_journal < total_readings * 0.3:
        recommendations.append({
            "type": "journaling",
            "text": "Regular journaling can deepen your understanding of cosmic guidance."
        })
    
    if patterns.get("patterns_found"):
        for pattern in patterns.get("patterns", []):
            recommendations.append({
                "type": "pattern",
                "text": pattern["insight"]
            })
    
    if not recommendations:
        recommendations.append({
            "type": "encouragement",
            "text": "Great work! Keep tracking to maintain your cosmic awareness."
        })
    
    return {
        "period": period,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_readings": total_readings,
            "with_feedback": readings_with_feedback,
            "with_journal": readings_with_journal,
            "engagement_score": engagement,
            "engagement_rating": (
                "Excellent" if engagement >= 75 else
                "Good" if engagement >= 50 else
                "Growing" if engagement >= 25 else
                "Getting Started"
            )
        },
        "accuracy": stats,
        "insights": insights,
        "patterns": patterns,
        "recommendations": recommendations
    }


def format_reading_for_journal(
    reading: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format a reading for display in journal view.
    
    Args:
        reading: Raw reading data
        
    Returns:
        Formatted reading dict
    """
    # Parse content if it's a JSON string
    content = reading.get("content", {})
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {"raw": content}
    
    # Extract key info
    feedback = reading.get("feedback")
    journal = reading.get("journal", "")
    scope = reading.get("scope", "daily")
    date = reading.get("date", "")
    
    # Format date nicely
    formatted_date = ""
    if date:
        try:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%B %d, %Y")
        except ValueError:
            formatted_date = date
    
    return {
        "id": reading.get("id"),
        "scope": scope,
        "scope_label": scope.capitalize(),
        "date": date,
        "formatted_date": formatted_date,
        "has_journal": bool(journal),
        "journal_preview": journal[:100] + "..." if len(journal) > 100 else journal,
        "journal_full": journal,
        "feedback": feedback,
        "feedback_emoji": FEEDBACK_EMOJI.get(feedback, ""),
        "content_summary": content.get("summary", content.get("theme", ""))
    }
