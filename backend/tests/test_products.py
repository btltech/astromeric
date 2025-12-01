from backend.app.products import build_compatibility, build_forecast


def _profile():
    return {
        "name": "Snapshot User",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "08:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "house_system": "Placidus",
    }


def test_build_forecast_sections():
    profile = _profile()
    forecast = build_forecast(profile, scope="daily")
    assert forecast["scope"] == "daily"
    assert len(forecast["sections"]) >= 1
    titles = [s["title"] for s in forecast["sections"]]
    assert "Overview" in titles
    assert "theme" in forecast


def test_build_compatibility_strengths():
    person_a = _profile()
    person_b = dict(person_a)
    person_b["name"] = "Partner"
    compatibility = build_compatibility(person_a, person_b)
    assert "strengths" in compatibility and isinstance(compatibility["strengths"], list)
    assert "challenges" in compatibility and isinstance(
        compatibility["challenges"], list
    )
    assert "advice" in compatibility
