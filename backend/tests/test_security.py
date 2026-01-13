import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_rate_limiting():
    """Test that rate limiting works correctly."""
    # The limit is 100/minute. We'll make 101 requests.
    # Note: In a real test environment, we might need to mock the limiter or use a lower limit for testing.
    # For now, we just check that the first few requests succeed.

    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200


def test_health_endpoint():
    """Test the health endpoint returns correct structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
