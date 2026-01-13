"""
V1 API Router: Journal & Accountability
Provides journal entries, outcome tracking, accuracy stats, and accountability reports.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..engine.journal import (
    add_journal_entry,
    analyze_prediction_patterns,
    calculate_accuracy_stats,
    create_accountability_report,
    format_reading_for_journal,
    get_journal_prompts,
    get_reading_insights,
    record_outcome,
)
from ..models import Profile as DBProfile
from ..models import Reading as DBReading
from ..models import SessionLocal, User


# Request models
class JournalEntryRequest(BaseModel):
    """Request to add or update a journal entry for a reading."""

    reading_id: int
    entry: str = Field(..., min_length=1, max_length=5000)


class OutcomeRequest(BaseModel):
    """Request to record prediction outcome."""

    reading_id: int
    outcome: str = Field(..., pattern="^(yes|no|partial|neutral)$")
    notes: Optional[str] = None


class AccountabilityReportRequest(BaseModel):
    """Request for accountability report."""

    profile_id: int
    period: str = Field(default="month", pattern="^(week|month|year)$")


router = APIRouter()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/journal/entry", tags=["Journal"])
def add_journal_entry_endpoint(
    req: JournalEntryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add or update a journal entry for a reading.
    Requires authentication.
    """
    # Get the reading
    reading = db.query(DBReading).filter(DBReading.id == req.reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Verify user owns this reading via profile
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this reading"
        )

    # Update the journal entry
    reading.journal = req.entry
    db.commit()

    entry_data = add_journal_entry(req.reading_id, req.entry)

    return {"success": True, "message": "Journal entry saved", "entry": entry_data}


@router.post("/journal/outcome", tags=["Journal"])
def record_outcome_endpoint(
    req: OutcomeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record whether a prediction came true.
    Requires authentication.
    """
    # Get the reading
    reading = db.query(DBReading).filter(DBReading.id == req.reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Verify user owns this reading
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this reading"
        )

    # Update feedback
    reading.feedback = req.outcome
    db.commit()

    outcome_data = record_outcome(req.reading_id, req.outcome, notes=req.notes or "")

    return {"success": True, "message": "Outcome recorded", "outcome": outcome_data}


@router.get("/journal/readings/{profile_id}", tags=["Journal"])
def get_journal_readings(
    profile_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get readings for journaling view with feedback and journal status.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    # Get readings with pagination
    readings = (
        db.query(DBReading)
        .filter(DBReading.profile_id == profile_id)
        .order_by(DBReading.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = db.query(DBReading).filter(DBReading.profile_id == profile_id).count()

    return {
        "profile_id": profile_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "readings": [
            format_reading_for_journal(
                {
                    "id": r.id,
                    "scope": r.scope,
                    "date": r.date,
                    "content": r.content,
                    "feedback": r.feedback,
                    "journal": r.journal or "",
                }
            )
            for r in readings
        ],
    }


@router.get("/journal/reading/{reading_id}", tags=["Journal"])
def get_single_reading_journal(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single reading with full journal and content.
    Requires authentication.
    """
    reading = db.query(DBReading).filter(DBReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Verify user owns this reading
    profile = db.query(DBProfile).filter(DBProfile.id == reading.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this reading"
        )

    content = reading.content
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {"raw": content}

    return {
        "id": reading.id,
        "scope": reading.scope,
        "date": reading.date,
        "content": content,
        "feedback": reading.feedback,
        "journal": reading.journal or "",
        "created_at": reading.created_at.isoformat() if reading.created_at else None,
    }


@router.get("/journal/stats/{profile_id}", tags=["Journal"])
def get_journal_stats(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get accuracy statistics for a profile's readings.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    # Get all readings for stats
    readings = db.query(DBReading).filter(DBReading.profile_id == profile_id).all()

    readings_data = [
        {
            "id": r.id,
            "scope": r.scope,
            "date": r.date,
            "feedback": r.feedback,
            "journal": r.journal or "",
        }
        for r in readings
    ]

    stats = calculate_accuracy_stats(readings_data)
    insights = get_reading_insights(readings_data)

    return {"profile_id": profile_id, "stats": stats, "insights": insights}


@router.get("/journal/patterns/{profile_id}", tags=["Journal"])
def get_reading_patterns(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze prediction patterns over time.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    readings = db.query(DBReading).filter(DBReading.profile_id == profile_id).all()

    readings_data = [
        {"id": r.id, "scope": r.scope, "date": r.date, "feedback": r.feedback}
        for r in readings
    ]

    patterns = analyze_prediction_patterns(readings_data)

    return {"profile_id": profile_id, "patterns": patterns}


@router.post("/journal/report", tags=["Journal"])
def get_accountability_report(
    req: AccountabilityReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate comprehensive accountability report.
    Requires authentication.
    """
    # Verify profile belongs to user
    profile = db.query(DBProfile).filter(DBProfile.id == req.profile_id).first()
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    # Calculate date range based on period
    now = datetime.now(timezone.utc)
    if req.period == "week":
        start_date = now - timedelta(days=7)
    elif req.period == "month":
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)

    # Get readings in range
    readings = (
        db.query(DBReading)
        .filter(
            DBReading.profile_id == req.profile_id,
            DBReading.date >= start_date.isoformat(),
        )
        .all()
    )

    readings_data = [
        {
            "id": r.id,
            "scope": r.scope,
            "date": r.date,
            "feedback": r.feedback,
            "journal": r.journal or "",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in readings
    ]

    report = create_accountability_report(readings_data, req.period)

    return {"profile_id": req.profile_id, "report": report}


@router.get("/journal/prompts", tags=["Journal"])
def get_prompts(
    scope: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    themes: Optional[str] = Query(default=None, description="Comma-separated themes"),
):
    """
    Get journal prompts for reflection.
    No authentication required.
    """
    theme_list = themes.split(",") if themes else None
    prompts = get_journal_prompts(scope, theme_list)

    return {"scope": scope, "prompts": prompts}
