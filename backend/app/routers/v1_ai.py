"""
V1 API Router: AI Insights
Provides AI-powered explanations for astrological readings.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..ai_service import explain_with_gemini, fallback_summary
from ..auth import get_current_user
from ..models import User


# Request/Response models
class AIExplainSection(BaseModel):
    title: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class AIExplainRequest(BaseModel):
    scope: str
    headline: Optional[str] = None
    theme: Optional[str] = None
    sections: list[AIExplainSection] = Field(default_factory=list)
    numerology_summary: Optional[str] = None


class AIExplainResponse(BaseModel):
    summary: str
    provider: str


router = APIRouter()


@router.post("/ai/explain", response_model=AIExplainResponse, tags=["AI"])
def explain_reading(
    payload: AIExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Explain reading with AI - requires paid subscription."""
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
    return {"summary": summary, "provider": provider}
