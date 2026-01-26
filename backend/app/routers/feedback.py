"""
API v2 - Feedback Endpoints
Section feedback and rating endpoints.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..models import Profile as DBProfile
from ..models import SectionFeedback, SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/feedback", tags=["Feedback"])


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SectionFeedbackRequest(BaseModel):
    """Request for section feedback."""
    scope: str
    section: str
    vote: str = Field(..., pattern=r"^(up|down)$")
    profile_id: Optional[int] = None


@router.post("/section", response_model=ApiResponse[Dict[str, Any]])
async def submit_section_feedback(
    request: Request,
    req: SectionFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Submit thumbs up/down feedback for a reading section.
    
    ## Authentication
    Required when feedback is tied to a saved profile.
    
    ## Vote Values
    - **up**: Positive feedback
    - **down**: Negative feedback
    """
    profile_id: Optional[int] = None
    
    if req.profile_id is not None:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        profile = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to rate this profile")
        
        profile_id = profile.id

    feedback_row = SectionFeedback(
        profile_id=profile_id,
        scope=req.scope,
        section=req.section,
        vote=req.vote,
    )
    db.add(feedback_row)
    db.commit()

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"status": "ok", "message": "Feedback recorded"}
    )
