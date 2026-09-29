"""The daily numerology library: complete, in voice, and never repeating within a year."""

import re
import warnings
from collections import Counter
from datetime import date, timedelta

from starlette.testclient import TestClient

from backend.app.interpretation.numerology_library import (
    LENSES,
    MASTER_DAYS,
    daily_reading,
    lens_slot,
    load_library,
)
from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)

PERSONAL_YEARS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)
BANNED = re.compile(
    r"\byou will\b|\buniverse\b|\bmanifest|\bcosmic\b|\bvibes?\b|personal (day|month)",
    re.IGNORECASE,
)
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")


def _days(year: int):
    day = date(year, 1, 1)
    while day.year == year:
        yield day
        day += timedelta(days=1)


def test_every_pairing_has_eight_passages_in_voice():
    daily = load_library()["daily"]
    assert sorted(daily, key=int) == [str(n) for n in range(1, 10)]
    seen = set()
    for month, days in daily.items():
        assert sorted(days, key=int) == [str(n) for n in range(1, 10)], month
        for day, passages in days.items():
            assert len(passages) == len(LENSES), (month, day)
            for text in passages:
                words = len(text.split())
                # 38, not 45: several approved sample passages run 39-44 words.
                assert 38 <= words <= 65, (month, day, words, text)
                assert "!" not in text and not EMOJI.search(text), text
                assert not BANNED.search(text), text
                assert text not in seen, text
                seen.add(text)


def test_every_master_day_has_an_opener_per_lens():
    masters = load_library()["master_days"]
    assert sorted(masters, key=int) == [str(n) for n in MASTER_DAYS]
    for number, lines in masters.items():
        assert len(lines) == len(LENSES), number
        for line in lines:
            assert 15 <= len(line.split()) <= 40, line
            assert "!" not in line and not BANNED.search(line), line


def test_no_one_sees_the_same_reading_twice_in_a_year():
    for year in (2026, 2027, 2028):  # 2028 is a leap year
        for personal_year in PERSONAL_YEARS:
            texts = Counter(
                daily_reading(personal_year, day)["text"] for day in _days(year)
            )
            repeated = [text for text, count in texts.items() if count > 1]
            assert not repeated, (year, personal_year, repeated[:1])


def test_versions_are_met_in_lens_order():
    # The first time a pairing comes round in a year is its work passage, the
    # second its relationships passage, and so on.
    first_seen = {}
    for day in _days(2027):
        reading = daily_reading(4, day)
        pairing = (reading["personal_day"] % 9 or 9, reading["personal_month"] % 9 or 9)
        first_seen.setdefault(pairing, []).append(lens_slot(4, day))
    for slots in first_seen.values():
        assert slots == list(range(len(slots))), slots


def test_master_days_open_with_their_line_then_the_root_passage():
    library = load_library()
    for day in _days(2027):
        reading = daily_reading(4, day)
        if reading["personal_day"] not in MASTER_DAYS:
            continue
        slot = LENSES.index(reading["lens"])
        opener = library["master_days"][str(reading["personal_day"])][slot]
        assert reading["text"].startswith(opener + " ")
        return
    raise AssertionError("no master day found in 2027 for Personal Year 4")


def test_profile_endpoint_returns_todays_reading():
    resp = client.post(
        "/v2/numerology/profile",
        json={
            "profile": {"name": "Maria Yolanda Brown", "date_of_birth": "1985-11-29"}
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    reading = data["daily_reading"]
    assert reading["lens"] in LENSES
    assert reading["personal_day"] == data["numerology_numbers"]["personal_day"]
    assert len(reading["text"].split()) >= 38


# --- Lifelong, yearly, relationship and cycle readings ----------------------

from backend.app.interpretation.numerology_library import (  # noqa: E402
    LIFELONG_POSITIONS,
    cycle_reading,
    life_path_pair_reading,
    lifelong_reading,
    load_readings,
    month_reading,
    year_reading,
)

NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)


def _in_voice(text: str, low: int, high: int) -> None:
    assert low <= len(text.split()) <= high, (len(text.split()), text[:80])
    assert "!" not in text and not EMOJI.search(text), text[:80]
    assert not BANNED.search(text), text[:80]


def test_every_lifelong_reading_exists_and_reads_as_lifelong():
    for position in LIFELONG_POSITIONS:
        for number in NUMBERS:
            reading = lifelong_reading(position, number)
            assert reading and 2 <= len(reading["title"].split()) <= 4, (
                position,
                number,
            )
            _in_voice(reading["text"], 170, 230)
            assert not re.search(r"\btoday\b", reading["text"], re.I), (
                position,
                number,
            )


def test_every_life_path_pair_reads_the_same_either_way_round():
    for a in NUMBERS:
        for b in NUMBERS:
            text = life_path_pair_reading(a, b)
            assert text and text == life_path_pair_reading(b, a), (a, b)
            _in_voice(text, 90, 130)
    assert life_path_pair_reading(10, 4) is None


def test_every_year_and_month_reading_exists():
    for life_path in NUMBERS:
        for personal_year in range(1, 10):
            _in_voice(year_reading(life_path, personal_year), 90, 130)
    # A master Personal Year reads as its root.
    assert year_reading(7, 11) == year_reading(7, 2)
    for personal_year in range(1, 10):
        for personal_month in range(1, 10):
            _in_voice(month_reading(personal_year, personal_month), 60, 85)


def test_cycle_readings_cover_every_number_they_can_take():
    for number in NUMBERS:
        _in_voice(cycle_reading("pinnacles", number)["text"], 60, 90)
    for number in range(9):
        _in_voice(cycle_reading("challenges", number)["text"], 60, 90)
    for number in (13, 14, 16, 19):
        _in_voice(cycle_reading("karmic_debt", number)["text"], 80, 110)
    assert set(load_readings()["karmic_debt"]) == {"13", "14", "16", "19"}


def test_profile_carries_the_full_readings_beside_the_short_ones():
    resp = client.post(
        "/v2/numerology/profile",
        json={
            "profile": {"name": "Maria Yolanda Brown", "date_of_birth": "1985-11-29"}
        },
    )
    data = resp.json()["data"]
    life_path = data["life_path"]["number"]
    assert data["lifelong"]["life_path"]["number"] == life_path
    assert (
        data["lifelong"]["life_path"]["text"]
        == lifelong_reading("life_path", life_path)["text"]
    )
    assert set(data["lifelong"]) == set(LIFELONG_POSITIONS)
    assert data["year_reading"] == year_reading(
        life_path, data["personal_year"]["cycle_number"]
    )
    assert data["month_reading"]
    assert all(p["reading"] for p in data["pinnacles"])
    assert all(c["reading"] for c in data["challenges"])
    # Short fields are untouched: build 6 shows them in clipped rows.
    assert len(data["life_path"]["meaning"].split()) < 40


def test_compatibility_life_path_dimension_uses_the_pair_reading():
    resp = client.post(
        "/v2/compatibility/romantic",
        json={
            "person_a": {"name": "A", "date_of_birth": "1990-06-15"},
            "person_b": {"name": "B", "date_of_birth": "1992-11-03"},
        },
    )
    assert resp.status_code == 200, resp.text
    dims = {d["name"]: d["interpretation"] for d in resp.json()["data"]["dimensions"]}
    assert dims["Life Path"] in load_readings()["compatibility"].values()
