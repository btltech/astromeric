import warnings

from starlette.testclient import TestClient

from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_v2_charts_natal_allows_missing_birth_time_defaults_to_noon():
    payload = {
        "profile": {
            "name": "Test User",
            "date_of_birth": "1990-06-15",
            "time_of_birth": None,
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
            "house_system": "Placidus",
        },
        "lang": "en",
    }

    resp = client.post("/v2/charts/natal", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "success"
    data = body["data"]
    assert isinstance(data["planets"], list)
    assert data["metadata"]["birth_time_assumed"] is True
    assert data["metadata"]["assumed_time_of_birth"] == "12:00"


def test_v2_charts_natal_accepts_fixed_offset_timezones():
    payload = {
        "profile": {
            "name": "Offset TZ",
            "date_of_birth": "1990-06-15",
            "time_of_birth": "12:00",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "GMT+0100",
            "house_system": "Placidus",
        },
        "lang": "en",
    }

    resp = client.post("/v2/charts/natal", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
