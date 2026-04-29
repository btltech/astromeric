import warnings

from starlette.testclient import TestClient

from backend.app.main import app

# Suppress the deprecation warning - TestClient still works fine
warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_v2_numerology_profile_endpoint():
    payload = {
        "profile": {
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            # v2 accepts full profile payload but numerology requires only name + dob
            "time_of_birth": "12:00:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        "language": "en",
    }

    resp = client.post("/v2/numerology/profile", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"] is not None
    assert body["data"]["life_path"]["number"] in range(1, 34)


def test_v2_numerology_compatibility_endpoint():
    payload = {
        "profile": {
            "name": "Alice Example",
            "date_of_birth": "1992-05-15",
            "time_of_birth": "08:30:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        "person_b": {
            "name": "Bob Example",
            "date_of_birth": "1990-08-20",
            "time_of_birth": "11:00:00",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "timezone": "America/Los_Angeles",
        },
        "language": "en",
    }

    resp = client.post("/v2/numerology/compatibility", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"] is not None
    assert 0.0 <= body["data"]["compatibility_score"] <= 1.0
    assert "interpretation" in body["data"]
