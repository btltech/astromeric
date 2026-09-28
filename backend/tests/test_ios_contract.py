"""The response fields the iOS app cannot decode without.

Each test here pins a field that, when missing or the wrong type, made a whole
screen fail to decode on device while the endpoint still returned 200. The
payloads mirror what the app sends (Core/API/Endpoints.swift).
"""

import re
import warnings

from starlette.testclient import TestClient

from backend.app.engine.year_ahead import get_eclipses_for_year, get_ingresses_for_year
from backend.app.main import app
from backend.app.rule_engine import _aspect_meaning

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)

PROFILE = {
    "name": "Test User",
    "date_of_birth": "1990-06-15",
    "time_of_birth": "14:30:00",
    "place_of_birth": "London, United Kingdom",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "house_system": "Placidus",
}
PROFILE_NO_TIME = {k: v for k, v in PROFILE.items() if k != "time_of_birth"}

# JSONDecoder's .iso8601 strategy on iOS 17/18: no fractional seconds.
WHOLE_SECOND_ISO8601 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$"
)


def _data(resp):
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def test_daily_reading_timestamps_decode_on_ios_17_and_18():
    data = _data(client.post("/v2/daily/reading", json=PROFILE))
    for field in ("date", "generated_at"):
        assert WHOLE_SECOND_ISO8601.match(data[field]), (field, data[field])


def test_morning_brief_date_decodes_on_ios_17_and_18():
    data = _data(client.post("/v2/daily/brief", json=PROFILE))
    assert WHOLE_SECOND_ISO8601.match(data["date"]), data["date"]


def test_progressed_metadata_carries_target_date():
    data = _data(client.post("/v2/charts/progressed", json={"profile": PROFILE}))
    metadata = data["metadata"]
    assert isinstance(metadata["progressed_date"], str)
    assert isinstance(metadata["target_date"], str)


def test_upcoming_moon_events_have_phase_and_description():
    data = _data(client.get("/v2/moon/upcoming"))
    assert data["events"]
    for event in data["events"]:
        for field in ("date", "type", "phase", "description"):
            assert isinstance(event[field], str) and event[field], (field, event)


def test_moon_ritual_avoid_is_text_and_events_are_complete():
    data = _data(client.post("/v2/moon/ritual", json={"profile": PROFILE}))
    assert isinstance(data["ritual"]["avoid"], str)
    for event in data["upcoming_events"]:
        for field in ("date", "type", "phase", "description"):
            assert isinstance(event[field], str), (field, event)


def test_compatibility_reports_confidence_where_the_app_reads_it():
    partner_no_time = {"name": "Partner", "date_of_birth": "1992-11-03"}
    data = _data(
        client.post(
            "/v2/compatibility/romantic",
            json={"person_a": PROFILE, "person_b": partner_no_time},
        )
    )
    assert data["data_confidence"]["score"] < 100
    assert "Birth time unknown" in data["data_confidence"]["note"]

    partner = {**partner_no_time, "time_of_birth": "08:15"}
    data = _data(
        client.post(
            "/v2/compatibility/romantic",
            json={"person_a": PROFILE, "person_b": partner},
        )
    )
    assert data["data_confidence"] == {"score": 100, "note": None}


def test_forecast_text_reads_as_english():
    for scope in ("daily", "weekly", "monthly"):
        for profile in (PROFILE, PROFILE_NO_TIME):
            data = _data(
                client.post(
                    f"/v2/forecasts/{scope}", json={"profile": profile, "scope": scope}
                )
            )
            text = " ".join(
                [data.get("tldr") or ""] + [s["summary"] for s in data["sections"]]
            )
            for broken in (
                "Daily's",
                "Weekly's",
                "Monthly's",
                "this daily",
                "This day's",
                "points to Your",
            ):
                assert broken not in text, (scope, broken, text)


def test_weekly_and_monthly_do_not_repeat_the_days_guidance():
    daily = _data(
        client.post("/v2/forecasts/daily", json={"profile": PROFILE, "scope": "daily"})
    )
    day_avoid = daily["sections"][0]["avoid"]
    assert day_avoid, "daily Overview should carry the day's guidance"
    for scope in ("weekly", "monthly"):
        data = _data(
            client.post(
                f"/v2/forecasts/{scope}", json={"profile": PROFILE, "scope": scope}
            )
        )
        assert data["sections"][0]["avoid"] != day_avoid, scope


def test_plural_themes_take_plural_verbs():
    text = _aspect_meaning("Neptune", "Mercury", "sextile", {"sextile": {"text": ""}})[
        "text"
    ]
    assert text == "Your mystic waters open doors to your quicksilver mind."
    text = _aspect_meaning("Venus", "Mercury", "sextile", {"sextile": {"text": ""}})[
        "text"
    ]
    assert text == "Your heart magnetism opens doors to your quicksilver mind."


def test_2026_sky_events_match_the_ephemeris():
    eclipse = next(e for e in get_eclipses_for_year(2026) if e["date"] == "2026-08-12")
    assert eclipse["type"] == "Total Solar Eclipse"
    ingresses = {
        (i["planet"], i["sign"]): i["date"] for i in get_ingresses_for_year(2026)
    }
    assert ingresses == {
        ("Neptune", "Aries"): "2026-01-26",
        ("Saturn", "Aries"): "2026-02-14",
        ("Uranus", "Gemini"): "2026-04-26",
        ("Jupiter", "Leo"): "2026-06-30",
    }
