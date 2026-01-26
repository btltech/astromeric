"""
API v2 - Cosmic Guide AI Endpoint
Standardized request/response format for AI-powered guidance and interpretations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..engine.cosmic_guide import ask_cosmic_guide
from ..exceptions import InvalidDateError, StructuredLogger
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/cosmic-guide", tags=["Cosmic Guide"])


# ============================================================================
# STANDARDIZED RESPONSE MODELS FOR v2
# ============================================================================


class GuidanceResponse(BaseModel):
    """AI-generated guidance response."""

    question: str
    guidance: str
    interpretation: str
    recommendations: List[str]
    affirmation: str
    generated_at: datetime


class InterpretationData(BaseModel):
    """Detailed astrological interpretation."""

    topic: str
    summary: str
    detailed_interpretation: str
    planetary_influences: Dict[str, str]
    timing_insights: str
    practical_advice: List[str]
    generated_at: datetime


class ChatRequest(BaseModel):
    """Chat request with cosmic guide."""

    message: str
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    rising_sign: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response from cosmic guide."""

    response: str
    provider: str
    model: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/chat")
async def chat_with_cosmic_guide(
    request: Request,
    req: ChatRequest,
):
    """
    Chat with the cosmic guide AI assistant.

    ## Parameters
    - **message**: The user's message/question
    - **sun_sign**: Optional sun sign for personalization
    - **moon_sign**: Optional moon sign for personalization
    - **rising_sign**: Optional rising sign for personalization
    - **history**: Optional conversation history

    ## Response
    Returns AI-generated response with cosmic wisdom.
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        if not req.message or len(req.message.strip()) == 0:
            raise ValueError("Message cannot be empty")

        logger.info(
            "Cosmic guide chat request",
            request_id=request_id,
            message_length=len(req.message),
            has_signs=bool(req.sun_sign or req.moon_sign or req.rising_sign),
        )

        # Build chart data for personalization
        chart_data = None
        if req.sun_sign or req.moon_sign or req.rising_sign:
            planets = []
            if req.sun_sign:
                planets.append({"name": "Sun", "sign": req.sun_sign})
            if req.moon_sign:
                planets.append({"name": "Moon", "sign": req.moon_sign})

            chart_data = {"planets": planets}
            if req.rising_sign:
                chart_data["houses"] = [{"house": 1, "sign": req.rising_sign}]

        # Use the proper cosmic guide engine
        result = await ask_cosmic_guide(
            question=req.message,
            chart_data=chart_data,
            conversation_history=req.history,
        )

        response_text = result.get(
            "response",
            "The cosmic energies are aligning to bring you clarity. Trust in the journey and remain open to the wisdom that unfolds.",
        )
        provider = result.get("provider", "gemini")

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=ChatResponse(
                response=response_text, provider=provider, model=result.get("model")
            ),
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid chat request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_MESSAGE",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Chat error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "CHAT_ERROR",
                "message": "Failed to generate cosmic guidance",
            },
        )


@router.post("/guidance", response_model=ApiResponse[GuidanceResponse])
async def get_cosmic_guidance(
    request: Request,
    question: str,
    profile: Optional[ProfilePayload] = None,
) -> ApiResponse[GuidanceResponse]:
    """
    Get AI-powered cosmic guidance for a specific question.

    ## Parameters
    - **question**: The question to ask the cosmic guide
    - **profile**: Optional birth profile for personalized guidance

    ## Response
    Returns AI-generated guidance with interpretation and recommendations.
    """
    request_id = request.state.request_id

    try:
        if not question or len(question.strip()) == 0:
            raise ValueError("Question cannot be empty")

        logger.info(
            "Generating cosmic guidance",
            request_id=request_id,
            question=question[:100],
            personalized=profile is not None,
        )

        # Generate guidance using AI
        guidance_text = await explain_with_gemini(question)
        if not guidance_text or guidance_text == fallback_summary:
            guidance_text = (
                "The cosmos suggests reflection and trust in your intuition."
            )

        response_data = GuidanceResponse(
            question=question,
            guidance=guidance_text,
            interpretation="Your question resonates with current cosmic energies",
            recommendations=[
                "Trust your inner wisdom",
                "Take action aligned with your values",
                "Remain open to unexpected opportunities",
            ],
            affirmation="I am guided by the universe's infinite wisdom",
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Cosmic guidance generated successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid guidance request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_QUESTION",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Guidance generation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "GUIDANCE_ERROR",
                "message": "Failed to generate cosmic guidance",
            },
        )


@router.post("/interpret", response_model=ApiResponse[InterpretationData])
async def get_detailed_interpretation(
    request: Request,
    topic: str,
    context: Optional[str] = None,
) -> ApiResponse[InterpretationData]:
    """
    Get detailed AI interpretation of an astrological topic.

    ## Parameters
    - **topic**: The astrological topic to interpret
    - **context**: Optional context for personalized interpretation

    ## Response
    Returns detailed interpretation with planetary influences and practical advice.
    """
    request_id = request.state.request_id

    try:
        if not topic or len(topic.strip()) == 0:
            raise ValueError("Topic cannot be empty")

        logger.info(
            "Generating interpretation",
            request_id=request_id,
            topic=topic[:100],
        )

        # Generate interpretation using AI
        query = f"Provide detailed interpretation of: {topic}"
        if context:
            query += f" Context: {context}"

        interpretation_text = await explain_with_gemini(query)
        if not interpretation_text:
            interpretation_text = fallback_summary

        response_data = InterpretationData(
            topic=topic,
            summary=interpretation_text[:200],
            detailed_interpretation=interpretation_text,
            planetary_influences={
                "Sun": "Core identity and life direction",
                "Moon": "Emotional nature and inner needs",
                "Mercury": "Communication and thinking patterns",
            },
            timing_insights="This influence is currently strong and will peak next month",
            practical_advice=[
                "Align your actions with astrological timing",
                "Leverage planetary transits for best outcomes",
                "Journal your observations and synchronicities",
            ],
            generated_at=datetime.now(timezone.utc),
        )

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=response_data,
            message="Interpretation generated successfully",
            request_id=request_id,
        )
    except ValueError as e:
        logger.error(f"Invalid interpretation request: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_TOPIC",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(
            f"Interpretation error: {str(e)}",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERPRETATION_ERROR",
                "message": "Failed to generate interpretation",
            },
        )
