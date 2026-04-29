from datetime import datetime, timezone

from backend.app.numerology_engine import build_numerology
from backend.tests.test_numerology_v2 import client


def test_build_numerology_includes_deterministic_synthesis():
    numerology = build_numerology(
        "Taylor Example",
        "1990-03-21",
        datetime(2025, 1, 15, tzinfo=timezone.utc),
    )

    synthesis = numerology["synthesis"]
    assert synthesis["summary"]
    assert "Life Path" in synthesis["summary"]
    assert "Personal Year" in synthesis["summary"]
    assert len(synthesis["strengths"]) >= 3
    assert len(synthesis["growth_edges"]) >= 1
    assert synthesis["affirmation"].startswith("I ")
    assert [item["key"] for item in synthesis["dominant_numbers"]] == [
        "life_path",
        "expression",
        "soul_urge",
        "personal_year",
    ]


def test_v2_numerology_profile_exposes_synthesis_block():
    payload = {
        "profile": {
            "name": "Taylor Example",
            "date_of_birth": "1990-03-21",
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
    synthesis = body["data"]["synthesis"]

    assert synthesis["summary"]
    assert synthesis["current_focus"]
    assert synthesis["affirmation"]
    assert synthesis["dominant_numbers"][0]["key"] == "life_path"
    assert (
        synthesis["dominant_numbers"][0]["number"]
        == body["data"]["life_path"]["number"]
    )
