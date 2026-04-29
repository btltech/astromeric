import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from backend.app import auth as auth_module
from backend.app.firebase_push import PushDeliveryResult
from backend.app.main import app
from backend.app.models import Base, DeviceToken, User
from backend.app.routers import alerts
from backend.app.routers import auth as auth_router


@pytest.fixture(autouse=True)
def isolated_alerts_db(monkeypatch, tmp_path):
    db_path = tmp_path / "alerts.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(alerts, "SessionLocal", testing_session)
    monkeypatch.setattr(auth_module, "SessionLocal", testing_session)
    monkeypatch.setattr(auth_router, "SessionLocal", testing_session)

    yield testing_session

    engine.dispose()


def test_test_fcm_push_sends_to_current_user_tokens(monkeypatch, isolated_alerts_db):
    client = TestClient(app)
    email = f"push-self-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    register = client.post(
        "/v2/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200

    user_id = register.json()["data"]["user"]["id"]
    access_token = register.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    db = isolated_alerts_db()
    db.add(
        DeviceToken(
            token=f"self-token-{uuid.uuid4().hex}", platform="android", user_id=user_id
        )
    )
    db.commit()
    db.close()

    sent = {}

    def fake_send(tokens, title, body, data=None):
        sent["tokens"] = tokens
        sent["title"] = title
        sent["body"] = body
        sent["data"] = data
        return PushDeliveryResult(delivered_count=len(tokens), invalid_tokens=[])

    monkeypatch.setattr(alerts, "send_fcm_push_notification", fake_send)

    response = client.post(
        "/v2/alerts/test-fcm",
        json={"title": "Manual smoke", "body": "Testing shared backend push."},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["target_email"] == email
    assert body["requested_token_count"] == 1
    assert body["delivered_count"] == 1
    assert body["using_admin_override"] is False
    assert sent["data"]["alert_type"] == "test_push"
    assert sent["data"]["source"] == "manual_smoke"


def test_test_fcm_push_supports_admin_target_override(monkeypatch, isolated_alerts_db):
    client = TestClient(app)
    admin_email = f"push-admin-{uuid.uuid4().hex[:8]}@example.com"
    target_email = f"push-target-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    admin_register = client.post(
        "/v2/auth/register", json={"email": admin_email, "password": password}
    )
    target_register = client.post(
        "/v2/auth/register", json={"email": target_email, "password": password}
    )
    assert admin_register.status_code == 200
    assert target_register.status_code == 200

    target_user_id = target_register.json()["data"]["user"]["id"]
    admin_access_token = admin_register.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_access_token}"}

    db = isolated_alerts_db()
    target_token = f"target-token-{uuid.uuid4().hex}"
    db.add(DeviceToken(token=target_token, platform="android", user_id=target_user_id))
    db.commit()
    db.close()

    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    monkeypatch.setattr(
        alerts,
        "send_fcm_push_notification",
        lambda tokens, title, body, data=None: PushDeliveryResult(
            delivered_count=len(tokens),
            invalid_tokens=[],
        ),
    )

    response = client.post(
        "/v2/alerts/test-fcm",
        json={"target_email": target_email, "platform": "android"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["target_email"] == target_email
    assert body["requested_token_count"] == 1
    assert body["using_admin_override"] is True


def test_test_fcm_push_returns_not_found_when_user_has_no_tokens(isolated_alerts_db):
    client = TestClient(app)
    email = f"push-empty-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    register = client.post(
        "/v2/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200

    access_token = register.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/v2/alerts/test-fcm",
        json={"title": "Manual smoke", "body": "No tokens expected."},
        headers=headers,
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "No registered device tokens found for this account"
    )


def test_broadcast_transit_alert_sends_fcm_to_linked_device_tokens(
    monkeypatch, isolated_alerts_db
):
    db = isolated_alerts_db()
    user = User(
        id=str(uuid.uuid4()),
        email=f"push-alert-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="not-used",
        alert_mercury_retrograde=True,
        alert_frequency="every_retrograde",
    )
    db.add(user)
    db.commit()
    db.add_all(
        [
            DeviceToken(
                token=f"token-a-{uuid.uuid4().hex}", platform="android", user_id=user.id
            ),
            DeviceToken(
                token=f"token-b-{uuid.uuid4().hex}", platform="android", user_id=user.id
            ),
        ]
    )
    db.commit()

    sent = {}

    def fake_send(tokens, title, body, data=None):
        sent["tokens"] = tokens
        sent["title"] = title
        sent["body"] = body
        sent["data"] = data
        return PushDeliveryResult(delivered_count=len(tokens), invalid_tokens=[])

    monkeypatch.setattr(alerts, "send_fcm_push_notification", fake_send)

    try:
        alerts.broadcast_transit_alert(
            title="Mercury Retrograde begins! 🌀",
            body="Double-check communications.",
            db=db,
        )
        db.refresh(user)

        assert sent["tokens"]
        assert sent["title"] == "Mercury Retrograde begins! 🌀"
        assert sent["data"]["alert_type"] == "mercury_retrograde"
        assert user.last_retrograde_alert is not None
    finally:
        db.close()


def test_broadcast_transit_alert_prunes_invalid_fcm_tokens(
    monkeypatch, isolated_alerts_db
):
    db = isolated_alerts_db()
    user = User(
        id=str(uuid.uuid4()),
        email=f"push-prune-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="not-used",
        alert_mercury_retrograde=True,
        alert_frequency="every_retrograde",
    )
    db.add(user)
    db.commit()

    stale_token = f"stale-{uuid.uuid4().hex}"
    valid_token = f"valid-{uuid.uuid4().hex}"
    db.add_all(
        [
            DeviceToken(token=stale_token, platform="android", user_id=user.id),
            DeviceToken(token=valid_token, platform="android", user_id=user.id),
        ]
    )
    db.commit()

    monkeypatch.setattr(
        alerts,
        "send_fcm_push_notification",
        lambda tokens, title, body, data=None: PushDeliveryResult(
            delivered_count=1,
            invalid_tokens=[stale_token],
        ),
    )

    try:
        alerts.broadcast_transit_alert(
            title="Mercury direct! ✨",
            body="Clarity returns.",
            db=db,
        )

        assert (
            db.query(DeviceToken).filter(DeviceToken.token == stale_token).first()
            is None
        )
        assert (
            db.query(DeviceToken).filter(DeviceToken.token == valid_token).first()
            is not None
        )
    finally:
        db.close()


def test_broadcast_transit_alert_can_own_its_db_session(
    monkeypatch, isolated_alerts_db
):
    db = isolated_alerts_db()
    user = User(
        id=str(uuid.uuid4()),
        email=f"push-session-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="not-used",
        alert_mercury_retrograde=True,
        alert_frequency="every_retrograde",
    )
    token = DeviceToken(
        token=f"owned-session-{uuid.uuid4().hex}", platform="android", user_id=user.id
    )
    db.add(user)
    db.commit()
    db.add(token)
    db.commit()
    db.close()

    called = {"count": 0}

    def fake_send(tokens, title, body, data=None):
        called["count"] += 1
        return PushDeliveryResult(delivered_count=len(tokens), invalid_tokens=[])

    monkeypatch.setattr(alerts, "send_fcm_push_notification", fake_send)

    alerts.broadcast_transit_alert(
        title="Mercury Retrograde begins! 🌀",
        body="Double-check communications.",
    )

    assert called["count"] == 1
