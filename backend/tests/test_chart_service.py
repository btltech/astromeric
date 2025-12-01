import copy

from backend.app import chart_service


def _profile():
    return {
        "name": "Test User",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "08:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "house_system": "Placidus",
    }


def test_build_natal_chart_structure():
    chart = chart_service.build_natal_chart(_profile())
    assert chart["metadata"]["chart_type"] == "natal"
    assert len(chart["planets"]) == len(chart_service.PLANETS)
    assert len(chart["houses"]) == 12
    assert "aspects" in chart


def test_stub_fallback(monkeypatch):
    profile = copy.deepcopy(_profile())
    original = chart_service.HAS_FLATLIB
    try:
        chart_service.HAS_FLATLIB = False
        chart = chart_service.build_natal_chart(profile)
        assert chart["metadata"].get("provider") == "stub"
    finally:
        chart_service.HAS_FLATLIB = original
