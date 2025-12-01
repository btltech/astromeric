import warnings

from starlette.testclient import TestClient

from backend.app.main import app

# Suppress the deprecation warning - TestClient still works fine
# The new async pattern requires httpx.AsyncClient with ASGITransport
warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_daily_and_weekly_readings_and_health():
    # Build a simple profile payload
    profile_payload = {
        "profile": {
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            "time_of_birth": None,
            "location": None,
        }
    }

    # Daily reading
    resp = client.post("/daily-reading", json=profile_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "scope" in data or "summary" in data

    # Weekly reading
    resp = client.post("/weekly-reading", json=profile_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "scope" in data or "summary" in data

    # Health
    resp = client.get("/health")
    assert resp.status_code == 200
    h = resp.json()
    assert "status" in h and h["status"] in ("ok", True)


def test_natal_and_compatibility_endpoints():
    person_a = {
        "name": "Alice Example",
        "date_of_birth": "1992-05-15",
        "time_of_birth": None,
        "location": None,
    }
    person_b = {
        "name": "Bob Example",
        "date_of_birth": "1990-08-20",
        "time_of_birth": None,
        "location": None,
    }

    # Natal profile
    resp = client.post("/natal-profile", json={"profile": person_a})
    assert resp.status_code == 200
    data = resp.json()
    assert "chart" in data or "natal" in data

    # Compatibility
    resp = client.post(
        "/compatibility", json={"person_a": person_a, "person_b": person_b}
    )
    assert resp.status_code == 200
    comp = resp.json()
    assert isinstance(comp, dict)
    assert any(
        k in comp
        for k in ("topic_scores", "highlights", "compatibility", "astro", "numerology")
    )
