from unittest.mock import patch

from app.engine.numerology import (
    calculate_life_path_number,
    calculate_name_number,
    get_life_path_data,
)


class TestNumerology:
    def test_calculate_life_path_number(self):
        # Standard Pythagorean method: reduce month/day/year separately, then sum.
        assert calculate_life_path_number("1990-03-21") == 7

        # 1980-01-01 -> month(1) + day(1) + year(1980->9) = 11 (master number preserved)
        assert calculate_life_path_number("1980-01-01") == 11

    def test_calculate_name_number(self):
        # A=1, B=2, C=3
        assert calculate_name_number("ABC") == 6
        # a=1, b=2, c=3
        assert calculate_name_number("abc") == 6
        # Space ignored
        assert calculate_name_number("A B C") == 6

    def test_get_life_path_data_structure(self):
        data = get_life_path_data(1)
        assert isinstance(data, dict)
        assert "meaning" in data
        assert "advice" in data
        assert isinstance(data["advice"], list)

    def test_get_life_path_data_content(self):
        data = get_life_path_data(1)
        assert data["meaning"] == "Leadership and independence"
        assert "Take initiative" in data["advice"]

    def test_get_life_path_data_invalid(self):
        data = get_life_path_data(999)
        assert data["meaning"] == "Unknown path"


class TestNumerologyLocalization:
    @patch("app.engine.numerology.get_translation")
    def test_get_life_path_data_localized(self, mock_get_translation):
        # Setup mock
        def side_effect(lang, category, key):
            if lang == "es" and category == "numerology_life_path":
                if key == "numerology_life_path_1_meaning":
                    return "Liderazgo e independencia"
                if key == "numerology_life_path_1_advice_0":
                    return "Toma la iniciativa"
            return None

        mock_get_translation.side_effect = side_effect

        data = get_life_path_data(1, lang="es")

        assert data["meaning"] == "Liderazgo e independencia"
        assert data["advice"][0] == "Toma la iniciativa"
        # Check fallback
        assert data["advice"][1] == "Trust your instincts"
