import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from ..auth import get_current_user, get_current_user_optional
from ..firebase_push import send_fcm_push_notification
from ..models import DeviceToken, SessionLocal, User
from ..schemas import ApiResponse, ResponseStatus

router = APIRouter(prefix="/v2/alerts", tags=["Transit Alerts"])
logger = logging.getLogger(__name__)

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


class TestPushRequest(BaseModel):
    title: str = "Astromeric test push"
    body: str = "Backend push delivery is configured for this account."
    target_email: Optional[str] = None
    platform: Optional[str] = None
    data: Dict[str, str] = Field(default_factory=dict)


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


@router.post("/test-fcm", response_model=ApiResponse[Dict[str, Any]])
async def test_fcm_push(
    body: TestPushRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send an authenticated FCM smoke-test push to the current user's device tokens."""

    target_user = current_user
    using_admin_override = False

    if body.target_email and body.target_email.lower() != current_user.email.lower():
        admin_emails = {
            email.strip().lower()
            for email in os.getenv("ADMIN_EMAILS", "").split(",")
            if email.strip()
        }
        if current_user.email.lower() not in admin_emails:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to send a test push to another account",
            )

        target_user = db.query(User).filter(User.email == body.target_email).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        using_admin_override = True

    token_query = db.query(DeviceToken).filter(DeviceToken.user_id == target_user.id)
    if body.platform:
        token_query = token_query.filter(DeviceToken.platform == body.platform)

    device_tokens = [token.token for token in token_query.all()]
    if not device_tokens:
        raise HTTPException(
            status_code=404,
            detail="No registered device tokens found for this account",
        )

    payload_data = {
        "url": "/tools",
        "alert_type": "test_push",
        "source": "manual_smoke",
    }
    payload_data.update(body.data)

    delivery = send_fcm_push_notification(
        tokens=device_tokens,
        title=body.title,
        body=body.body,
        data=payload_data,
    )

    if not delivery.configured:
        raise HTTPException(
            status_code=503,
            detail=delivery.error or "Firebase Admin push is not configured",
        )

    if delivery.invalid_tokens:
        (
            db.query(DeviceToken)
            .filter(DeviceToken.token.in_(delivery.invalid_tokens))
            .delete(synchronize_session=False)
        )
        db.commit()

    response_data = {
        "target_email": target_user.email,
        "requested_token_count": len(device_tokens),
        "delivered_count": delivery.delivered_count,
        "invalid_tokens": delivery.invalid_tokens,
        "platform": body.platform,
        "using_admin_override": using_admin_override,
    }
    if delivery.error:
        response_data["delivery_error"] = delivery.error

    return ApiResponse(status=ResponseStatus.SUCCESS, data=response_data)


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
    title: str,
    body: str,
    db: Optional[Session] = None,
    alert_type: str = "mercury_retrograde",
):
    """
    Utility to notify all subscribers about a major transit.
    Respects user notification preferences.
    """
    owns_session = db is None
    if db is None:
        db = SessionLocal()

    # Get all users with notifications enabled
    users_to_notify = []
    if alert_type == "mercury_retrograde":
        users_to_notify = db.query(User).filter(User.alert_mercury_retrograde).all()

    try:
        eligible_users = [
            user for user in users_to_notify if should_send_alert(user, alert_type)
        ]

        for user in eligible_users:
            user.last_retrograde_alert = datetime.now(timezone.utc)

            device_tokens = [
                token.token
                for token in db.query(DeviceToken)
                .filter(DeviceToken.user_id == user.id)
                .all()
            ]
            delivery = send_fcm_push_notification(
                tokens=device_tokens,
                title=title,
                body=body,
                data={
                    "url": "/tools",
                    "alert_type": alert_type,
                },
            )
            if delivery.invalid_tokens:
                (
                    db.query(DeviceToken)
                    .filter(DeviceToken.token.in_(delivery.invalid_tokens))
                    .delete(synchronize_session=False)
                )

        # Browser push subscriptions are not account-linked, so deliver once
        # when at least one eligible account would receive the alert.
        if eligible_users:
            for sub_info in subscriptions.values():
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
                except Exception as exc:
                    logger.warning("Browser webpush delivery failed: %s", exc)

        db.commit()
    finally:
        if owns_session:
            db.close()
