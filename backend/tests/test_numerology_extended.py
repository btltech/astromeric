import pytest
from unittest.mock import patch, MagicMock
from app.engine.numerology_extended import (
    get_number_meaning,
    calculate_challenges,
    calculate_pinnacles,
    get_full_numerology_profile,
    analyze_name,
    NUMBER_MEANINGS
)

class TestNumerologyExtended:
    def test_get_number_meaning(self):
        meaning = get_number_meaning(1)
        assert meaning["keyword"] == "Leadership"
        assert meaning["description"] == "Independent pioneer. Forge your own path."
        
        meaning = get_number_meaning(999)
        assert meaning["keyword"] == "Unknown"

    def test_calculate_challenges(self):
        # 1990-03-21
        # Month=3, Day=21->3, Year=1990->19->10->1
        # c1 = |3-3| = 0
        # c2 = |3-1| = 2
        # c3 = |0-2| = 2
        challenges = calculate_challenges("1990-03-21")
        assert len(challenges) == 3
        assert challenges[0]["label"] == "First Challenge"
        assert challenges[0]["description"] == "Early life lesson"
        assert challenges[0]["number"] == 0
        assert challenges[1]["number"] == 2
        assert challenges[2]["number"] == 2

    def test_calculate_pinnacles(self):
        # 1990-03-21
        # Month=3, Day=3, Year=1
        # Life Path = 3+3+1 = 7
        # First end = 36 - 7 = 29
        pinnacles = calculate_pinnacles("1990-03-21")
        assert len(pinnacles) == 4
        assert pinnacles[0]["period"] == "Birth to age 29"
        assert pinnacles[1]["period"] == "Age 30 to 38"

    def test_get_full_numerology_profile(self):
        profile = get_full_numerology_profile("John Doe", "1990-03-21")
        assert "core_numbers" in profile
        assert "cycles" in profile
        assert "pinnacles" in profile
        assert "challenges" in profile
        assert profile["core_numbers"]["life_path"]["keyword"] == "Analysis" # 7

    def test_analyze_name(self):
        analysis = analyze_name("John Doe")
        assert "expression" in analysis
        assert "soul_urge" in analysis
        assert "personality" in analysis

class TestNumerologyExtendedLocalization:
    @patch('app.engine.numerology_extended.get_translation')
    def test_get_number_meaning_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es" and category == "numerology_meanings":
                if key == "numerology_number_1_keyword":
                    return "Liderazgo"
                if key == "numerology_number_1_description":
                    return "Pionero independiente."
            return None
        mock_get_translation.side_effect = side_effect
        
        meaning = get_number_meaning(1, lang="es")
        assert meaning["keyword"] == "Liderazgo"
        assert meaning["description"] == "Pionero independiente."

    @patch('app.engine.numerology_extended.get_translation')
    def test_calculate_challenges_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es" and category == "numerology_challenges":
                if key == "first_label": return "Primer Desafío"
                if key == "first_desc": return "Lección temprana"
            return None
        mock_get_translation.side_effect = side_effect
        
        challenges = calculate_challenges("1990-03-21", lang="es")
        assert challenges[0]["label"] == "Primer Desafío"
        assert challenges[0]["description"] == "Lección temprana"

    @patch('app.engine.numerology_extended.get_translation')
    def test_calculate_pinnacles_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es" and category == "numerology_periods":
                if key == "birth_to_age": return "Nacimiento a edad {age}"
            return None
        mock_get_translation.side_effect = side_effect
        
        pinnacles = calculate_pinnacles("1990-03-21", lang="es")
        # Life path 7, first end 29
        assert pinnacles[0]["period"] == "Nacimiento a edad 29"

