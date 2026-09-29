"""Numerology text must describe the number shown beside it."""

import warnings
from datetime import datetime, timezone

from starlette.testclient import TestClient

from backend.app.engine.compatibility import LIFE_PATH_COMPAT, get_life_path_compat
from backend.app.engine.numerology_extended import (
    CHALLENGE_MEANINGS,
    calculate_challenges,
)
from backend.app.main import app
from backend.app.numerology_engine import _numerology_text, build_numerology

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def _profile(method: str) -> dict:
    resp = client.post(
        "/v2/numerology/profile",
        json={
            "profile": {"name": "Maria Yolanda Brown", "date_of_birth": "1985-11-29"},
            "method": method,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def test_each_insight_comes_with_the_number_it_was_written_for():
    for method in ("pythagorean", "chaldean"):
        data = _profile(method)
        numbers = data["numerology_numbers"]
        assert set(numbers) == set(data["numerology_insights"]), method
        for key, number in numbers.items():
            assert data["numerology_insights"][key] == _numerology_text(key, number), (
                method,
                key,
            )


def test_numbers_match_the_engine_including_chaldean_and_master_numbers():
    expected = build_numerology(
        "Maria Yolanda Brown", "1985-11-29", datetime.now(timezone.utc), "chaldean"
    )
    numbers = _profile("chaldean")["numerology_numbers"]
    assert numbers["soul_urge"] == expected["core_numbers"]["soul_urge"]["number"]
    assert numbers["personality"] == expected["core_numbers"]["personality"]["number"]
    assert numbers["personal_day"] == expected["cycles"]["personal_day"]["number"]


def test_challenge_text_depends_on_the_challenge_number():
    assert set(CHALLENGE_MEANINGS) == set(range(9))
    # 1985-11-29: month 2, day 2, year 5 -> challenges 0, 3, 3, 3.
    challenges = calculate_challenges("1985-11-29")
    assert [c["number"] for c in challenges] == [0, 3, 3, 3]
    assert challenges[0]["keyword"] == "Choice"
    assert challenges[1]["keyword"] == "Self-expression"

    meanings = {
        c["number"]: c["meaning"] for c in _profile("pythagorean")["challenges"]
    }
    assert meanings[0].startswith("Choice: ")
    assert meanings[3].startswith("Self-expression: ")


def test_master_number_life_paths_use_their_root_pairing():
    assert get_life_path_compat(11, 2)["harmony"] == LIFE_PATH_COMPAT[(2, 2)]["harmony"]
    assert get_life_path_compat(22, 8)["harmony"] == LIFE_PATH_COMPAT[(4, 8)]["harmony"]
    assert get_life_path_compat(33, 2)["harmony"] == LIFE_PATH_COMPAT[(2, 6)]["harmony"]


def test_synthesis_names_the_pinnacle_you_are_in_now():
    # Born 1977: pinnacle 1 runs to about age 30, pinnacle 4 covers age 49.
    data = build_numerology(
        "Abiola Bolaji", "1977-07-02", datetime(2026, 9, 29, tzinfo=timezone.utc)
    )
    current = next(
        p
        for p in data["pinnacles"]
        if p["start_year"] <= 2026 and (p["end_year"] is None or 2026 <= p["end_year"])
    )
    assert current["index"] == 4
    assert f"Pinnacle {current['number']}," in data["synthesis"]["current_focus"]
    first = data["pinnacles"][0]
    if first["number"] != current["number"]:
        assert f"Pinnacle {first['number']}," not in data["synthesis"]["current_focus"]
