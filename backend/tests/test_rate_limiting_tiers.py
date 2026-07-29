import os

import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.middleware.rate_limit import (
    gemini_daily_limiter,
    general_daily_limiter,
    login_limiter,
)


@pytest.fixture(autouse=True)
def setup_rate_limiting_test():
    # Enable rate limiting for this test suite
    os.environ["TEST_RATE_LIMITING"] = "1"

    # Reset limiter states
    gemini_daily_limiter.requests.clear()
    general_daily_limiter.requests.clear()
    login_limiter.tokens.clear()
    login_limiter.last_update.clear()

    yield

    # Clean up environment variable
    if "TEST_RATE_LIMITING" in os.environ:
        del os.environ["TEST_RATE_LIMITING"]


client = TestClient(app)


def test_gemini_api_daily_rate_limiting():
    # Gemini allows 1 request then blocks the 2nd
    response1 = client.post("/v2/ai/explain", json={})
    assert response1.status_code != 429

    response2 = client.post("/v2/ai/explain", json={})
    assert response2.status_code == 429
    data = response2.json()
    assert "Gemini AI" in data["detail"]
    assert "reset_time" in data
    assert "retry_after" in data


def test_general_services_daily_rate_limiting():
    # General services allow 3 requests then block the 4th
    for _ in range(3):
        response = client.post("/v2/natal", json={})
        assert response.status_code != 429

    response4 = client.post("/v2/natal", json={})
    assert response4.status_code == 429
    data = response4.json()
    assert "Core Services" in data["detail"]
    assert "reset_time" in data
    assert "retry_after" in data


def test_auth_endpoints_do_not_consume_general_quota():
    # Auth endpoints do not consume the general 3/day quota
    # Hit auth endpoints multiple times
    for _ in range(4):
        response = client.post("/v2/auth/login", json={})
        # Should not get 429 (since login limit is 5)
        assert response.status_code != 429

    # The general 3/day quota should still be completely free
    for _ in range(3):
        response = client.post("/v2/natal", json={})
        assert response.status_code != 429


def test_bypass_routes_are_never_blocked():
    # Bypass routes (/, /health, /docs, /openapi.json) are never blocked
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200

    for _ in range(10):
        response = client.get("/docs")
        assert response.status_code == 200


def test_unknown_api_routes_fall_under_general_limit():
    # Unknown API routes also fall under the 3/day general limit
    for _ in range(3):
        response = client.get("/v2/nonexistent-route-random-xyz")
        assert response.status_code == 404

    response4 = client.get("/v2/nonexistent-route-random-xyz")
    assert response4.status_code == 429
    assert "Core Services" in response4.json()["detail"]


def test_ios_requests_bypass_daily_limits():
    # iOS requests bypass the 1/day Gemini limit and 3/day service limit
    headers = {"X-Client-Platform": "ios"}

    # 1. Gemini AI endpoint (allows more than 1)
    for _ in range(5):
        response = client.post("/v2/ai/explain", json={}, headers=headers)
        assert response.status_code != 429

    # 2. General core services (allows more than 3)
    for _ in range(5):
        response = client.post("/v2/natal", json={}, headers=headers)
        assert response.status_code != 429
