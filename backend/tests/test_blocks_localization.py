import pytest
from unittest.mock import patch, MagicMock
from app.engine.interpretation.blocks import get_meaning_block, MeaningBlock, PLANET_SIGN_MEANINGS, PLANET_HOUSE_MEANINGS, ASPECT_MEANINGS

class TestBlocksLocalization:
    @patch('app.engine.interpretation.blocks.get_planet_sign_text')
    def test_get_meaning_block_planet_sign_localized(self, mock_get_text):
        mock_get_text.return_value = "Sol en Aries (ES)"
        
        # Mock PLANET_SIGN_MEANINGS structure
        mock_block = MeaningBlock(text="Sun in Aries", tags=[], weights={})
        mock_dict = {"Sun": {"Aries": mock_block}}
        
        block = get_meaning_block(mock_dict, "Sun", "Aries", lang="es", context="planet_sign")
        
        assert block.text == "Sol en Aries (ES)"
        mock_get_text.assert_called_with("Sun", "Aries", "es")

    @patch('app.engine.interpretation.blocks.get_translation')
    def test_get_meaning_block_planet_house_localized(self, mock_get_translation):
        mock_get_translation.return_value = "Sol en Casa 1 (ES)"
        
        mock_block = MeaningBlock(text="Sun in House 1", tags=[], weights={})
        mock_dict = {"Sun": {1: mock_block}}
        
        block = get_meaning_block(mock_dict, "Sun", 1, lang="es", context="planet_house")
        
        assert block.text == "Sol en Casa 1 (ES)"
        mock_get_translation.assert_called_with("es", "planet_house_meanings", "Sun_house_1")

    @patch('app.engine.interpretation.blocks.get_translation')
    def test_get_meaning_block_aspect_localized(self, mock_get_translation):
        mock_get_translation.return_value = "Conjuncion (ES)"
        
        mock_block = MeaningBlock(text="Conjunction", tags=[], weights={})
        mock_dict = {"conjunction": mock_block}
        
        block = get_meaning_block(mock_dict, "conjunction", lang="es", context="aspect")
        
        assert block.text == "Conjuncion (ES)"
        mock_get_translation.assert_called_with("es", "aspect_meanings", "aspect_conjunction")
