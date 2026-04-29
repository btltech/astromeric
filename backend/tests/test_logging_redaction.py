import warnings

from starlette.testclient import TestClient

from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_daily_forecast_logs_do_not_include_profile_name(caplog):
    payload = {
        "profile": {
            "name": "Sensitive Forecast Name",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "latitude": 40.7128,
            "longitude": -74.006,
            "timezone": "America/New_York",
        },
        "scope": "daily",
        "include_details": True,
    }

    with caplog.at_level("INFO", logger="backend.app.routers.forecasts"):
        response = client.post("/v2/forecasts/daily", json=payload)

    assert response.status_code == 200
    assert "Sensitive Forecast Name" not in caplog.text
    assert "Calculating daily forecast" in caplog.text


def test_friendship_compatibility_logs_do_not_include_names(caplog):
    payload = {
        "person_a": {
            "name": "Sensitive Person A",
            "date_of_birth": "1992-05-15",
        },
        "person_b": {
            "name": "Sensitive Person B",
            "date_of_birth": "1990-08-20",
        },
    }

    with caplog.at_level("INFO", logger="backend.app.routers.compatibility"):
        response = client.post("/v2/compatibility/friendship", json=payload)

    assert response.status_code == 200
    assert "Sensitive Person A" not in caplog.text
    assert "Sensitive Person B" not in caplog.text
    assert "Calculating friendship compatibility" in caplog.text
