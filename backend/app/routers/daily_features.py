"""
API v2 - Daily Features Endpoint
Standardized request/response format for daily readings, tarot, moon phases, and yes/no guidance.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

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
    lucky_color: Optional[str] = None
    power_hours: List[str] = []
    daily_luck: Optional[float] = None
    generated_at: datetime


class ForecastDay(BaseModel):
    """Single day forecast in a weekly view."""

    date: str
    score: int
    vibe: str
    icon: str
    recommendation: str


class WeeklyForecast(BaseModel):
    """7-day forecast data."""

    days: List[ForecastDay]


class DoDontResponse(BaseModel):
    """Daily Do's and Don'ts."""

    dos: List[str]
    donts: List[str]
    personal_day: int
    moon_phase: str
    mercury_retrograde: bool = False
    venus_retrograde: bool = False


class BriefBullet(BaseModel):
    emoji: str
    text: str


class MorningBriefResponse(BaseModel):
    """3-bullet morning summary for widgets and push."""

    date: datetime
    greeting: str
    bullets: List[BriefBullet]
    moon_phase: str
    personal_day: int
    vibe: str


def _profile_timezone_name(profile: Optional[ProfilePayload]) -> str:
    tz_name = profile.timezone if profile and profile.timezone else "UTC"
    return tz_name or "UTC"


def _profile_zone(profile: Optional[ProfilePayload]) -> ZoneInfo:
    try:
        return ZoneInfo(_profile_timezone_name(profile))
    except Exception:
        return ZoneInfo("UTC")


def _resolve_profile_now(
    profile: Optional[ProfilePayload],
    *,
    now_utc: Optional[datetime] = None,
) -> tuple[datetime, datetime]:
    current_utc = (
        now_utc.astimezone(timezone.utc) if now_utc else datetime.now(timezone.utc)
    )
    return current_utc, current_utc.astimezone(_profile_zone(profile))


def _profile_day_start(reference_date, profile: Optional[ProfilePayload]) -> datetime:
    return datetime.combine(
        reference_date, datetime.min.time(), tzinfo=_profile_zone(profile)
    )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/do-dont", response_model=ApiResponse[DoDontResponse])
async def get_daily_do_dont(
    request: Request,
    profile: ProfilePayload,
) -> ApiResponse[DoDontResponse]:
    """
    Get personalized daily Do's and Don'ts.

    Returns 3 things to embrace and 3 things to avoid today,
    computed from current transit aspects, personal day numerology,
    moon phase, and retrograde status.
    """
    request_id = request.state.request_id
    try:
        from ..chart_service import build_natal_chart, build_transit_chart
        from ..engine.astrology import get_zodiac_sign
        from ..engine.do_dont import build_do_dont
        from ..engine.moon_phases import calculate_moon_phase, estimate_moon_sign
        from ..engine.numerology import calculate_life_path_number
        from ..engine.numerology_extended import (
            calculate_personal_day,
            calculate_personal_month,
            calculate_personal_year,
        )

        now_utc, local_now = _resolve_profile_now(profile)
        dob = profile.date_of_birth

        # Build charts for transit analysis
        profile_dict = {
            "name": profile.name,
            "date_of_birth": dob,
            "time_of_birth": profile.time_of_birth or "12:00",
            "latitude": profile.latitude or 40.7128,
            "longitude": profile.longitude or -74.006,
            "timezone": profile.timezone or "UTC",
        }

        natal_chart, transit_chart = None, None
        try:
            natal_chart = build_natal_chart(profile_dict)
            transit_chart = build_transit_chart(profile_dict, now_utc)
        except Exception as chart_err:
            logger.warning(
                f"Chart build failed, using text-only do/dont: {chart_err}",
                request_id=request_id,
            )

        # Moon phase
        moon_res = calculate_moon_phase(now_utc)
        moon_phase = moon_res.get("phase_name", "Waxing Crescent")

        # Personal day
        py = calculate_personal_year(dob, local_now.year)
        pm = calculate_personal_month(py, local_now.month)
        pd = calculate_personal_day(pm, local_now.day)

        # Retrograde checks
        mercury_rx = False
        venus_rx = False
        try:
            import swisseph as swe

            jd = swe.julday(
                now_utc.year,
                now_utc.month,
                now_utc.day,
                now_utc.hour + now_utc.minute / 60.0,
            )
            merc_res, _ = swe.calc_ut(jd, swe.MERCURY, 2)
            mercury_rx = merc_res[3] < 0
            venus_res, _ = swe.calc_ut(jd, swe.VENUS, 2)
            venus_rx = venus_res[3] < 0
        except Exception:
            pass

        result = build_do_dont(
            natal_chart=natal_chart,
            transit_chart=transit_chart,
            personal_day=pd,
            moon_phase=moon_phase,
            is_mercury_retrograde=mercury_rx,
            is_venus_retrograde=venus_rx,
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=DoDontResponse(**result),
            message="Daily guidance generated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Do/Dont error: {e}", request_id=request_id, error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500, detail={"code": "DO_DONT_ERROR", "message": str(e)}
        )


@router.post("/brief", response_model=ApiResponse[MorningBriefResponse])
async def get_morning_brief(
    request: Request,
    profile: ProfilePayload,
) -> ApiResponse[MorningBriefResponse]:
    """
    Get a 3-bullet morning brief — ideal for widgets and push notifications.

    Returns a moon phase bullet, a personal-day numerology bullet,
    and an overall energy vibe bullet.
    """
    request_id = request.state.request_id
    try:
        from ..engine.astrology import get_zodiac_sign
        from ..engine.moon_phases import calculate_moon_phase, estimate_moon_sign
        from ..engine.numerology import calculate_life_path_number
        from ..engine.numerology_extended import (
            calculate_personal_day,
            calculate_personal_month,
            calculate_personal_year,
        )

        now_utc, local_now = _resolve_profile_now(profile)
        dob = profile.date_of_birth

        # Moon
        moon_res = calculate_moon_phase(now_utc)
        moon_phase = moon_res.get("phase_name", "Waxing Crescent")
        moon_sign = estimate_moon_sign(now_utc)
        moon_illumination = int(moon_res.get("illumination", 50))

        # Personal day
        py = calculate_personal_year(dob, local_now.year)
        pm = calculate_personal_month(py, local_now.month)
        pd = calculate_personal_day(pm, local_now.day)

        _pd_energy = {
            1: "leadership energy",
            2: "cooperative energy",
            3: "creative energy",
            4: "grounding energy",
            5: "adventurous energy",
            6: "nurturing energy",
            7: "spiritual energy",
            8: "ambitious energy",
            9: "completion energy",
        }
        personal_energy = _pd_energy.get(pd, "balanced energy")

        # Overall vibe from lucky numbers seed
        import hashlib

        seed_val = int.from_bytes(
            hashlib.sha256(f"{dob}-{local_now.date().isoformat()}".encode()).digest()[
                :4
            ],
            "big",
        )
        vibe_options = [
            "Powerful 🌟",
            "Favorable ✨",
            "Balanced ⚖️",
            "Reflective 🌙",
            "Charged ⚡",
        ]
        vibe = vibe_options[seed_val % len(vibe_options)]

        # Hour-based greeting
        hour = local_now.hour
        if hour < 12:
            greeting_prefix = "Good morning"
        elif hour < 17:
            greeting_prefix = "Good afternoon"
        else:
            greeting_prefix = "Good evening"
        greeting = f"{greeting_prefix}, {profile.name.split()[0]} ✨"

        bullets = [
            BriefBullet(
                emoji="🌙",
                text=f"Moon is {moon_phase} in {moon_sign} ({moon_illumination}% illuminated)",
            ),
            BriefBullet(
                emoji="🔢",
                text=f"Personal Day {pd} — this is a day of {personal_energy}",
            ),
            BriefBullet(
                emoji="⚡",
                text=f"Today's vibe: {vibe}",
            ),
        ]

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=MorningBriefResponse(
                date=now_utc,
                greeting=greeting,
                bullets=bullets,
                moon_phase=moon_phase,
                personal_day=pd,
                vibe=vibe,
            ),
            message="Morning brief generated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Morning brief error: {e}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500, detail={"code": "BRIEF_ERROR", "message": str(e)}
        )


@router.post("/affirmation", response_model=ApiResponse[Dict[str, str]])
async def get_daily_affirmation(
    request: Request,
    profile: Optional[ProfilePayload] = None,
) -> ApiResponse[Dict[str, str]]:
    """
    Get a personalized daily affirmation.

    ## Parameters
    - **profile**: Optional user birth data. When provided, the affirmation is
      tailored to the user's zodiac element and life path number.

    ## Response
    Returns a personalized daily affirmation.
    """
    request_id = request.state.request_id

    try:
        from ..engine.astrology import get_element, get_zodiac_sign
        from ..engine.daily_features import get_daily_affirmation
        from ..engine.numerology import calculate_life_path_number

        # Derive element and life path from profile when available
        if profile and profile.date_of_birth:
            sign = get_zodiac_sign(profile.date_of_birth)
            element = get_element(sign)
            life_path = calculate_life_path_number(profile.date_of_birth)
        else:
            element = "Fire"
            life_path = 1

        res = get_daily_affirmation(
            element=element,
            life_path=life_path,
            reference_date=datetime.now(timezone.utc).date(),
        )
        affirmation = res["text"]

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
        from ..engine.daily_features import get_tarot_card

        raw_card = get_tarot_card(question=question)

        card = TarotCard(
            name=raw_card["card"],
            suit="Major Arcana",  # All major for now
            number=raw_card["card_number"],
            upright=not raw_card["reversed"],
            meaning=", ".join(raw_card["keywords"]),
            interpretation=raw_card["message"],
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
        from ..engine.moon_phases import calculate_moon_phase

        # Calculate for now
        now = datetime.now(timezone.utc)
        res = calculate_moon_phase(now)

        moon_info = MoonPhaseInfo(
            phase=res["phase_name"],
            illumination=res["illumination"],
            next_new_moon=res.get("next_new_moon", now),
            next_full_moon=res.get("next_full_moon", now),
            influence=res.get("influence", "Growing energy"),
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
        from ..engine.daily_features import get_yes_no_reading

        res = get_yes_no_reading(question=question)

        response = YesNoResponse(
            question=question,
            answer=res["answer"],
            confidence=float(res["confidence"]) / 100.0,
            reasoning=res["reasoning"],
            guidance=[res["message"], res["timing"]],
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
        from ..engine.astrology import get_element, get_zodiac_sign
        from ..engine.daily_features import get_all_daily_features
        from ..engine.numerology import calculate_life_path_number
        from ..engine.numerology_extended import (
            calculate_personal_day,
            calculate_personal_month,
            calculate_personal_year,
        )
        from ..engine.planetary_timing import get_power_hours

        # Profile extraction
        name = profile.name if profile else "Guest"
        dob = profile.date_of_birth if profile else "1990-01-01"

        # Use date if provided in payload
        reference_date = _resolve_profile_now(profile)[1].date()
        if profile and profile.date:
            try:
                reference_date = datetime.strptime(profile.date, "%Y-%m-%d").date()
            except ValueError:
                pass  # Fallback to today on error

        # Derive element and numerology cycles from actual DOB
        sign = get_zodiac_sign(dob)
        element = get_element(sign)
        life_path = calculate_life_path_number(dob)
        personal_year = calculate_personal_year(dob, reference_date.year)
        personal_month_num = calculate_personal_month(
            personal_year, reference_date.month
        )
        personal_day = calculate_personal_day(personal_month_num, reference_date.day)

        res = get_all_daily_features(
            name=name,
            dob=dob,
            element=element,
            life_path=life_path,
            personal_day=personal_day,
            reference_date=reference_date,
            personal_year=personal_year,
        )

        # Power hours (fallback to defaults if no location)
        latitude = profile.latitude if profile else 0.0
        longitude = profile.longitude if profile else 0.0
        tz = profile.timezone if profile and profile.timezone else "UTC"
        power_hours_raw = get_power_hours(
            _profile_day_start(reference_date, profile),
            latitude=latitude,
            longitude=longitude,
            timezone=tz,
        )
        power_hours = [f"{h['start']} - {h['end']}" for h in power_hours_raw]

        mood_score = res.get("mood_forecast", {})
        # Use the real weighted luck_score (0–100); fall back to legacy score×10 if missing
        daily_luck = mood_score.get("luck_score") or (
            (mood_score.get("score") * 10.0)
            if isinstance(mood_score.get("score"), (int, float))
            else None
        )

        lucky_colors = res.get("lucky_colors")
        lucky_color = None
        if isinstance(lucky_colors, dict):
            lucky_color = lucky_colors.get("primary") or lucky_colors.get("accent")
        elif isinstance(lucky_colors, list) and lucky_colors:
            first = lucky_colors[0]
            if isinstance(first, dict):
                lucky_color = first.get("name") or first.get("primary")
            elif isinstance(first, str):
                lucky_color = first

        reading = SimplifiedDailyData(
            date=_profile_day_start(reference_date, profile).astimezone(timezone.utc),
            affirmation=res["affirmation"]["text"],
            advice=res["mood_forecast"]["description"],
            lucky_numbers=res["lucky_numbers"],
            lucky_color=lucky_color,
            power_hours=power_hours,
            daily_luck=daily_luck,
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

        from ..engine.astrology import get_element, get_zodiac_sign
        from ..engine.numerology import calculate_life_path_number
        from ..engine.numerology_extended import (
            calculate_personal_day,
            calculate_personal_month,
            calculate_personal_year,
        )
        from ..products.forecast import build_forecast

        logger.info(
            "Generating weekly vibe forecast",
            request_id=request_id,
        )

        # Build full profile dict for chart engine
        profile_dict = {
            "name": profile.name,
            "date_of_birth": profile.date_of_birth,
            "time_of_birth": profile.time_of_birth or "12:00",
            "latitude": profile.latitude or 40.7128,
            "longitude": profile.longitude or -74.006,
            "timezone": profile.timezone or "UTC",
            "house_system": profile.house_system or "Placidus",
        }

        # Vibe label mapping
        def score_to_vibe(score: float) -> tuple[str, str]:
            if score >= 8.0:
                return ("Powerful", "🌟")
            elif score >= 6.5:
                return ("Favorable", "✨")
            elif score >= 5.0:
                return ("Balanced", "⚖️")
            elif score >= 3.5:
                return ("Challenging", "⚡")
            else:
                return ("Reflective", "🌙")

        recommendations = {
            "Powerful": "Excellent alignment—take decisive action today.",
            "Favorable": "Positive energy supports your goals. Move forward.",
            "Balanced": "Steady energy. Good for routine and focus.",
            "Challenging": "Tension in the stars. Practice patience.",
            "Reflective": "Conserve energy. Best for inner work.",
        }

        _, today_local = _resolve_profile_now(profile)
        days_forecast = []

        for i in range(7):
            forecast_day = today_local.date() + timedelta(days=i)
            date_str = forecast_day.isoformat()

            try:
                # Real forecast using transit aspects + numerology cycles
                result = build_forecast(
                    profile=profile_dict,
                    scope="daily",
                    target_date=date_str,
                )
                # overall_score is already on a 3.0–9.5 scale
                raw_score = result.get("overall_score", 5.0)
                # Convert to 0-100 for consistency with ForecastDay model
                score = int(round(raw_score * 10))
            except Exception as day_error:
                logger.warning(
                    f"build_forecast failed for day {i}, using numerology fallback: {day_error}",
                    request_id=request_id,
                )
                # Fallback: deterministic score from personal-day numerology (always unique per user+date)
                try:
                    py = calculate_personal_year(
                        profile.date_of_birth, forecast_day.year
                    )
                    pm = calculate_personal_month(py, forecast_day.month)
                    pd = calculate_personal_day(pm, forecast_day.day)
                    # Personal day 1,3,5,9 = higher energy; 4,7 = lower — map to 35-85 range
                    pd_boost = {
                        1: 30,
                        2: 5,
                        3: 25,
                        4: -10,
                        5: 20,
                        6: 10,
                        7: -5,
                        8: 15,
                        9: 25,
                    }.get(pd, 0)
                    score = max(35, min(85, 55 + pd_boost))
                except Exception:
                    score = 50

            vibe_name, vibe_icon = score_to_vibe(score / 10.0)
            recommendation = recommendations.get(vibe_name, "Neutral day.")

            days_forecast.append(
                ForecastDay(
                    date=date_str,
                    score=score,
                    vibe=vibe_name,
                    icon=vibe_icon,
                    recommendation=recommendation,
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


# =============================================================================
# NEW v2 GUIDANCE ENDPOINTS — Astrology-informed symbolic guidance
# =============================================================================


# ── Response models ──────────────────────────────────────────────────────────


class ReasonFactor(BaseModel):
    type: str
    value: object


class GuidanceFeature(BaseModel):
    """Standard output contract for all five guidance features."""

    headline: str
    selection: object
    why_it_matches: str
    how_to_use: str
    basis: str
    trust_level: str
    reason_factors: List[ReasonFactor]


class BirthstoneStone(BaseModel):
    name: str
    emoji: Optional[str] = None
    why_chosen: str
    when_to_use: str
    basis: str


class BirthstoneGuidance(GuidanceFeature):
    trust_note: Optional[str] = None


class TarotGuidance(GuidanceFeature):
    keywords: Optional[List[str]] = None
    message: Optional[str] = None
    honesty_note: Optional[str] = None
    reflect_on: Optional[str] = None
    avoid: Optional[str] = None
    transit_theme: Optional[str] = None


class AllGuidanceResponse(BaseModel):
    """All five astrology-informed guidance features."""

    date: str
    lucky_number: object
    lucky_color: object
    affirmation: object
    tarot: object
    birthstone: object
    context_summary: object


@router.post("/guidance", response_model=ApiResponse[AllGuidanceResponse])
async def get_all_guidance(
    request: Request,
    profile: ProfilePayload,
) -> ApiResponse[AllGuidanceResponse]:
    """
    Get all five astrology-informed symbolic guidance features in one call.

    Returns Lucky Number, Lucky Color, Affirmation, Tarot, and Birthstone —
    all derived from a single shared AstroContext for consistency.

    ## Features
    - **Lucky Number**: 3-tier numerology (core, support, resonance) with explanation
    - **Lucky Color**: Day ruler × element × Moon sign palette with why-today text
    - **Affirmation**: Structured template from element + Moon mood + personal day
    - **Tarot**: Deterministic card draw + astro-informed interpretation layer
    - **Birthstone**: Chart-informed ranking (ruler → natal Moon → element → life path)

    ## Trust Rules
    - `birth_time_trusted = false` disables Ascendant/chart-ruler logic
    - `location_trusted = false` disables local-sky timing claims
    """
    request_id = request.state.request_id
    try:
        from datetime import date as date_t

        from ..engine.astro_context import build_astro_context
        from ..engine.daily_features import get_all_guidance as _all_guidance

        # Resolve reference date (use profile.date if provided, else today in profile tz)
        _, local_now = _resolve_profile_now(profile)
        reference_date: date_t = local_now.date()
        if profile.date:
            try:
                reference_date = date_t.fromisoformat(profile.date)
            except ValueError:
                pass

        # Build shared context — single source of truth
        context = build_astro_context(profile, reference_date)

        # Generate all five features
        guidance = _all_guidance(context)

        # Build a summary of context inputs visible to the client
        context_summary = {
            "reference_date": str(reference_date),
            "natal_sun": context["natal_sun"],
            "dominant_element": context["dominant_element"],
            "moon_sign": context["moon_sign"],
            "moon_sign_basis": context["moon_sign_basis"],
            "moon_phase": context["moon_phase"],
            "day_ruler": context["day_ruler"],
            "personal_day": context["personal_day"],
            "personal_month": context["personal_month"],
            "personal_year": context["personal_year"],
            "life_path": context["life_path"],
            "birth_time_trusted": context["birth_time_trusted"],
            "location_trusted": context["location_trusted"],
            "usable_inputs": context["usable_inputs"],
        }

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=AllGuidanceResponse(
                date=str(reference_date),
                lucky_number=guidance["lucky_number"],
                lucky_color=guidance["lucky_color"],
                affirmation=guidance["affirmation"],
                tarot=guidance["tarot"],
                birthstone=guidance["birthstone"],
                context_summary=context_summary,
            ),
            message="Astrology-informed guidance generated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Guidance generation error: {e}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "GUIDANCE_ERROR", "message": str(e)},
        )


@router.post("/birthstone", response_model=ApiResponse[object])
async def get_birthstone(
    request: Request,
    profile: ProfilePayload,
) -> ApiResponse[object]:
    """
    Get chart-informed birthstone guidance.

    Returns primary stone (stable, chart-based) and support stone (today's emphasis).

    ## Priority
    1. Chart ruler (requires trusted birth time)
    2. Natal Moon sign
    3. Dominant element
    4. Life path number
    """
    request_id = request.state.request_id
    try:
        from datetime import date as date_t

        from ..engine.astro_context import build_astro_context
        from ..engine.daily_features import get_birthstone_guidance

        _, local_now = _resolve_profile_now(profile)
        reference_date = local_now.date()
        if profile.date:
            try:
                reference_date = date_t.fromisoformat(profile.date)
            except ValueError:
                pass

        context = build_astro_context(profile, reference_date)
        result = get_birthstone_guidance(context)

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=result,
            message="Birthstone guidance generated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            f"Birthstone error: {e}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "BIRTHSTONE_ERROR", "message": str(e)},
        )
