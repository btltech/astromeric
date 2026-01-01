import pytest
from unittest.mock import patch, MagicMock
from app.engine.products.forecast import build_forecast
from app.engine.products.types import ProfileInput

class TestForecastProduct:
    def test_build_forecast_structure(self):
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060)
        forecast = build_forecast(profile, scope="daily", target_date="2023-10-27")
        
        assert "summary" in forecast
        assert "sections" in forecast
        assert len(forecast["sections"]) > 0
        assert "natal_chart" in forecast
        assert "transits" in forecast

    def test_build_forecast_content(self):
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060)
        forecast = build_forecast(profile, scope="daily", target_date="2023-10-27")
        
        # Check sections
        titles = [s["title"] for s in forecast["sections"]]
        assert "Overview" in titles
        assert "Love & Relationships" in titles
        assert "Work & Money" in titles

class TestForecastProductLocalization:
    @patch('app.engine.products.forecast.get_translation')
    def test_build_forecast_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es":
                if category == "forecast_sections":
                    if "overview" in key: return "Resumen"
                    if "love" in key: return "Amor"
                    if "career" in key: return "Trabajo"
                    if "emotional" in key: return "Emocional"
                    if "standout" in key: return "Transito Destacado"
                    if "numerology" in key: return "Numerologia"
                    if "actions" in key: return "Acciones"
                if category == "affirmations":
                    return "Afirmacion"
            return None
        mock_get_translation.side_effect = side_effect
        
        profile = ProfileInput(name="John", date_of_birth="1990-03-21", time_of_birth="12:00", latitude=40.7128, longitude=-74.0060, language="es")
        forecast = build_forecast(profile, scope="daily", target_date="2023-10-27")
        
        titles = [s["title"] for s in forecast["sections"]]
        assert "Resumen" in titles
        assert "Amor" in titles
        assert "Trabajo" in titles
        assert "Emocional" in titles
        assert "Transito Destacado" in titles
        assert "Numerologia" in titles
        assert "Acciones" in titles

