import pytest
from datetime import date
from app.engine.daily_features import (
    get_lucky_colors,
    get_lucky_planet,
    get_daily_affirmation,
    get_daily_tarot,
    get_manifestation_prompt,
    _calculate_mood_forecast,
    check_retrograde_alerts,
    get_all_daily_features
)

def test_get_lucky_colors():
    colors = get_lucky_colors("Fire", date(2023, 1, 1), lang="en")
    assert "primary" in colors
    assert "accent" in colors
    assert "description" in colors
    assert isinstance(colors["description"], str)

def test_get_lucky_planet():
    planet = get_lucky_planet(date(2023, 1, 1), 1, lang="en")
    assert "planet" in planet
    assert "message" in planet
    assert isinstance(planet["message"], str)

def test_get_daily_affirmation():
    affirmation = get_daily_affirmation("Fire", 1, date(2023, 1, 1), lang="en")
    assert "text" in affirmation
    assert "instruction" in affirmation
    assert isinstance(affirmation["text"], str)

def test_get_daily_tarot():
    tarot = get_daily_tarot(date(2023, 1, 1), "Test User", lang="en")
    assert "card" in tarot
    assert "message" in tarot
    assert "daily_advice" in tarot

def test_get_manifestation_prompt():
    prompt = get_manifestation_prompt(1, 1, date(2023, 1, 1), lang="en")
    assert "prompt" in prompt
    assert "practice" in prompt
    assert "visualization" in prompt

def test_calculate_mood_forecast():
    mood = _calculate_mood_forecast("Fire", 1, 1, date(2023, 1, 1), lang="en")
    assert "mood" in mood
    assert "description" in mood
    assert "tips" in mood

def test_check_retrograde_alerts():
    # Test a date known to be in retrograde (from the list in daily_features.py)
    # ("2024-04-01", "2024-04-25")
    alerts = check_retrograde_alerts(date(2024, 4, 10), lang="en")
    assert len(alerts) > 0
    assert alerts[0]["planet"] == "Mercury"
    assert "message" in alerts[0]
    assert "advice" in alerts[0]

def test_get_all_daily_features():
    features = get_all_daily_features(
        "Test User",
        "1990-01-01",
        "Fire",
        1,
        1,
        date(2023, 1, 1),
        lang="en"
    )
    assert "lucky_colors" in features
    assert "lucky_planet" in features
    assert "affirmation" in features
    assert "tarot" in features
    assert "manifestation" in features
    assert "mood_forecast" in features
    assert "retrograde_alerts" in features
