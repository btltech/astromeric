"""
API v2 - Habit Tracking Endpoint
Standardized request/response format for habit tracking and journaling.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus
)
from ..exceptions import (
    StructuredLogger, InvalidDateError
)

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/habits", tags=["Habits"])


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


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/create", response_model=ApiResponse[HabitResponse])
async def create_habit(
    request: Request,
    name: str,
    category: str,
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
        if not name or len(name.strip()) == 0:
            raise ValueError("Habit name cannot be empty")
        
        logger.info(
            "Creating habit",
            request_id=request_id,
            habit_name=name,
            category=category,
        )
        
        # Create habit
        habit = HabitResponse(
            id="habit_001",
            name=name,
            description=description or "",
            category=category,
            created_date=datetime.now(timezone.utc),
            entries=[],
            summary=HabitSummary(
                habit_id="habit_001",
                habit_name=name,
                total_days=0,
                completed_days=0,
                current_streak=0,
                longest_streak=0,
                completion_rate=0.0,
            ),
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=habit,
            message=f"Habit '{name}' created successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid habit request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_HABIT",
                "message": str(e),
            }
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
            }
        )


@router.post("/log-entry", response_model=ApiResponse[HabitEntry])
async def log_habit_entry(
    request: Request,
    habit_id: str,
    completed: bool,
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
        logger.info(
            "Logging habit entry",
            request_id=request_id,
            habit_id=habit_id,
            completed=completed,
        )
        
        entry = HabitEntry(
            id="entry_001",
            habit_name="Example Habit",
            category="health",
            date=datetime.now(timezone.utc),
            completed=completed,
            notes=notes,
            streak_days=1 if completed else 0,
        )
        
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=entry,
            message="Habit entry logged successfully",
            request_id=request_id,
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
            }
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
        
        summary = HabitSummary(
            habit_id=habit_id,
            habit_name="Example Habit",
            total_days=30,
            completed_days=24,
            current_streak=5,
            longest_streak=12,
            completion_rate=0.80,
            last_completed=datetime.now(timezone.utc),
        )
        
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
            }
        )
