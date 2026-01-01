import pytest
from unittest.mock import Mock, patch
from app.engine.products.compatibility import build_compatibility_report
from app.engine.products.types import ProfileInput

class TestCompatibilityProduct:
    def test_build_compatibility_report_structure(self):
        person_a = ProfileInput(name="A", date_of_birth="1990-01-01", time_of_birth="12:00", latitude=0, longitude=0)
        person_b = ProfileInput(name="B", date_of_birth="1990-01-01", time_of_birth="12:00", latitude=0, longitude=0)
        
        result = build_compatibility_report(person_a, person_b)
        
        assert "relationship_type" in result
        assert "people" in result
        assert "synastry_aspects" in result
        assert "summary" in result
        assert "sections" in result
        assert "numerology" in result
        
        titles = [s["title"] for s in result["sections"]]
        assert "Relationship dynamics" in titles

class TestCompatibilityProductLocalization:
    @patch('app.engine.products.compatibility.get_translation')
    def test_build_compatibility_report_localized(self, mock_get_translation):
        def side_effect(lang, category, key=None):
            if lang == "es":
                if category == "compatibility_sections" and key == "relationship_dynamics":
                    return ["Dinamica de Relacion"]
            return None
        mock_get_translation.side_effect = side_effect
        
        person_a = ProfileInput(name="A", date_of_birth="1990-01-01", time_of_birth="12:00", latitude=0, longitude=0, language="es")
        person_b = ProfileInput(name="B", date_of_birth="1990-01-01", time_of_birth="12:00", latitude=0, longitude=0, language="es")
        
        # Note: build_compatibility_report takes explicit lang arg, doesn't infer from profile yet?
        # Let's check the signature. It takes lang="en" default.
        # So we must pass lang="es" explicitly.
        
        result = build_compatibility_report(person_a, person_b, lang="es")
        
        titles = [s["title"] for s in result["sections"]]
        assert "Dinamica de Relacion" in titles
