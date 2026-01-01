import pytest
from unittest.mock import patch, MagicMock
from app.engine.astrology import get_zodiac_sign, get_element, get_sign_traits, SIGN_TRAITS

class TestAstrology:
    def test_get_zodiac_sign(self):
        assert get_zodiac_sign("1990-03-21") == "Aries"
        assert get_zodiac_sign("1990-04-19") == "Aries"
        assert get_zodiac_sign("1990-04-20") == "Taurus"
        assert get_zodiac_sign("1990-12-31") == "Capricorn"
        assert get_zodiac_sign("1990-01-01") == "Capricorn"

    def test_get_element(self):
        assert get_element("Aries") == "Fire"
        assert get_element("Taurus") == "Earth"
        assert get_element("Gemini") == "Air"
        assert get_element("Cancer") == "Water"
        assert get_element("Unknown") == "Unknown"

    def test_get_sign_traits_structure(self):
        traits = get_sign_traits("Aries")
        assert isinstance(traits, dict)
        assert "general" in traits
        assert "love" in traits
        assert "money" in traits
        assert "career" in traits
        assert "health" in traits
        assert "spiritual" in traits
        assert isinstance(traits["general"], list)
        assert len(traits["general"]) > 0

    def test_get_sign_traits_content(self):
        traits = get_sign_traits("Aries")
        assert "Bold energy" in traits["general"]
        
        traits = get_sign_traits("Taurus")
        assert "Steady presence" in traits["general"]

    def test_get_sign_traits_invalid(self):
        traits = get_sign_traits("InvalidSign")
        assert traits == {"love": [], "money": [], "career": []}

class TestAstrologyLocalization:
    @patch('app.engine.astrology.get_translation')
    def test_get_sign_traits_localized(self, mock_get_translation):
        # Setup mock to return a translated string for a specific key
        def side_effect(lang, category, key):
            if lang == "es" and category == "astrology_traits" and key == "Aries_general_0":
                return "Energía audaz"
            return None
            
        mock_get_translation.side_effect = side_effect
        
        traits = get_sign_traits("Aries", lang="es")
        
        # Check if the first trait in 'general' is translated
        assert traits["general"][0] == "Energía audaz"
        # Check if other traits fall back to English (since mock returns None)
        assert traits["general"][1] == "Direct action"

