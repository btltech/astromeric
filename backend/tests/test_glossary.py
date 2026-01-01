import pytest
from unittest.mock import patch
from app.engine.glossary import (
    get_sign_info,
    get_number_explanation,
    get_master_number_info,
    get_element_info,
    search_glossary
)

def test_get_sign_info_en():
    result = get_sign_info("Aries", lang="en")
    assert result["element"] == "Fire"
    assert "Aries is the first sign" in result["description"]

def test_get_sign_info_localized():
    with patch("app.engine.glossary.get_translation") as mock_trans:
        def side_effect(lang, key):
            if key == "glossary_zodiac_aries_desc":
                return ["Aries es el primer signo"]
            if key == "glossary_zodiac_aries_traits":
                return ["Valiente", "Pionero"]
            return None
        mock_trans.side_effect = side_effect
        
        result = get_sign_info("Aries", lang="es")
        assert result["description"] == "Aries es el primer signo"
        assert "Valiente" in result["traits"]

def test_get_number_explanation_en():
    result = get_number_explanation("Life Path", lang="en")
    assert "core life purpose" in result["meaning"]

def test_get_number_explanation_localized():
    with patch("app.engine.glossary.get_translation") as mock_trans:
        mock_trans.return_value = ["Proposito primario"]
        result = get_number_explanation("Life Path", lang="es")
        assert result["meaning"] == "Proposito primario"

def test_get_master_number_info_en():
    result = get_master_number_info(11, lang="en")
    assert "Intuitive Master" in result["title"]

def test_get_master_number_info_localized():
    with patch("app.engine.glossary.get_translation") as mock_trans:
        mock_trans.return_value = ["Maestro Iluminador Desc"]
        result = get_master_number_info(11, lang="es")
        assert result["description"] == "Maestro Iluminador Desc"

def test_get_element_info_en():
    result = get_element_info("Fire", lang="en")
    assert "enthusiasm" in result["description"]

def test_get_element_info_localized():
    with patch("app.engine.glossary.get_translation") as mock_trans:
        mock_trans.return_value = ["Pasion y energia"]
        result = get_element_info("Fire", lang="es")
        assert result["description"] == "Pasion y energia"

def test_search_glossary_en():
    results = search_glossary("Aries", lang="en")
    assert len(results) > 0
    assert results[0]["key"] == "Aries"

def test_search_glossary_localized():
    with patch("app.engine.glossary.get_translation") as mock_trans:
        # Mock translation for get_sign_info called inside search_glossary
        def side_effect(lang, key):
            if key == "glossary_zodiac_aries_desc":
                return ["Aries es el primer signo"]
            return None
        mock_trans.side_effect = side_effect
        
        results = search_glossary("Aries", lang="es")
        assert len(results) > 0
        # Check if the data inside result is localized
        aries_result = next((r for r in results if r["key"] == "Aries"), None)
        assert aries_result
        assert aries_result["data"]["description"] == "Aries es el primer signo"
