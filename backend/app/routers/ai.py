"""
API v2 - AI Endpoints
AI-powered reading explanations and insights.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..ai_service import explain_with_gemini, fallback_summary
from ..auth import get_current_user
from ..models import User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/ai", tags=["AI"])


class AIExplainSection(BaseModel):
    """Section data for AI explanation."""
    title: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)


class AIExplainRequest(BaseModel):
    """Request for AI explanation of a reading."""
    scope: str
    headline: Optional[str] = None
    theme: Optional[str] = None
    sections: List[AIExplainSection] = Field(default_factory=list)
    numerology_summary: Optional[str] = None


class AIExplainResponse(BaseModel):
    """AI explanation response."""
    summary: str
    provider: str


@router.post("/explain", response_model=ApiResponse[AIExplainResponse])
async def explain_reading(
    request: Request,
    payload: AIExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get AI-powered explanation of a reading.
    
    ## Authentication
    Requires valid JWT token and premium subscription.
    
    ## Features
    - Gemini Flash-powered natural language explanations
    - Personalized insights based on reading data
    - Fallback to rule-based summary if AI unavailable
    
    ## Response
    Returns friendly explanation with practical tips.
    """
    if not current_user.is_paid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI insights require a premium subscription. Upgrade to unlock this feature.",
        )

    sections = [section.model_dump() for section in payload.sections]
    summary = explain_with_gemini(
        payload.scope,
        payload.headline,
        payload.theme,
        sections,
        payload.numerology_summary,
    )
    provider = "gemini-flash"
    
    if not summary:
        provider = "fallback"
        summary = fallback_summary(
            payload.headline, sections, payload.numerology_summary
        )
    
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=AIExplainResponse(summary=summary, provider=provider)
    )
