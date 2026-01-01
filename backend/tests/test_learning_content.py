import pytest
from unittest.mock import patch
from app.engine.learning_content import (
    get_moon_sign_lesson,
    get_rising_sign_lesson,
    get_element_lesson,
    get_modality_lesson,
    get_retrograde_guide,
    get_mini_course,
    get_learning_module,
    get_lesson,
    search_learning_content
)

def test_get_moon_sign_lesson_en():
    result = get_moon_sign_lesson("Aries", lang="en")
    assert "Aries Moon" in result["title"]
    assert "fiery" in result["short_desc"]

def test_get_moon_sign_lesson_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key == "learn_moon_aries_title": return ["Luna en Aries"]
            if key == "learn_moon_aries_short": return ["Naturaleza de fuego"]
            return None
        mock_trans.side_effect = side_effect
        
        result = get_moon_sign_lesson("Aries", lang="es")
        assert result["title"] == "Luna en Aries"
        assert result["short_desc"] == "Naturaleza de fuego"

def test_get_rising_sign_lesson_en():
    result = get_rising_sign_lesson("Aries", lang="en")
    assert "Aries Rising" in result["title"]

def test_get_rising_sign_lesson_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        mock_trans.return_value = ["Ascendente Aries"]
        result = get_rising_sign_lesson("Aries", lang="es")
        assert result["title"] == "Ascendente Aries"

def test_get_element_lesson_en():
    result = get_element_lesson("Fire", lang="en")
    assert "Fire signs burn" in result["description"]

def test_get_element_lesson_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        mock_trans.return_value = ["Elemento Fuego Desc"]
        result = get_element_lesson("Fire", lang="es")
        assert result["description"] == "Elemento Fuego Desc"

def test_get_learning_module_en():
    result = get_learning_module("moon_signs", lang="en")
    assert "Moon Signs" in result["title"]

def test_get_learning_module_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        mock_trans.return_value = ["Signos Lunares"]
        result = get_learning_module("moon_signs", lang="es")
        assert result["title"] == "Signos Lunares"

def test_get_lesson_en():
    result = get_lesson("read_your_chart", 1, lang="en")
    assert result["lesson_number"] == 1
    assert "The Big Three" in result["title"]

def test_get_lesson_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key == "learn_lesson_read_your_chart_1_title": return ["Los Tres Grandes"]
            return None
        mock_trans.side_effect = side_effect
        
        result = get_lesson("read_your_chart", 1, lang="es")
        assert result["title"] == "Los Tres Grandes"

def test_search_learning_content_en():
    results = search_learning_content("Aries", lang="en")
    assert len(results) > 0
    assert results[0]["key"] == "Aries"

def test_search_learning_content_localized():
    with patch("app.engine.learning_content.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key == "learn_moon_aries_title": return ["Luna en Aries"]
            if key == "learn_moon_aries_short": return ["Naturaleza de fuego"]
            return None
        mock_trans.side_effect = side_effect
        
        results = search_learning_content("Aries", lang="es")
        aries_moon = next((r for r in results if r["type"] == "moon_sign" and r["key"] == "Aries"), None)
        assert aries_moon
        assert aries_moon["title"] == "Luna en Aries"
