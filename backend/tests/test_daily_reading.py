from fastapi.testclient import TestClient


def test_v2_daily_reading_returns_lucky_color():
    from app.main import api

    client = TestClient(api)
    body = {
        "name": "Test",
        "date_of_birth": "1990-06-15",
        "time_of_birth": "12:00:00",
        "place_of_birth": "New York, NY, USA",
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": "America/New_York",
        "house_system": "Placidus",
    }

    resp = client.post("/v2/daily/reading", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert isinstance(data["data"]["lucky_color"], (str, type(None)))
