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


def test_v2_daily_reading_includes_the_full_features_the_website_card_reads():
    from app.main import api

    client = TestClient(api)
    resp = client.post(
        "/v2/daily/reading",
        json={"name": "Guest", "date_of_birth": "1992-04-12", "sun_sign": "Aries"},
    )
    assert resp.status_code == 200
    features = resp.json()["data"]["features"]
    assert features["affirmation"]["text"]
    assert (
        features["lucky_colors"]["primary"] and features["lucky_colors"]["primary_hex"]
    )
    assert features["lucky_planet"]["planet"]
    assert {"mood", "emoji", "description", "peak_hours"} <= set(
        features["mood_forecast"]
    )
    assert isinstance(features["life_path"], int)
    assert isinstance(features["personal_day"], int)
    assert isinstance(features["retrograde_alerts"], list)


def test_peak_hours_never_start_at_midnight():
    from datetime import date

    from app.engine.daily_features import _calculate_mood_forecast

    for personal_day in range(1, 10):
        hours = _calculate_mood_forecast("Fire", 1, personal_day, date(2026, 9, 29))[
            "peak_hours"
        ]
        assert not hours.startswith("12am"), (personal_day, hours)


def test_weekly_forecast_days_carry_the_day_detail():
    from app.main import api

    client = TestClient(api)
    resp = client.post(
        "/v2/daily/forecast", json={"name": "Guest", "date_of_birth": "1992-04-12"}
    )
    assert resp.status_code == 200
    days = resp.json()["data"]["days"]
    assert len(days) == 7
    for day in days:
        assert day["recommendation"]
        assert day["overview"] and not day["overview"].startswith("Cosmic weather")
        assert 0 < len(day["embrace"]) <= 3
        assert 0 < len(day["avoid"]) <= 3
