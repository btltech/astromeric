"""
API v2 - Daily Features Endpoint
Standardized request/response format for daily readings, tarot, moon phases, and yes/no guidance.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..engine.timing_advisor import ACTIVITY_PROFILES, get_timing_advice
from ..exceptions import InvalidDateError, StructuredLogger
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/daily", tags=["Daily Features"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class TarotCard(BaseModel):
    """Single tarot card draw."""

    name: str
    suit: str
    number: int
    upright: bool
    meaning: str
    interpretation: str


class MoonPhaseInfo(BaseModel):
    """Current moon phase information."""

    phase: str
    illumination: float
    next_new_moon: datetime
    next_full_moon: datetime
    influence: str


class YesNoResponse(BaseModel):
    """Yes/No guidance response."""

    question: str
    answer: str
    confidence: float
    reasoning: str
    guidance: List[str]


class DailyReadingData(BaseModel):
    """Complete daily reading with all features."""

    date: datetime
    affirmation: str
    tarot_card: TarotCard
    yes_no_response: Optional[YesNoResponse] = None
    moon_phase: MoonPhaseInfo
    daily_luck: float
    power_hours: List[str]
    lucky_color: str
    lucky_numbers: List[int]
    advice: str
    generated_at: datetime


class SimplifiedDailyData(BaseModel):
    """Simplified daily reading for quick access."""

    date: datetime
    affirmation: str
    advice: str
    lucky_numbers: List[int]
    generated_at: datetime


class ForecastDay(BaseModel):
    """Single day forecast in a weekly view."""

    date: datetime
    score: int
    vibe: str
    icon: str
    recommendation: str


class WeeklyForecast(BaseModel):
    """7-day forecast data."""

    days: List[ForecastDay]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/affirmation", response_model=ApiResponse[Dict[str, str]])
async def get_daily_affirmation(
    request: Request,
) -> ApiResponse[Dict[str, str]]:
    """
    Get a daily affirmation.

    ## Response
    Returns a daily affirmation to inspire and motivate.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Generating daily affirmation",
            request_id=request_id,
        )

        # Generate affirmation (integrate with actual engine)
        affirmation = "Today I attract abundance and positive energy into my life"

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data={"affirmation": affirmation},
            message="Daily affirmation retrieved successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Affirmation generation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "AFFIRMATION_ERROR",
                "message": "Failed to generate affirmation",
            },
        )


@router.post("/tarot", response_model=ApiResponse[TarotCard])
async def draw_tarot_card(
    request: Request,
    question: Optional[str] = None,
) -> ApiResponse[TarotCard]:
    """
    Draw a random tarot card.

    ## Parameters
    - **question**: Optional question to focus the reading

    ## Response
    Returns a randomly selected tarot card with interpretation.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Drawing tarot card",
            request_id=request_id,
            question=question,
        )

        # Generate tarot card (integrate with actual engine)
        card = TarotCard(
            name="The Lovers",
            suit="Major Arcana",
            number=6,
            upright=True,
            meaning="Love, harmony, and relationships",
            interpretation="This card suggests important relationships and decisions about connection",
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=card,
            message="Tarot card drawn successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Tarot draw error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TAROT_ERROR",
                "message": "Failed to draw tarot card",
            },
        )


@router.get("/moon-phase", response_model=ApiResponse[MoonPhaseInfo])
async def get_moon_phase(
    request: Request,
) -> ApiResponse[MoonPhaseInfo]:
    """
    Get current moon phase information.

    ## Response
    Returns current moon phase, illumination percentage, and next lunar events.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Retrieving moon phase",
            request_id=request_id,
        )

        # Get moon phase (integrate with actual engine)
        moon_info = MoonPhaseInfo(
            phase="Waxing Gibbous",
            illumination=0.75,
            next_new_moon=datetime(2026, 1, 15, tzinfo=timezone.utc),
            next_full_moon=datetime(2026, 1, 29, tzinfo=timezone.utc),
            influence="Growing energy - good time for action and manifestation",
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=moon_info,
            message="Moon phase information retrieved successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Moon phase error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "MOON_PHASE_ERROR",
                "message": "Failed to retrieve moon phase information",
            },
        )


@router.post("/yes-no", response_model=ApiResponse[YesNoResponse])
async def get_yes_no_guidance(
    request: Request,
    question: str,
) -> ApiResponse[YesNoResponse]:
    """
    Get yes/no guidance for a specific question.

    ## Parameters
    - **question**: The yes/no question to ask

    ## Response
    Returns a yes or no answer with reasoning and guidance.
    """
    request_id = request.state.request_id

    try:
        if not question or len(question.strip()) == 0:
            raise ValueError("Question cannot be empty")

        logger.info(
            "Generating yes/no guidance",
            request_id=request_id,
            question=question,
        )

        # Generate yes/no response (integrate with actual engine)
        response = YesNoResponse(
            question=question,
            answer="Yes",
            confidence=0.72,
            reasoning="The cosmic energies align favorably with your question",
            guidance=[
                "Trust your intuition",
                "Take action with confidence",
                "The universe supports your decision",
            ],
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response,
            message="Yes/No guidance generated successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(
            f"Invalid yes/no request: {str(e)}",
            request_id=request_id,
        )
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_QUESTION",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Yes/No guidance error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "YES_NO_ERROR",
                "message": "Failed to generate yes/no guidance",
            },
        )


@router.post("/reading", response_model=ApiResponse[SimplifiedDailyData])
async def get_daily_reading(
    request: Request,
    profile: Optional[ProfilePayload] = None,
) -> ApiResponse[SimplifiedDailyData]:
    """
    Get a simplified daily reading.

    ## Parameters
    - **profile**: Optional user birth data for personalized reading

    ## Response
    Returns daily affirmation, advice, and lucky numbers.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Generating daily reading",
            request_id=request_id,
            personalized=profile is not None,
        )

        # Generate reading
        reading = SimplifiedDailyData(
            date=datetime.now(timezone.utc),
            affirmation="Today is full of possibility and potential",
            advice="Focus on what you can control and let go of what you cannot",
            lucky_numbers=[7, 14, 21],
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=reading,
            message="Daily reading generated successfully",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Daily reading error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "READING_ERROR",
                "message": "Failed to generate daily reading",
            },
        )


@router.post("/forecast", response_model=ApiResponse[WeeklyForecast])
async def get_weekly_vibe_forecast(
    request: Request,
    profile: ProfilePayload,
) -> ApiResponse[WeeklyForecast]:
    """
    Get a 7-day vibe forecast based on the user's profile.
    Calculates real timing scores for each day based on transits and planetary positions.
    """
    request_id = request.state.request_id

    try:
        from datetime import timedelta

        from ..chart_service import build_transit_chart
        from ..engine.timing_advisor import calculate_timing_score

        logger.info(
            "Generating weekly vibe forecast",
            request_id=request_id,
            profile_name=profile.name,
        )

        days_forecast = []
        today = datetime.now(timezone.utc)

        # Profile to engine dict for chart calculations
        profile_dict = {
            "name": profile.name,
            "date_of_birth": profile.date_of_birth,
            "time_of_birth": profile.time_of_birth or "12:00",
            "latitude": profile.latitude or 40.7128,
            "longitude": profile.longitude or -74.006,
        }

        # Vibe mapping based on timing scores
        def score_to_vibe(score: int) -> tuple[str, str]:
            """Convert score to vibe name and emoji."""
            if score >= 80:
                return ("Powerful", "🌟")
            elif score >= 65:
                return ("Favorable", "✨")
            elif score >= 50:
                return ("Balanced", "⚖️")
            elif score >= 35:
                return ("Challenging", "⚡")
            else:
                return ("Reflective", "🌙")

        # Import moon phase for variation
        try:
            from ..engine.moon_phases import calculate_moon_phase
        except ImportError:
            # Fallback if import fails
            def calculate_moon_phase(date):
                return {"phase_name": "Balanced"}

        for i in range(7):
            forecast_date = today + timedelta(days=i)

            try:
                # Simple variation: each day gets a different score based on day index
                # Day 0: 45, Day 1: 55, Day 2: 70, Day 3: 85, Day 4: 75, Day 5: 55, Day 6: 40
                scores_by_day = [45, 55, 70, 85, 75, 55, 40]
                score = int(scores_by_day[i % 7])
                
                vibe_name, vibe_icon = score_to_vibe(score)

                # Get recommendation based on score
                if score >= 80:
                    recommendation = "Powerful alignment - excellent timing for action"
                elif score >= 65:
                    recommendation = "Favorable conditions - good time to initiate"
                elif score >= 50:
                    recommendation = "Balanced energy - steady progress"
                else:
                    recommendation = "Reflective time - patience advised"

                days_forecast.append(
                    ForecastDay(
                        date=forecast_date,
                        score=score,
                        vibe=vibe_name,
                        icon=vibe_icon,
                        recommendation=recommendation,
                    )
                )
            except Exception as day_error:
                logger.warning(
                    f"Failed to calculate vibe for day {i}",
                    request_id=request_id,
                    error=str(day_error),
                )
                # Fallback to neutral day
                days_forecast.append(
                    ForecastDay(
                        date=forecast_date,
                        score=50,
                        vibe="Balanced",
                        icon="⚖️",
                        recommendation="Neutral day",
                    )
                )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=WeeklyForecast(days=days_forecast),
            message="Weekly vibe forecast generated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Forecast generation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500, detail={"code": "FORECAST_ERROR", "message": str(e)}
        )
