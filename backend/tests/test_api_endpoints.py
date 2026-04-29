import warnings
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.routers import daily_features as daily_router

# Suppress the deprecation warning - TestClient still works fine
# The new async pattern requires httpx.AsyncClient with ASGITransport
warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_daily_and_weekly_forecasts_and_health():
    # Build a simple profile payload for v2 API
    forecast_payload = {
        "profile": {
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        "scope": "daily",
        "include_details": True,
    }

    # Daily forecast (v2)
    resp = client.post("/v2/forecasts/daily", json=forecast_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["scope"] == "daily"

    # Weekly forecast (v2)
    forecast_payload["scope"] = "weekly"
    resp = client.post("/v2/forecasts/weekly", json=forecast_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["scope"] == "weekly"

    # Health
    resp = client.get("/health")
    assert resp.status_code == 200
    h = resp.json()
    assert "status" in h and h["status"] in ("ok", True)


def test_weekly_vibe_forecast_endpoint():
    payload = {
        "name": "Test User",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.006,
    }

    resp = client.post("/v2/daily/forecast", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "success"
    assert body["data"] is not None
    assert "days" in body["data"]
    assert len(body["data"]["days"]) == 7

    scores = [day["score"] for day in body["data"]["days"]]

    # Regression guard: previously every day could fall back to the neutral path.
    assert any(score != 50 for score in scores)
    assert all(len(day["date"]) == 10 for day in body["data"]["days"])
    assert all("T" not in day["date"] for day in body["data"]["days"])


def test_daily_reading_uses_profile_timezone_for_default_date(monkeypatch):
    fixed_utc = datetime(2026, 4, 8, 3, 30, tzinfo=timezone.utc)
    pacific = ZoneInfo("America/Los_Angeles")

    monkeypatch.setattr(
        daily_router,
        "_resolve_profile_now",
        lambda profile, now_utc=None: (fixed_utc, fixed_utc.astimezone(pacific)),
    )

    payload = {
        "name": "Time Zone Test",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "12:00:00",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles",
    }

    resp = client.post("/v2/daily/reading", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["date"].startswith("2026-04-07")


def test_morning_brief_uses_profile_local_hour_for_greeting(monkeypatch):
    fixed_utc = datetime(2026, 4, 8, 3, 30, tzinfo=timezone.utc)
    pacific = ZoneInfo("America/Los_Angeles")

    monkeypatch.setattr(
        daily_router,
        "_resolve_profile_now",
        lambda profile, now_utc=None: (fixed_utc, fixed_utc.astimezone(pacific)),
    )

    payload = {
        "name": "Evening User",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "12:00:00",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles",
    }

    resp = client.post("/v2/daily/brief", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["greeting"].startswith("Good evening")


def test_daily_forecast_tone_changes_narrative_style():
    payload = {
        "profile": {
            "name": "Tone Test",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        "scope": "daily",
        "include_details": True,
        "tone": "very_practical",
    }

    practical = client.post("/v2/forecasts/daily", json=payload)
    assert practical.status_code == 200
    practical_summary = practical.json()["data"]["sections"][0]["summary"]

    payload["tone"] = "very_mystical"
    mystical = client.post("/v2/forecasts/daily", json=payload)
    assert mystical.status_code == 200
    mystical_summary = mystical.json()["data"]["sections"][0]["summary"]

    assert practical_summary.startswith("Bottom line:")
    assert mystical_summary.startswith("The stars gather around this theme:")
    assert practical_summary != mystical_summary


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
