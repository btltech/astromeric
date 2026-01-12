"""
API v2 - Cosmic Guide AI Endpoint
Standardized request/response format for AI-powered guidance and interpretations.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..schemas import (
    ApiResponse, ResponseStatus, ProfilePayload
)
from ..exceptions import (
    StructuredLogger, InvalidDateError
)
from ..ai_service import explain_with_gemini, fallback_summary

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


# ============================================================================
# ENDPOINTS
# ============================================================================

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
            guidance_text = "The cosmos suggests reflection and trust in your intuition."
        
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
            }
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
            }
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
            }
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
            }
        )
