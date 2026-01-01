import pytest
from unittest.mock import patch, MagicMock
from app.engine.products.natal import build_natal_profile
from app.engine.products.types import ProfileInput

class TestNatalProduct:
    def test_build_natal_profile_structure(self):
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060)
        result = build_natal_profile(profile)
        
        assert "profile" in result
        assert "chart" in result
        assert "sections" in result
        assert "numerology" in result
        assert len(result["sections"]) == 3

    def test_build_natal_profile_content(self):
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060)
        result = build_natal_profile(profile)
        
        titles = [s["title"] for s in result["sections"]]
        assert "General personality" in titles
        assert "Love & relationships" in titles
        assert "Career & direction" in titles

class TestNatalProductLocalization:
    @patch('app.engine.products.natal.get_translation')
    def test_build_natal_profile_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es":
                if category == "natal_sections":
                    if "general" in key: return "Personalidad General"
                    if "love" in key: return "Amor y Relaciones"
                    if "career" in key: return "Carrera y Direccion"
                if category == "numerology_labels":
                    if "life_path" in key: return "Camino de Vida"
            return None
        mock_get_translation.side_effect = side_effect
        
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060, language="es")
        result = build_natal_profile(profile)
        
        titles = [s["title"] for s in result["sections"]]
        assert "Personalidad General" in titles
        assert "Amor y Relaciones" in titles
        assert "Carrera y Direccion" in titles
        
        assert result["numerology"]["life_path"]["label"] == "Camino de Vida"

