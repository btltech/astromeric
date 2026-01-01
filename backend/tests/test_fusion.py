import pytest
from unittest.mock import patch, MagicMock
from app.engine.fusion import fuse_prediction, _fuse_prediction

class TestFusion:
    def test_fuse_prediction_structure(self):
        result = fuse_prediction(
            name="John Doe",
            dob="1990-03-21",
            date="2023-10-27",
            scope="daily"
        )
        assert "tldr" in result
        assert "tracks" in result
        assert "love" in result["tracks"]
        assert "money" in result["tracks"]
        assert "ratings" in result
        assert "lucky" in result
        assert "theme_word" in result
        assert "advice" in result
        assert "affirmation" in result
        assert "daily_action" in result

    def test_fuse_prediction_content(self):
        result = fuse_prediction(
            name="John Doe",
            dob="1990-03-21",
            date="2023-10-27",
            scope="daily"
        )
        # Check if content is generated (not empty)
        assert len(result["tldr"]) > 0
        assert len(result["tracks"]["love"]) > 0
        assert len(result["theme_word"]) > 0

    def test_fuse_prediction_with_time_and_place(self):
        result = fuse_prediction(
            name="John Doe",
            dob="1990-03-21",
            date="2023-10-27",
            scope="daily",
            time_of_birth="12:00",
            place_of_birth="New York"
        )
        assert result["rising_sign"] is not None
        assert result["place_vibe"] is not None

class TestFusionLocalization:
    @patch('app.engine.fusion.get_translation')
    def test_fuse_prediction_localized(self, mock_get_translation):
        def side_effect(lang, category, key):
            if lang == "es":
                if category == "fusion_content":
                    if "theme_words" in key:
                        return "PalabraTema"
                    if "advice" in key:
                        return "Consejo"
                    if "affirmations" in key:
                        return "Afirmación"
                    if "daily_actions" in key:
                        return "Acción"
                    if "scope_daily" in key:
                        return "Resumen diario para {sign} con {element}"
                    if "track_love" in key:
                        return "Amor: {traits}"
                    if "track_money" in key:
                        return "Dinero: {traits}"
                    if "track_career" in key:
                        return "Carrera: {traits}"
                    if "track_health" in key:
                        return "Salud: {traits}"
                    if "track_spiritual" in key:
                        return "Espiritual: {traits}"
                if category == "elements" and key == "Fire":
                    return "Fuego"
                if category == "astrology_traits":
                    return "Rasgo"
            return None
        mock_get_translation.side_effect = side_effect
        
        result = fuse_prediction(
            name="John Doe",
            dob="1990-03-21",
            date="2023-10-27",
            scope="daily",
            lang="es"
        )
        
        assert result["theme_word"] == "PalabraTema"
        assert result["advice"] == "Consejo"
        assert result["affirmation"] == "Afirmación"
        assert result["daily_action"] == "Acción"
        assert result["element"] == "Fuego"
        assert "Resumen diario" in result["tldr"]
        assert "Fuego" in result["tldr"]

