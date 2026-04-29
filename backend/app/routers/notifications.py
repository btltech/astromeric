"""
API v2 - Notifications
Register device tokens for push notifications.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..models import DeviceToken, SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/notifications", tags=["Notifications"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeviceTokenRequest(BaseModel):
    token: str
    platform: str = "ios"


@router.post("/register", response_model=ApiResponse[dict])
async def register_device_token(
    request: Request,
    body: DeviceTokenRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    existing = db.query(DeviceToken).filter(DeviceToken.token == body.token).first()
    if existing:
        existing.platform = body.platform
        existing.user_id = current_user.id if current_user else existing.user_id
        db.commit()
        return ApiResponse(status=ResponseStatus.SUCCESS, data={"registered": True})

    token = DeviceToken(
        token=body.token,
        platform=body.platform,
        user_id=current_user.id if current_user else None,
    )
    db.add(token)
    db.commit()

    return ApiResponse(status=ResponseStatus.SUCCESS, data={"registered": True})


@router.delete("/register", response_model=ApiResponse[Dict[str, Any]])
async def unregister_device_token(
    request: Request,
    body: DeviceTokenRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    existing = db.query(DeviceToken).filter(DeviceToken.token == body.token).first()
    if existing:
        if current_user and existing.user_id and existing.user_id != current_user.id:
            return ApiResponse(status=ResponseStatus.SUCCESS, data={"removed": False})
        db.delete(existing)
        db.commit()
        return ApiResponse(status=ResponseStatus.SUCCESS, data={"removed": True})

    return ApiResponse(status=ResponseStatus.SUCCESS, data={"removed": False})
