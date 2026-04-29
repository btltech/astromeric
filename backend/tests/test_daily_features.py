import hashlib
from datetime import date

from app.engine.daily_features import (
    _calculate_daily_luck_score,
    _calculate_mood_forecast,
    _stable_seed,
    calculate_lucky_numbers,
    check_retrograde_alerts,
    get_all_daily_features,
    get_daily_affirmation,
    get_daily_tarot,
    get_lucky_colors,
    get_lucky_planet,
    get_manifestation_prompt,
)


def test_get_lucky_colors():
    colors = get_lucky_colors("Fire", date(2023, 1, 1), lang="en")
    assert "primary" in colors
    assert "accent" in colors
    assert "description" in colors
    assert isinstance(colors["description"], str)


def test_lucky_numbers_use_birth_year_and_always_return_five():
    reference_date = date(2026, 4, 2)
    numbers_1990 = calculate_lucky_numbers("1990-01-01", reference_date)
    numbers_1980 = calculate_lucky_numbers("1980-01-01", reference_date)

    assert len(numbers_1990) == 5
    assert len(numbers_1980) == 5
    assert numbers_1990 != numbers_1980


def test_get_lucky_colors_can_vary_by_personal_day():
    reference_date = date(2026, 4, 2)
    day_one = get_lucky_colors("Fire", reference_date, lang="en", personal_day=1)
    day_two = get_lucky_colors("Fire", reference_date, lang="en", personal_day=2)

    assert day_one["primary"] == day_two["primary"]
    assert day_one["accent"] != day_two["accent"]


def test_stable_seed_uses_cross_process_stable_hashing():
    payload = "affirmation||Fire||1||2023-01-01||en"
    expected = int.from_bytes(
        hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big", signed=False
    )
    assert _stable_seed("affirmation", "Fire", 1, "2023-01-01", "en") == expected


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


def test_daily_luck_score_matches_mood_forecast():
    reference_date = date(2026, 4, 2)
    luck = _calculate_daily_luck_score("Fire", 1, 5, 9, reference_date)
    mood = _calculate_mood_forecast(
        "Fire", 1, 5, reference_date, lang="en", personal_year=9
    )
    assert mood["luck_score"] == luck
    assert 5 <= mood["luck_score"] <= 100


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
        "Test User", "1990-01-01", "Fire", 1, 1, date(2023, 1, 1), lang="en"
    )
    assert "lucky_colors" in features
    assert "lucky_planet" in features
    assert "affirmation" in features
    assert "tarot" in features
    assert "manifestation" in features
    assert "mood_forecast" in features
    assert "retrograde_alerts" in features
