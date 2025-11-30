"""Tests for extended numerology, compatibility, and glossary modules."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engine.compatibility import (
    calculate_astro_compatibility,
    calculate_combined_compatibility,
    calculate_numerology_compatibility,
)
from app.engine.glossary import (
    NUMEROLOGY_GLOSSARY,
    ZODIAC_GLOSSARY,
    get_number_explanation,
    get_sign_info,
    search_glossary,
)
from app.engine.numerology_extended import (
    analyze_name,
    calculate_challenges,
    calculate_expression_number,
    calculate_maturity_number,
    calculate_personal_day,
    calculate_personal_month,
    calculate_personal_year,
    calculate_personality_number,
    calculate_pinnacles,
    calculate_soul_urge_number,
    get_full_numerology_profile,
)


class TestNumerologyExtended:
    def test_expression_number(self):
        result = calculate_expression_number("John Doe")
        assert isinstance(result, int)
        assert 1 <= result <= 33

    def test_soul_urge(self):
        result = calculate_soul_urge_number("Jane Doe")
        assert isinstance(result, int)
        assert 1 <= result <= 33

    def test_personality_number(self):
        result = calculate_personality_number("Alice Smith")
        assert isinstance(result, int)
        assert 1 <= result <= 33

    def test_maturity_number(self):
        # Maturity number requires life_path and expression numbers
        life_path = 7
        expression = 5
        result = calculate_maturity_number(life_path, expression)
        assert isinstance(result, int)
        assert 1 <= result <= 33

    def test_personal_year(self):
        result = calculate_personal_year("1990-01-01")
        assert isinstance(result, int)
        assert 1 <= result <= 9 or result in (11, 22, 33)

    def test_personal_month(self):
        personal_year = calculate_personal_year("1990-01-01")
        result = calculate_personal_month(personal_year, 6)
        assert isinstance(result, int)

    def test_personal_day(self):
        personal_year = calculate_personal_year("1990-01-01")
        personal_month = calculate_personal_month(personal_year, 6)
        result = calculate_personal_day(personal_month, 15)
        assert isinstance(result, int)

    def test_pinnacles(self):
        pinnacles = calculate_pinnacles("1990-01-01")
        assert len(pinnacles) == 4
        for p in pinnacles:
            assert isinstance(p["number"], int)
            assert "period" in p  # Pinnacles have period, not meaning

    def test_challenges(self):
        challenges = calculate_challenges("1990-01-01")
        assert len(challenges) >= 3  # At least 3 challenges
        for c in challenges:
            assert isinstance(c["number"], int)
            assert "label" in c

    def test_full_numerology_profile(self):
        profile = get_full_numerology_profile("John Doe", "1990-01-01")
        # The profile has nested structure
        assert "core_numbers" in profile
        assert "cycles" in profile
        assert "pinnacles" in profile
        assert "challenges" in profile
        # Check core numbers
        assert "life_path" in profile["core_numbers"]
        assert "expression" in profile["core_numbers"]
        assert "soul_urge" in profile["core_numbers"]
        assert "personality" in profile["core_numbers"]
        assert "maturity" in profile["core_numbers"]

    def test_analyze_name(self):
        result = analyze_name("John Doe")
        assert "expression" in result
        assert "soul_urge" in result
        assert "personality" in result


class TestCompatibility:
    def test_astro_compatibility(self):
        result = calculate_astro_compatibility("1990-01-01", "1992-05-15")
        assert "person1" in result
        assert "person2" in result
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_numerology_compatibility(self):
        result = calculate_numerology_compatibility(
            "John", "1990-01-01", "Jane", "1992-05-15"
        )
        assert "person1" in result
        assert "person2" in result
        assert "life_path_harmony" in result
        assert 0 <= result["life_path_harmony"] <= 100

    def test_combined_compatibility(self):
        result = calculate_combined_compatibility(
            "John", "1990-01-01", "Jane", "1992-05-15", "romantic"
        )
        assert "combined_score" in result
        assert "astrology" in result
        assert "numerology" in result
        assert 0 <= result["combined_score"] <= 100


class TestGlossary:
    def test_zodiac_glossary_exists(self):
        assert len(ZODIAC_GLOSSARY) == 12
        assert "Aries" in ZODIAC_GLOSSARY
        assert "Pisces" in ZODIAC_GLOSSARY

    def test_get_sign_info(self):
        info = get_sign_info("Aries")
        assert info is not None
        assert "element" in info
        assert "modality" in info
        assert "description" in info

    def test_get_sign_info_case_insensitive(self):
        info = get_sign_info("aries")
        assert info is not None

    def test_numerology_glossary_exists(self):
        assert len(NUMEROLOGY_GLOSSARY) > 0
        # Check for general terms like "Life Path" without number
        assert "Life Path" in NUMEROLOGY_GLOSSARY or any(
            "Life" in k for k in NUMEROLOGY_GLOSSARY.keys()
        )

    def test_get_number_explanation(self):
        # Try getting explanation for "Life Path"
        info = get_number_explanation("Life Path")
        assert info is not None
        assert "meaning" in info or "calculation" in info

    def test_search_glossary(self):
        results = search_glossary("fire")
        assert isinstance(results, list)
        # Should find fire signs like Aries, Leo, Sagittarius
        assert len(results) > 0

    def test_search_glossary_no_results(self):
        results = search_glossary("xyznonexistent")
        assert results == []


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
