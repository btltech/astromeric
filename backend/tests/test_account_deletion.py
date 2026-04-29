import uuid

from starlette.testclient import TestClient

from backend.app.main import app


def test_delete_account_removes_user_and_blocks_token():
    client = TestClient(app)

    email = f"delete-test-{uuid.uuid4().hex[:10]}@example.com"
    password = "Password123"

    register = client.post(
        "/v2/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200
    token = register.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_profile = client.post(
        "/v2/profiles/",
        json={
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        headers=headers,
    )
    assert create_profile.status_code == 200

    delete_resp = client.delete("/v2/auth/account", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "success"

    # Token should no longer be valid because the user no longer exists.
    me = client.get("/v2/auth/me", headers=headers)
    assert me.status_code == 401
