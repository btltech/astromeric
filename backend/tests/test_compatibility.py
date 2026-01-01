import pytest
from unittest.mock import patch
from app.engine.compatibility import (
    calculate_astro_compatibility,
    calculate_numerology_compatibility,
    calculate_combined_compatibility,
    get_element_compat,
    get_life_path_compat
)

def test_get_element_compat_en():
    result = get_element_compat("Fire", "Water", lang="en")
    assert result["score"] == 40
    assert "Steam or sizzle" in result["desc"]

def test_get_element_compat_localized():
    with patch("app.engine.compatibility.get_translation") as mock_trans:
        mock_trans.return_value = ["Fuego y Agua"]
        result = get_element_compat("Fire", "Water", lang="es")
        assert result["desc"] == "Fuego y Agua"

def test_calculate_astro_compatibility_en():
    # Aries (Fire) and Cancer (Water)
    result = calculate_astro_compatibility("1990-03-21", "1990-06-22", lang="en")
    assert result["score"] == 40
    assert "Both share" not in result["strengths"][0]
    assert "balance each other" in result["strengths"][0]

def test_calculate_astro_compatibility_localized():
    with patch("app.engine.compatibility.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key == "compat_strength_diff_element":
                return ["{elem1} y {elem2} balance"]
            if key == "compat_strength_sign1":
                return ["{sign} perspectiva"]
            if key == "compat_strength_sign2":
                return ["{sign} energia"]
            return None
        mock_trans.side_effect = side_effect
        
        result = calculate_astro_compatibility("1990-03-21", "1990-06-22", lang="es")
        assert "Fire y Water balance" in result["strengths"][0]

def test_calculate_numerology_compatibility_en():
    # LP 1 and LP 1
    result = calculate_numerology_compatibility("John", "1990-01-01", "Jane", "1990-01-01", lang="en")
    assert "Life Paths" in result["summary"]

def test_calculate_numerology_compatibility_localized():
    with patch("app.engine.compatibility.get_translation") as mock_trans:
        mock_trans.return_value = ["Caminos {lp1} y {lp2}"]
        result = calculate_numerology_compatibility("John", "1990-01-01", "Jane", "1990-01-01", lang="es")
        assert "Caminos" in result["summary"]

def test_calculate_combined_compatibility_en():
    result = calculate_combined_compatibility("John", "1990-03-21", "Jane", "1990-06-22", lang="en")
    assert "overall_assessment" in result
    assert "top_advice" in result

def test_calculate_combined_compatibility_localized():
    with patch("app.engine.compatibility.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key.startswith("compat_overall"):
                return ["Evaluacion {frame}"]
            if key.startswith("compat_rel_frame"):
                return ["Marco"]
            if key == "compat_advice_leverage":
                return ["Aprovechar {e1}-{e2}"]
            if key == "compat_advice_communicate":
                return ["Comunicar"]
            return None
        mock_trans.side_effect = side_effect
        
        result = calculate_combined_compatibility("John", "1990-03-21", "Jane", "1990-06-22", lang="es")
        assert "Evaluacion Marco" in result["overall_assessment"]
        assert "Aprovechar Fire-Water" in result["top_advice"][1]
        assert "Comunicar" in result["top_advice"][2]
