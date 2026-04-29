"""Firebase Cloud Messaging helpers for backend push delivery."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


@dataclass
class PushDeliveryResult:
    delivered_count: int = 0
    invalid_tokens: List[str] = field(default_factory=list)
    configured: bool = True
    error: Optional[str] = None


def _load_firebase_modules():
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        return firebase_admin, credentials, messaging
    except Exception as exc:  # pragma: no cover - import path depends on env
        logger.warning("firebase-admin unavailable, skipping FCM push: %s", exc)
        return None, None, None


def _get_firebase_app(firebase_admin: Any, credentials: Any):
    if firebase_admin is None or credentials is None:
        return None, "firebase-admin unavailable"

    try:
        return firebase_admin.get_app(), None
    except ValueError:
        pass

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH") or os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    project_id = os.getenv("FIREBASE_PROJECT_ID")

    try:
        if service_account_json:
            credential = credentials.Certificate(json.loads(service_account_json))
        elif service_account_path and os.path.exists(service_account_path):
            credential = credentials.Certificate(service_account_path)
        else:
            credential = credentials.ApplicationDefault()

        options = {"projectId": project_id} if project_id else None
        return (
            firebase_admin.initialize_app(credential=credential, options=options),
            None,
        )
    except Exception as exc:  # pragma: no cover - env dependent
        logger.warning(
            "Failed to initialize Firebase Admin, skipping FCM push: %s", exc
        )
        return None, str(exc)


def send_fcm_push_notification(
    tokens: Sequence[str],
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
) -> PushDeliveryResult:
    """Send a notification to a set of FCM registration tokens."""
    unique_tokens = list(dict.fromkeys(token for token in tokens if token))
    if not unique_tokens:
        return PushDeliveryResult()

    firebase_admin, credentials, messaging = _load_firebase_modules()
    if firebase_admin is None or credentials is None or messaging is None:
        return PushDeliveryResult(
            configured=False,
            error="firebase-admin is not installed in the runtime environment",
        )

    app, config_error = _get_firebase_app(firebase_admin, credentials)
    if app is None:
        return PushDeliveryResult(configured=False, error=config_error)

    message = messaging.MulticastMessage(
        tokens=unique_tokens,
        notification=messaging.Notification(title=title, body=body),
        data={key: str(value) for key, value in (data or {}).items()},
    )

    try:
        response = messaging.send_each_for_multicast(message, app=app)
    except Exception as exc:  # pragma: no cover - network/credential dependent
        logger.warning("Failed to send FCM push notification batch: %s", exc)
        return PushDeliveryResult(error=str(exc))

    invalid_tokens: List[str] = []
    for token, send_response in zip(unique_tokens, response.responses):
        if send_response.success:
            continue

        exception = send_response.exception
        if _should_prune_token(exception):
            invalid_tokens.append(token)
        else:
            logger.warning("FCM push failed for token %s: %s", token, exception)

    return PushDeliveryResult(
        delivered_count=response.success_count,
        invalid_tokens=invalid_tokens,
    )


def _should_prune_token(exception: Exception | None) -> bool:
    if exception is None:
        return False

    error_code = getattr(exception, "code", None)
    if error_code in {"registration-token-not-registered", "unregistered"}:
        return True

    type_name = exception.__class__.__name__
    if type_name in {"UnregisteredError", "SenderIdMismatchError"}:
        return True

    message = str(exception).lower()
    return "not registered" in message or "senderid mismatch" in message
