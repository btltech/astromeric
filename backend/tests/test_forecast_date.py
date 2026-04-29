import pytest


@pytest.mark.parametrize(
    "timezone_name, expected_offset_suffix",
    [
        ("UTC", "+00:00"),
        ("America/New_York", None),  # DST varies; just assert it is not UTC.
    ],
)
def test_build_forecast_honors_target_date(timezone_name, expected_offset_suffix):
    from app.products.forecast import build_forecast

    profile = {
        "name": "Test",
        "date_of_birth": "1990-06-15",
        "time_of_birth": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": timezone_name,
    }

    result = build_forecast(profile, scope="daily", target_date="2000-01-01")

    assert result["date"] == "2000-01-01"

    transit_dt = (
        result.get("charts", {})
        .get("transit", {})
        .get("metadata", {})
        .get("datetime", "")
    )
    assert transit_dt.startswith("2000-01-01T12:00:00")

    if expected_offset_suffix is not None:
        assert transit_dt.endswith(expected_offset_suffix)
    else:
        assert not transit_dt.endswith("+00:00")


def test_v2_forecast_endpoint_uses_requested_date():
    from app.main import api
    from fastapi.testclient import TestClient

    client = TestClient(api)
    profile = {
        "name": "Test",
        "date_of_birth": "1990-06-15",
        "time_of_birth": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": "America/New_York",
    }

    r1 = client.post(
        "/v2/forecasts/daily",
        json={
            "profile": profile,
            "scope": "daily",
            "date": "2000-01-01",
            "include_details": True,
        },
    )
    r2 = client.post(
        "/v2/forecasts/daily",
        json={
            "profile": profile,
            "scope": "daily",
            "date": "2099-12-31",
            "include_details": True,
        },
    )

    assert r1.status_code == 200
    assert r2.status_code == 200

    j1 = r1.json()
    j2 = r2.json()

    assert j1["data"]["date"] == "2000-01-01"
    assert j2["data"]["date"] == "2099-12-31"
    assert j1["data"]["sections"] != j2["data"]["sections"]


def test_forecast_anchor_respects_dst_offset():
    from app.products.forecast import build_forecast

    profile = {
        "name": "Test",
        "date_of_birth": "1990-06-15",
        "time_of_birth": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": "America/New_York",
    }

    winter = build_forecast(profile, scope="daily", target_date="2026-01-15")
    summer = build_forecast(profile, scope="daily", target_date="2026-07-01")

    winter_dt = winter["charts"]["transit"]["metadata"]["datetime"]
    summer_dt = summer["charts"]["transit"]["metadata"]["datetime"]

    assert winter_dt.startswith("2026-01-15T12:00:00")
    assert summer_dt.startswith("2026-07-01T12:00:00")
    assert winter_dt.endswith("-05:00")
    assert summer_dt.endswith("-04:00")
