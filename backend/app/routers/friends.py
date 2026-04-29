"""
friends.py — Social Friend Chart Comparison
--------------------------------------------
Allows users to store, retrieve, and compare friend profiles.
Friend profiles are stored per owner ID and support
chart comparison (compatibility + natal side-by-side).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..exceptions import StructuredLogger
from ..models import Friend, SessionLocal
from ..products.compatibility import build_compatibility
from ..schemas import ApiResponse, ProfilePayload, ResponseStatus

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/friends", tags=["Friends"])


# Legacy JSON store used by older Railway deployments. Keep a read-only import
# path so previously stored data can be pulled into the database on demand.
_STORE_PATH = Path(os.getenv("FRIENDS_STORE_PATH", "/tmp/friends_store.json"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FriendProfile(BaseModel):
    id: str  # Client-generated UUID
    name: str
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: Optional[str] = "12:00"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = "UTC"
    avatar_emoji: Optional[str] = "👤"
    relationship_type: str = "friendship"  # friendship | romantic | professional
    notes: Optional[str] = None
    added_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AddFriendRequest(BaseModel):
    owner_id: str
    friend: FriendProfile


class CompareRequest(BaseModel):
    owner_profile: ProfilePayload
    friend_id: str
    owner_id: str
    relationship_type: str = "friendship"


class CompareAllRequest(BaseModel):
    owner_id: str
    owner_profile: ProfilePayload


class FriendCompatibilitySummary(BaseModel):
    friend_name: str
    friend_id: str
    overall_score: float
    headline: str
    emoji: str
    relationship_type: str
    dimensions: List[Dict[str, Any]]
    strengths: List[str]
    recommendations: List[str]


def _score_to_emoji(score: float) -> str:
    if score >= 85:
        return "🔥"
    if score >= 70:
        return "✨"
    if score >= 55:
        return "💛"
    if score >= 40:
        return "🌱"
    return "💙"


def _score_to_headline(score: float, name: str, rel_type: str) -> str:
    label = {
        "romantic": "romantic connection",
        "professional": "professional synergy",
    }.get(rel_type, "friendship")
    if score >= 85:
        return f"Exceptional {label} with {name}"
    if score >= 70:
        return f"Strong {label} with {name}"
    if score >= 55:
        return f"Good {label} with {name} — worth nurturing"
    if score >= 40:
        return f"Moderate {label} — growth through differences"
    return f"Challenging but growth-rich connection with {name}"


def _load_legacy_store() -> dict:
    try:
        if _STORE_PATH.exists():
            return json.loads(_STORE_PATH.read_text())
    except Exception:
        pass
    return {}


def _parse_added_at(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _serialize_added_at(value: Optional[datetime]) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _friend_row_to_profile(friend: Friend) -> FriendProfile:
    return FriendProfile(
        id=friend.friend_id,
        name=friend.name,
        date_of_birth=friend.date_of_birth,
        time_of_birth=friend.time_of_birth,
        latitude=friend.latitude,
        longitude=friend.longitude,
        timezone=friend.timezone,
        avatar_emoji=friend.avatar_emoji,
        relationship_type=friend.relationship_type,
        notes=friend.notes,
        added_at=_serialize_added_at(friend.added_at),
    )


def _friend_profile_to_row(owner_id: str, friend: FriendProfile) -> Friend:
    return Friend(
        owner_id=owner_id,
        friend_id=friend.id,
        name=friend.name,
        date_of_birth=friend.date_of_birth,
        time_of_birth=friend.time_of_birth,
        latitude=friend.latitude,
        longitude=friend.longitude,
        timezone=friend.timezone,
        avatar_emoji=friend.avatar_emoji,
        relationship_type=friend.relationship_type,
        notes=friend.notes,
        added_at=_parse_added_at(friend.added_at),
    )


def _migrate_legacy_friends(db: Session, owner_id: str) -> None:
    legacy_store = _load_legacy_store()
    legacy_friends = legacy_store.get(owner_id, [])
    if not legacy_friends:
        return

    existing_ids = {
        row[0]
        for row in db.query(Friend.friend_id).filter(Friend.owner_id == owner_id).all()
    }
    migrated = 0

    for raw_friend in legacy_friends:
        try:
            friend = FriendProfile(**raw_friend)
        except Exception:
            continue

        if friend.id in existing_ids:
            continue

        db.add(_friend_profile_to_row(owner_id, friend))
        existing_ids.add(friend.id)
        migrated += 1

    if not migrated:
        return

    try:
        db.commit()
        logger.info("Migrated legacy friends store", migrated_count=migrated)
    except IntegrityError:
        db.rollback()


def _owner_friends_query(db: Session, owner_id: str):
    return (
        db.query(Friend)
        .filter(Friend.owner_id == owner_id)
        .order_by(Friend.added_at.asc(), Friend.id.asc())
    )


def _get_owner_friends(db: Session, owner_id: str) -> List[Friend]:
    _migrate_legacy_friends(db, owner_id)
    return _owner_friends_query(db, owner_id).all()


def _get_friend(db: Session, owner_id: str, friend_id: str) -> Optional[Friend]:
    _migrate_legacy_friends(db, owner_id)
    return (
        db.query(Friend)
        .filter(Friend.owner_id == owner_id, Friend.friend_id == friend_id)
        .first()
    )


@router.post("/add", response_model=ApiResponse[FriendProfile])
async def add_friend(
    request: Request,
    body: AddFriendRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[FriendProfile]:
    request_id = request.state.request_id
    try:
        _migrate_legacy_friends(db, body.owner_id)

        if _get_friend(db, body.owner_id, body.friend.id):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "FRIEND_EXISTS",
                    "message": "Friend already added",
                },
            )

        friend_row = _friend_profile_to_row(body.owner_id, body.friend)
        db.add(friend_row)
        db.commit()
        db.refresh(friend_row)

        logger.info(
            "Friend added",
            request_id=request_id,
            owner_id=body.owner_id,
            friend_id=friend_row.friend_id,
        )
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=_friend_row_to_profile(friend_row),
            message="Friend added",
            request_id=request_id,
        )
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "FRIEND_EXISTS",
                "message": "Friend already added",
            },
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "add_friend error",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "FRIEND_ADD_ERROR", "message": str(e)},
        )


@router.get("/list/{owner_id}", response_model=ApiResponse[List[FriendProfile]])
async def list_friends(
    request: Request,
    owner_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[List[FriendProfile]]:
    request_id = request.state.request_id
    friends = _get_owner_friends(db, owner_id)
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data=[_friend_row_to_profile(friend) for friend in friends],
        message=f"{len(friends)} friends",
        request_id=request_id,
    )


@router.delete("/remove/{owner_id}/{friend_id}", response_model=ApiResponse[Dict])
async def remove_friend(
    request: Request,
    owner_id: str,
    friend_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[Dict]:
    request_id = request.state.request_id
    friend = _get_friend(db, owner_id, friend_id)
    if friend is None:
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data={"removed": 0},
            message="Friend not found",
            request_id=request_id,
        )

    db.delete(friend)
    db.commit()
    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"removed": 1},
        message="Friend removed",
        request_id=request_id,
    )


@router.post("/compare", response_model=ApiResponse[FriendCompatibilitySummary])
async def compare_with_friend(
    request: Request,
    body: CompareRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[FriendCompatibilitySummary]:
    request_id = request.state.request_id
    try:
        friend = _get_friend(db, body.owner_id, body.friend_id)
        if not friend:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "FRIEND_NOT_FOUND",
                    "message": "Friend not found",
                },
            )

        person_a = {
            "name": body.owner_profile.name,
            "date_of_birth": body.owner_profile.date_of_birth,
        }
        person_b = {
            "name": friend.name,
            "date_of_birth": friend.date_of_birth,
        }

        compat = build_compatibility(
            person_a,
            person_b,
            relationship_type=body.relationship_type,
        )
        score = float(compat.get("overall_score", 70))

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=FriendCompatibilitySummary(
                friend_name=friend.name,
                friend_id=friend.friend_id,
                overall_score=score,
                headline=_score_to_headline(score, friend.name, body.relationship_type),
                emoji=_score_to_emoji(score),
                relationship_type=body.relationship_type,
                dimensions=compat.get("dimensions", []),
                strengths=compat.get("strengths", [])[:3],
                recommendations=compat.get("recommendations", [])[:3],
            ),
            message="Compatibility calculated",
            request_id=request_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "compare_with_friend error",
            request_id=request_id,
            friend_id=body.friend_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "COMPARE_ERROR", "message": str(e)},
        )


@router.post(
    "/compare-all", response_model=ApiResponse[List[FriendCompatibilitySummary]]
)
async def compare_all_friends(
    request: Request,
    body: CompareAllRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[List[FriendCompatibilitySummary]]:
    request_id = request.state.request_id
    try:
        friends = _get_owner_friends(db, body.owner_id)
        if not friends:
            return ApiResponse(
                status=ResponseStatus.SUCCESS,
                data=[],
                message="No friends yet",
                request_id=request_id,
            )

        person_a = {
            "name": body.owner_profile.name,
            "date_of_birth": body.owner_profile.date_of_birth,
        }
        results: List[FriendCompatibilitySummary] = []

        for friend in friends:
            try:
                person_b = {
                    "name": friend.name,
                    "date_of_birth": friend.date_of_birth,
                }
                compat = build_compatibility(
                    person_a,
                    person_b,
                    relationship_type=friend.relationship_type,
                )
                score = float(compat.get("overall_score", 70))
                results.append(
                    FriendCompatibilitySummary(
                        friend_name=friend.name,
                        friend_id=friend.friend_id,
                        overall_score=score,
                        headline=_score_to_headline(
                            score,
                            friend.name,
                            friend.relationship_type,
                        ),
                        emoji=_score_to_emoji(score),
                        relationship_type=friend.relationship_type,
                        dimensions=compat.get("dimensions", []),
                        strengths=compat.get("strengths", [])[:3],
                        recommendations=compat.get("recommendations", [])[:2],
                    )
                )
            except Exception as inner_err:
                logger.warning(
                    "Skipping friend during compare_all",
                    request_id=request_id,
                    friend_id=friend.friend_id,
                    error_type=type(inner_err).__name__,
                )

        results.sort(key=lambda row: row.overall_score, reverse=True)

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=results,
            message=f"{len(results)} compatibilities calculated",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(
            "compare_all error",
            request_id=request_id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "COMPARE_ALL_ERROR", "message": str(e)},
        )
