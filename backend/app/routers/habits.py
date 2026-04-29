"""API v2 - Habit Tracking Endpoint.

Note: This module uses an in-memory store for now (no DB). That removes hardcoded
mock responses so clients can create/list/log habits during a single process
runtime.
"""

from datetime import date, datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from ..exceptions import StructuredLogger
from ..schemas import ApiResponse, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/habits", tags=["Habits"])


# ==========================================================================
# IN-MEMORY STORE (TEMPORARY)
# ==========================================================================


class _StoredHabit(BaseModel):
    id: str
    name: str
    description: str
    category: str
    created_date: datetime


class _StoredHabitEntry(BaseModel):
    id: str
    habit_id: str
    category: str
    date: datetime
    completed: bool
    notes: Optional[str] = None


_HABITS: Dict[str, _StoredHabit] = {}
_ENTRIES: List[_StoredHabitEntry] = []


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _entries_for_habit(habit_id: str) -> List[_StoredHabitEntry]:
    return [e for e in _ENTRIES if e.habit_id == habit_id]


def _compute_summary(habit: _StoredHabit) -> "HabitSummary":
    entries = sorted(_entries_for_habit(habit.id), key=lambda e: e.date)
    completed_entries = [e for e in entries if e.completed]

    # Basic stats
    completed_days = len({e.date.date() for e in completed_entries})
    total_days = len({e.date.date() for e in entries})

    # Streaks: count consecutive completed days ending today (UTC), and longest streak.
    completed_dates = sorted({e.date.date() for e in completed_entries})
    longest_streak = 0
    current_streak = 0

    run = 0
    prev: Optional[date] = None
    for d in completed_dates:
        if prev is None or (d - prev).days == 1:
            run += 1
        else:
            run = 1
        longest_streak = max(longest_streak, run)
        prev = d

    # Current streak must end at today or yesterday to be meaningful.
    if completed_dates:
        last = completed_dates[-1]
        if last == _today_utc():
            # Count backwards from today.
            streak = 1
            cursor = last
            completed_set = set(completed_dates)
            while True:
                cursor = cursor.replace(day=cursor.day)  # no-op; clarity
                prev_day = cursor.fromordinal(cursor.toordinal() - 1)
                if prev_day in completed_set:
                    streak += 1
                    cursor = prev_day
                else:
                    break
            current_streak = streak
        elif (_today_utc() - last).days == 1:
            current_streak = 1

    completion_rate = (completed_days / total_days) if total_days > 0 else 0.0
    last_completed = completed_entries[-1].date if completed_entries else None

    return HabitSummary(
        habit_id=habit.id,
        habit_name=habit.name,
        total_days=total_days,
        completed_days=completed_days,
        current_streak=current_streak,
        longest_streak=longest_streak,
        completion_rate=round(completion_rate, 4),
        last_completed=last_completed,
    )


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class HabitEntry(BaseModel):
    """Single habit tracking entry."""

    id: str
    habit_name: str
    category: str
    date: datetime
    completed: bool
    notes: Optional[str] = None
    streak_days: int = 0


class HabitSummary(BaseModel):
    """Habit tracking summary."""

    habit_id: str
    habit_name: str
    total_days: int
    completed_days: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    last_completed: Optional[datetime] = None


class HabitResponse(BaseModel):
    """Complete habit with entries and summary."""

    id: str
    name: str
    description: str
    category: str
    created_date: datetime
    entries: List[HabitEntry]
    summary: HabitSummary


class CreateHabitBody(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    frequency: Optional[str] = None
    description: Optional[str] = None


class LogHabitEntryBody(BaseModel):
    habit_id: str | int = Field(..., description="Habit identifier")
    completed: bool
    note: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/create", response_model=ApiResponse[HabitResponse])
async def create_habit(
    request: Request,
    body: Optional[CreateHabitBody] = Body(default=None),
    # Back-compat (query params) for older clients
    name: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> ApiResponse[HabitResponse]:
    """
    Create a new habit to track.

    ## Parameters
    - **name**: Habit name
    - **category**: Category (health, meditation, learning, exercise, etc.)
    - **description**: Optional description

    ## Response
    Returns newly created habit with metadata.
    """
    request_id = request.state.request_id

    try:
        habit_name = (body.name if body else name) or ""
        habit_category = (body.category if body else category) or ""
        habit_description = (
            body.description
            if body and body.description is not None
            else (description or "")
        )

        if not habit_name or len(habit_name.strip()) == 0:
            raise ValueError("Habit name cannot be empty")

        if not habit_category or len(habit_category.strip()) == 0:
            raise ValueError("Habit category cannot be empty")

        logger.info(
            "Creating habit",
            request_id=request_id,
            habit_name=habit_name,
            category=habit_category,
        )

        habit_id = str(len(_HABITS) + 1)
        stored = _StoredHabit(
            id=habit_id,
            name=habit_name.strip(),
            description=habit_description.strip(),
            category=habit_category.strip(),
            created_date=datetime.now(timezone.utc),
        )
        _HABITS[habit_id] = stored

        habit = HabitResponse(
            id=stored.id,
            name=stored.name,
            description=stored.description,
            category=stored.category,
            created_date=stored.created_date,
            entries=[],
            summary=_compute_summary(stored),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=habit,
            message=f"Habit '{habit_name.strip()}' created successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid habit request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_HABIT",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Habit creation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "HABIT_ERROR",
                "message": "Failed to create habit",
            },
        )


@router.post("/log-entry", response_model=ApiResponse[HabitEntry])
async def log_habit_entry(
    request: Request,
    body: Optional[LogHabitEntryBody] = Body(default=None),
    # Back-compat (query params)
    habit_id: Optional[str] = None,
    completed: Optional[bool] = None,
    notes: Optional[str] = None,
) -> ApiResponse[HabitEntry]:
    """
    Log a habit completion entry.

    ## Parameters
    - **habit_id**: Habit identifier
    - **completed**: Whether habit was completed
    - **notes**: Optional notes about the entry

    ## Response
    Returns the logged entry with streak information.
    """
    request_id = request.state.request_id

    try:
        resolved_habit_id_raw = (body.habit_id if body else habit_id) or ""
        resolved_habit_id = str(resolved_habit_id_raw).strip()
        resolved_completed = body.completed if body else completed
        resolved_notes = body.note if body else notes

        if not resolved_habit_id:
            raise ValueError("habit_id is required")
        if resolved_completed is None:
            raise ValueError("completed is required")

        if resolved_habit_id not in _HABITS:
            raise ValueError("Unknown habit_id")

        logger.info(
            "Logging habit entry",
            request_id=request_id,
            habit_id=resolved_habit_id,
            completed=resolved_completed,
        )

        habit = _HABITS[resolved_habit_id]
        stored_entry = _StoredHabitEntry(
            id=f"entry_{uuid4().hex[:8]}",
            habit_id=resolved_habit_id,
            category=habit.category,
            date=datetime.now(timezone.utc),
            completed=bool(resolved_completed),
            notes=resolved_notes,
        )
        _ENTRIES.append(stored_entry)

        summary = _compute_summary(habit)

        entry = HabitEntry(
            id=stored_entry.id,
            habit_name=habit.name,
            category=habit.category,
            date=stored_entry.date,
            completed=stored_entry.completed,
            notes=stored_entry.notes,
            streak_days=summary.current_streak,
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=entry,
            message="Habit entry logged successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid habit log request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_HABIT_LOG",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Habit entry logging error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LOGGING_ERROR",
                "message": "Failed to log habit entry",
            },
        )


@router.get("/habit/{habit_id}", response_model=ApiResponse[HabitSummary])
async def get_habit_summary(
    request: Request,
    habit_id: str,
) -> ApiResponse[HabitSummary]:
    """
    Get summary statistics for a habit.

    ## Parameters
    - **habit_id**: Habit identifier

    ## Response
    Returns completion rate, streak info, and historical data.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Retrieving habit summary",
            request_id=request_id,
            habit_id=habit_id,
        )

        if habit_id not in _HABITS:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "HABIT_NOT_FOUND",
                    "message": "Habit not found",
                },
            )

        summary = _compute_summary(_HABITS[habit_id])

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=summary,
            message="Habit summary retrieved successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Habit summary error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "SUMMARY_ERROR",
                "message": "Failed to retrieve habit summary",
            },
        )


@router.get("/list", response_model=ApiResponse[List[HabitResponse]])
async def list_habits(request: Request) -> ApiResponse[List[HabitResponse]]:
    """List all habits for the current runtime.

    Note: Until auth/user persistence is added, this returns the in-memory list.
    """

    request_id = request.state.request_id

    habits: List[HabitResponse] = []
    for habit in _HABITS.values():
        habits.append(
            HabitResponse(
                id=habit.id,
                name=habit.name,
                description=habit.description,
                category=habit.category,
                created_date=habit.created_date,
                entries=[],
                summary=_compute_summary(habit),
            )
        )

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=habits,
        message="Habits retrieved successfully",
        request_id=request_id,
    )
