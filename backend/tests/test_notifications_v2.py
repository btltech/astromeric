import uuid

from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.models import DeviceToken, SessionLocal


def test_register_device_token_links_authenticated_user():
    client = TestClient(app)
    email = f"push-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    register = client.post(
        "/v2/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200
    token = register.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    device_token = f"android-token-{uuid.uuid4().hex}"

    response = client.post(
        "/v2/notifications/register",
        json={"token": device_token, "platform": "android"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["registered"] is True

    db = SessionLocal()
    try:
        stored = db.query(DeviceToken).filter(DeviceToken.token == device_token).first()
        assert stored is not None
        assert stored.platform == "android"
        assert stored.user_id == register.json()["data"]["user"]["id"]
    finally:
        db.close()


def test_unregister_device_token_removes_existing_token():
    client = TestClient(app)
    device_token = f"android-token-{uuid.uuid4().hex}"

    create = client.post(
        "/v2/notifications/register",
        json={"token": device_token, "platform": "android"},
    )
    assert create.status_code == 200

    remove = client.request(
        "DELETE",
        "/v2/notifications/register",
        json={"token": device_token, "platform": "android"},
    )

    assert remove.status_code == 200
    assert remove.json()["data"]["removed"] is True

    db = SessionLocal()
    try:
        stored = db.query(DeviceToken).filter(DeviceToken.token == device_token).first()
        assert stored is None
    finally:
        db.close()
