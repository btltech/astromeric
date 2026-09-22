"""Regression tests for the advanced chart techniques used by the Android app."""

from app.chart_service import build_lunar_return_chart, build_solar_arc_chart
from app.engine.advanced_techniques import calculate_profections

PROFILE = {
    "name": "Test",
    "date_of_birth": "1990-05-15",
    "time_of_birth": "14:30",
    "latitude": 40.71,
    "longitude": -74.01,
    "timezone": "America/New_York",
    "house_system": "Placidus",
}


def test_profections_feb_29_birthday_in_common_year():
    result = calculate_profections("1992-02-29", "2026-09-22")
    assert result["age"] == 34
    assert result["annual_house"] == 11


def test_profections_feb_29_birthday_falls_on_feb_28():
    assert calculate_profections("1992-02-29", "2026-02-27")["age"] == 33
    assert calculate_profections("1992-02-29", "2026-02-28")["age"] == 34


def test_profections_lord_counts_from_ascendant_sign():
    # 1st-house year for a Leo rising: profected sign Leo, lord Sun.
    result = calculate_profections("2014-03-10", "2026-09-22", ascendant_sign="Leo")
    assert result["annual_house"] == 1
    assert result["annual_sign"] == "Leo"
    assert result["annual_lord"] == "Sun"


def test_profections_without_ascendant_leaves_lord_blank():
    result = calculate_profections("2014-03-10", "2026-09-22")
    assert result["annual_lord"] == ""
    assert result["monthly_lord"] == ""
    assert result["annual_sign"] is None


def test_solar_arc_aspects_are_directed_to_natal_only_and_sorted():
    chart = build_solar_arc_chart(PROFILE, "2026-09-22")
    aspects = chart["aspects"]
    assert aspects
    for a in aspects:
        assert a["planet_a"].endswith("(d)")
        assert not a["planet_b"].endswith("(d)")
    orbs = [a["orb"] for a in aspects]
    assert orbs == sorted(orbs)


def test_solar_arc_planets_do_not_carry_natal_motion():
    chart = build_solar_arc_chart(PROFILE, "2026-09-22")
    assert all(p["retrograde"] is False for p in chart["planets"])


def test_solar_arc_advances_between_birthdays():
    before = build_solar_arc_chart(PROFILE, "2026-05-16")["metadata"]
    later = build_solar_arc_chart(PROFILE, "2026-11-16")["metadata"]
    assert later["solar_arc_degrees"] > before["solar_arc_degrees"]


def test_lunar_return_searches_from_the_given_instant():
    early = build_lunar_return_chart(PROFILE, "2026-09-01T00:00:00+00:00")
    late = build_lunar_return_chart(PROFILE, "2026-09-01T00:00:00-12:00")
    assert (
        early["metadata"]["return_datetime_utc"]
        <= late["metadata"]["return_datetime_utc"]
    )
    # The return is never before the requested instant.
    assert early["metadata"]["return_datetime_utc"] >= "2026-09-01T00:00:00"
