import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..models import SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/alerts", tags=["Transit Alerts"])

# VAPID constants
VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY",
    "BCPloRz8zIkfeMDNuaqTN5bIreZsr6sYcKIBqbQV3X3TiHBpd3GvGRngnPgF4U4QUWBbQToMHYa9HoVJ8v_gGxo",
)
VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY", "YxDywGzrvW8Wra7lzPknQXfZhPd3vv2Cgzoe_I1S-q8"
)
VAPID_CLAIMS = {"sub": "mailto:alerts@astromeric.com"}


class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]


class NotificationPreferences(BaseModel):
    alert_mercury_retrograde: bool = True
    alert_frequency: str = "every_retrograde"  # "every_retrograde", "once_per_year", "weekly_digest", "none"


# In-memory storage for subscriptions (should be in DB in production)
subscriptions = {}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/vapid-key")
async def get_vapid_key():
    return {"public_key": VAPID_PUBLIC_KEY}


@router.post("/subscribe")
async def subscribe(sub: PushSubscription, request: Request):
    # Store subscription
    client_id = request.client.host
    subscriptions[client_id] = sub.model_dump()
    return {"status": "ok", "message": "Subscribed successfully"}


@router.get("/preferences")
async def get_preferences(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get notification preferences for authenticated user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "alert_mercury_retrograde": user.alert_mercury_retrograde,
        "alert_frequency": user.alert_frequency,
    }


@router.post("/preferences")
async def update_preferences(
    prefs: NotificationPreferences,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Update notification preferences for authenticated user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.alert_mercury_retrograde = prefs.alert_mercury_retrograde
    user.alert_frequency = prefs.alert_frequency
    db.commit()

    return {
        "status": "ok",
        "message": "Preferences updated",
        "alert_mercury_retrograde": user.alert_mercury_retrograde,
        "alert_frequency": user.alert_frequency,
    }


@router.post("/test-notify")
async def test_notify(request: Request):
    client_id = request.client.host
    if client_id not in subscriptions:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub_info = subscriptions[client_id]

    try:
        webpush(
            subscription_info=sub_info,
            data=json.dumps(
                {
                    "title": "Cosmic Alert 🌌",
                    "body": "Your test transit alert is working! Mercury is watching.",
                    "icon": "/icons/icon-192x192.png",
                    "url": "/",
                }
            ),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
        return {"status": "ok", "message": "Notification sent"}
    except WebPushException as ex:
        return {"status": "error", "message": str(ex)}


def should_send_alert(user: User, alert_type: str = "mercury_retrograde") -> bool:
    """
    Determine if alert should be sent based on user preferences and frequency.

    Returns True if alert should be sent, False otherwise.
    """
    if alert_type == "mercury_retrograde" and not user.alert_mercury_retrograde:
        return False

    frequency = user.alert_frequency

    if frequency == "none":
        return False
    elif frequency == "every_retrograde":
        # Always send
        return True
    elif frequency == "once_per_year":
        # Only send if last alert was > 365 days ago
        if user.last_retrograde_alert:
            days_since = (datetime.now(timezone.utc) - user.last_retrograde_alert).days
            return days_since > 365
        return True  # First time
    elif frequency == "weekly_digest":
        # Only send if last alert was > 7 days ago
        if user.last_retrograde_alert:
            days_since = (datetime.now(timezone.utc) - user.last_retrograde_alert).days
            return days_since > 7
        return True  # First time

    return False


def broadcast_transit_alert(
    title: str, body: str, db: Session, alert_type: str = "mercury_retrograde"
):
    """
    Utility to notify all subscribers about a major transit.
    Respects user notification preferences.
    """
    # Get all users with notifications enabled
    users_to_notify = []
    if alert_type == "mercury_retrograde":
        users_to_notify = (
            db.query(User).filter(User.alert_mercury_retrograde == True).all()
        )

    for user in users_to_notify:
        if not should_send_alert(user, alert_type):
            continue

        # Update last alert timestamp
        user.last_retrograde_alert = datetime.now(timezone.utc)

        # Send via browser push if subscribed
        for client_id, sub_info in subscriptions.items():
            try:
                webpush(
                    subscription_info=sub_info,
                    data=json.dumps(
                        {
                            "title": title,
                            "body": body,
                            "icon": "/icons/icon-192x192.png",
                            "url": "/tools",
                        }
                    ),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS,
                )
            except Exception:
                continue

    db.commit()
