import pytest
from unittest.mock import patch, MagicMock
from app.engine.guidance import (
    get_daily_guidance,
    _get_numerology_guidance,
    _get_astrology_guidance,
    _get_color_guidance,
    _calculate_power_hour,
    _get_current_hour_info
)

@pytest.fixture
def mock_natal_chart():
    return {
        "planets": [
            {"name": "Sun", "sign": "Aries", "house": 1},
            {"name": "Moon", "sign": "Taurus", "house": 2}
        ],
        "metadata": {
            "location": {"lat": 40.7128, "lon": -74.0060}
        }
    }

@pytest.fixture
def mock_transit_chart():
    return {
        "planets": [
            {"name": "Sun", "sign": "Leo"},
            {"name": "Moon", "sign": "Virgo"}
        ]
    }

def test_get_numerology_guidance_en():
    result = _get_numerology_guidance(1, lang="en")
    assert "avoid" in result
    assert "embrace" in result
    assert len(result["avoid"]) > 0
    assert len(result["embrace"]) > 0

def test_get_numerology_guidance_es_fallback():
    # Should fallback or return empty if no translation
    with patch("app.engine.guidance.get_translation") as mock_trans:
        mock_trans.return_value = ["Evitar esto"]
        result = _get_numerology_guidance(1, lang="es")
        assert result["avoid"] == ["Evitar esto"]

def test_get_astrology_guidance_en(mock_natal_chart, mock_transit_chart):
    result = _get_astrology_guidance(mock_natal_chart, mock_transit_chart, lang="en")
    assert isinstance(result, dict)
    # Virgo moon is Earth
    assert "Risky spending" in result["avoid"] or len(result["avoid"]) > 0

def test_get_color_guidance_en():
    result = _get_color_guidance(1, lang="en")
    assert "avoid" in result
    assert "embrace" in result
    assert isinstance(result["embrace"], list)
    if result["embrace"]:
        assert "name" in result["embrace"][0]
        assert "hex" in result["embrace"][0]

def test_calculate_power_hour_en(mock_natal_chart, mock_transit_chart):
    with patch("app.engine.guidance.get_power_hours") as mock_ph:
        mock_ph.return_value = [
            {"planet": "Sun", "start": "10:00", "end": "11:00", "is_day": True}
        ]
        result = _calculate_power_hour(
            mock_natal_chart, 
            mock_transit_chart, 
            latitude=40.7, 
            longitude=-74.0,
            lang="en"
        )
        assert "10:00 - 11:00" in result
        assert "Sun" in result

def test_get_current_hour_info_en():
    with patch("app.engine.guidance.get_current_planetary_hour") as mock_ph:
        mock_ph.return_value = {
            "planet": "Sun",
            "start": "10:00",
            "end": "11:00"
        }
        result = _get_current_hour_info(40.7, -74.0, "UTC", lang="en")
        assert result["planet"] == "Sun"
        assert result["quality"] == "Favorable"

def test_get_daily_guidance_integration(mock_natal_chart, mock_transit_chart):
    # Mock all internal calls to avoid complex setup
    with patch("app.engine.guidance._get_numerology_guidance") as mock_num, \
         patch("app.engine.guidance._get_astrology_guidance") as mock_astro, \
         patch("app.engine.guidance._get_color_guidance") as mock_color, \
         patch("app.engine.guidance._calculate_power_hour") as mock_power, \
         patch("app.engine.guidance._get_current_hour_info") as mock_hour:
        
        mock_num.return_value = {"avoid": [], "embrace": []}
        mock_astro.return_value = {"avoid": [], "embrace": []}
        mock_color.return_value = {"avoid": [], "embrace": []}
        mock_power.return_value = "10:00 - 11:00"
        mock_hour.return_value = {"planet": "Sun"}
        
        result = get_daily_guidance(
            mock_natal_chart,
            mock_transit_chart,
            numerology=1,
            latitude=40.7,
            longitude=-74.0,
            lang="es"
        )
        
        assert "avoid" in result
        assert "embrace" in result
        assert "current_planetary_hour" in result
        
        # Verify lang was passed down
        mock_num.assert_called_with(1, lang="es")
        mock_astro.assert_called_with(mock_natal_chart, mock_transit_chart, lang="es")
        mock_color.assert_called_with(1, lang="es")
        mock_power.assert_called_with(mock_natal_chart, mock_transit_chart, 40.7, -74.0, "UTC", lang="es")
        mock_hour.assert_called_with(40.7, -74.0, "UTC", "es")
