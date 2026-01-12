"""
V1 API Router: Habits
Provides habit tracking with lunar cycle alignment and analytics.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from ..engine.habit_tracker import (
    HABIT_CATEGORIES,
    LUNAR_HABIT_GUIDANCE,
    calculate_lunar_alignment_score,
    get_lunar_habit_recommendations,
    create_habit,
    log_habit_completion,
    get_habit_streak,
    calculate_habit_analytics,
    get_today_habit_forecast,
    get_lunar_cycle_report,
)

# Request models
class HabitCreateRequest(BaseModel):
    """Request to create a new habit."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., description="Habit category key")
    frequency: str = Field(default="daily", pattern="^(daily|weekly|lunar_cycle)$")
    target_count: int = Field(default=1, ge=1, le=10)
    description: Optional[str] = Field(default="", max_length=500)


class HabitLogRequest(BaseModel):
    """Request to log a habit completion."""
    habit_id: int
    notes: Optional[str] = Field(default="", max_length=500)


class HabitAnalyticsRequest(BaseModel):
    """Request for habit analytics."""
    habit_id: int
    period_days: int = Field(default=30, ge=7, le=365)


class HabitForecastRequest(BaseModel):
    """Request for today's habit forecast."""
    habits: List[Dict[str, Any]]
    completions_today: Optional[List[int]] = None
    
    model_config = {"extra": "allow"}


class StreakRequest(BaseModel):
    """Request for streak calculation."""
    completions: List[Dict[str, Any]]
    
    model_config = {"extra": "allow"}


router = APIRouter()


@router.get("/habits/categories", tags=["Habits"])
def get_habit_categories():
    """
    Get all available habit categories with their descriptions
    and lunar phase recommendations.
    """
    categories = []
    for key, cat in HABIT_CATEGORIES.items():
        categories.append({
            "id": key,
            "name": cat["name"],
            "emoji": cat["emoji"],
            "description": cat["description"],
            "best_phases": cat["best_phases"],
            "avoid_phases": cat["avoid_phases"]
        })
    return {"categories": categories}


@router.get("/habits/lunar-guidance", tags=["Habits"])
def get_lunar_guidance():
    """
    Get habit guidance for all moon phases.
    """
    phases = []
    for key, phase in LUNAR_HABIT_GUIDANCE.items():
        phases.append({
            "id": key,
            "name": phase["phase_name"],
            "emoji": phase["emoji"],
            "theme": phase["theme"],
            "best_for": phase["best_for"],
            "avoid": phase["avoid"],
            "energy": phase["energy"],
            "ideal_habits": phase["ideal_habits"]
        })
    return {"phases": phases}


@router.get("/habits/lunar-guidance/{phase}", tags=["Habits"])
def get_phase_guidance(phase: str):
    """
    Get habit guidance for a specific moon phase.
    """
    valid_phases = list(LUNAR_HABIT_GUIDANCE.keys())
    if phase not in valid_phases:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {valid_phases}"
        )
    
    phase_info = LUNAR_HABIT_GUIDANCE[phase]
    return {
        "phase": phase,
        "phase_name": phase_info["phase_name"],
        "emoji": phase_info["emoji"],
        "theme": phase_info["theme"],
        "energy": phase_info["energy"],
        "best_for": phase_info["best_for"],
        "avoid": phase_info["avoid"],
        "ideal_habits": phase_info["ideal_habits"],
        "power_modifier": phase_info["power_score_modifier"]
    }


@router.post("/habits/alignment", tags=["Habits"])
def check_habit_alignment(
    category: str = Query(..., description="Habit category key"),
    moon_phase: str = Query(..., description="Moon phase key")
):
    """
    Check how well a habit category aligns with a moon phase.
    Returns alignment score and guidance.
    """
    if category not in HABIT_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(HABIT_CATEGORIES.keys())}"
        )
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return calculate_lunar_alignment_score(category, moon_phase)


@router.post("/habits/recommendations", tags=["Habits"])
def get_recommendations(
    moon_phase: str = Query(..., description="Current moon phase key"),
    existing_habits: Optional[List[Dict[str, Any]]] = None
):
    """
    Get habit recommendations based on the current moon phase.
    Optionally provide existing habits for personalized suggestions.
    """
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return get_lunar_habit_recommendations(moon_phase, existing_habits)


@router.post("/habits/create", tags=["Habits"])
def create_new_habit(req: HabitCreateRequest):
    """
    Create a new habit definition.
    Returns the habit object (not persisted - for session use).
    """
    if req.category not in HABIT_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {list(HABIT_CATEGORIES.keys())}"
        )
    
    habit = create_habit(
        name=req.name,
        category=req.category,
        frequency=req.frequency,
        target_count=req.target_count,
        description=req.description
    )
    
    return {"success": True, "habit": habit}


@router.post("/habits/log", tags=["Habits"])
def log_completion(
    req: HabitLogRequest,
    moon_phase: Optional[str] = Query(default=None, description="Current moon phase")
):
    """
    Log a habit completion.
    Returns the completion record.
    """
    completion = log_habit_completion(
        habit_id=req.habit_id,
        moon_phase=moon_phase,
        notes=req.notes
    )
    
    return {"success": True, "completion": completion}


@router.post("/habits/streak", tags=["Habits"])
def calculate_streak(
    req: StreakRequest,
    frequency: str = Query(default="daily", pattern="^(daily|weekly|lunar_cycle)$")
):
    """
    Calculate habit streak from a list of completions.
    """
    return get_habit_streak(req.completions, frequency)


@router.post("/habits/analytics", tags=["Habits"])
def get_analytics(
    habit: Dict[str, Any],
    completions: List[Dict[str, Any]],
    period_days: int = Query(default=30, ge=7, le=365)
):
    """
    Get detailed analytics for a habit over a period.
    """
    return calculate_habit_analytics(habit, completions, period_days)


@router.post("/habits/today", tags=["Habits"])
def get_today_forecast(
    req: HabitForecastRequest,
    moon_phase: str = Query(..., description="Current moon phase key")
):
    """
    Get today's habit forecast with lunar alignment for each habit.
    """
    if moon_phase not in LUNAR_HABIT_GUIDANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phase. Must be one of: {list(LUNAR_HABIT_GUIDANCE.keys())}"
        )
    
    return get_today_habit_forecast(
        habits=req.habits,
        moon_phase=moon_phase,
        completions_today=req.completions_today
    )


@router.post("/habits/lunar-report", tags=["Habits"])
def get_lunar_report(
    habits: List[Dict[str, Any]],
    completions: List[Dict[str, Any]],
    cycle_days: int = Query(default=29, ge=14, le=45)
):
    """
    Generate a lunar cycle report for habits.
    Analyzes performance over a complete moon cycle.
    """
    return get_lunar_cycle_report(habits, completions, cycle_days)
