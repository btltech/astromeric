import pytest
from unittest.mock import patch, MagicMock
from app.engine.rules.engine import RuleEngine, Chart, Factor
from app.engine.charts.models import PlanetPosition, Aspect

class TestRulesEngineLocalization:
    @patch('app.engine.rules.engine.get_meaning_block')
    def test_evaluate_localized(self, mock_get_meaning_block):
        # Setup mock meaning block
        mock_meaning = MagicMock()
        mock_meaning.weights = {"general": 1.0}
        mock_get_meaning_block.return_value = mock_meaning
        
        engine = RuleEngine()
        chart = MagicMock(spec=Chart)
        chart.planets = [
            PlanetPosition(name="Sun", sign="Aries", degree=0, absolute_degree=0, house=1)
        ]
        chart.aspects = []
        
        result = engine.evaluate("general", chart, lang="es")
        
        # Verify get_meaning_block was called with lang="es"
        # It should be called for planet sign and planet house
        calls = mock_get_meaning_block.call_args_list
        
        # Check for planet sign call
        # args: (PLANET_SIGN_MEANINGS, "Sun", "Aries") kwargs: {lang="es", context="planet_sign"}
        found_sign = False
        for call in calls:
            args, kwargs = call
            if args[1] == "Sun" and args[2] == "Aries" and kwargs.get("lang") == "es" and kwargs.get("context") == "planet_sign":
                found_sign = True
                break
        assert found_sign
        
        # Check for planet house call
        found_house = False
        for call in calls:
            args, kwargs = call
            if args[1] == "Sun" and args[2] == 1 and kwargs.get("lang") == "es" and kwargs.get("context") == "planet_house":
                found_house = True
                break
        assert found_house

    @patch('app.engine.rules.engine.get_meaning_block')
    def test_aspect_factors_localized(self, mock_get_meaning_block):
        mock_meaning = MagicMock()
        mock_meaning.weights = {"general": 1.0}
        mock_get_meaning_block.return_value = mock_meaning
        
        engine = RuleEngine()
        aspects = [Aspect(planet_a="Sun", planet_b="Moon", aspect_type="conjunction", orb=1.0, strength_score=10.0)]
        
        factors = engine._aspect_factors(aspects, "natal", lang="es")
        
        # Verify call
        args, kwargs = mock_get_meaning_block.call_args
        assert args[1] == "conjunction"
        assert kwargs["lang"] == "es"
        assert kwargs["context"] == "aspect"

    @patch('app.engine.rules.engine.get_meaning_block')
    def test_numerology_factors_localized(self, mock_get_meaning_block):
        mock_meaning = MagicMock()
        mock_meaning.weights = {"general": 1.0}
        mock_get_meaning_block.return_value = mock_meaning
        
        engine = RuleEngine()
        numerology = {"life_path": {"number": 7}}
        
        factors = engine._numerology_factors(numerology, lang="es")
        
        # Verify call
        args, kwargs = mock_get_meaning_block.call_args
        assert args[1] == "life_path"
        assert kwargs["lang"] == "es"
        assert kwargs["context"] == "numerology_type"
