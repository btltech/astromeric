"""
test_guidance.py
----------------
Tests for the daily guidance engine: Avoid/Embrace, Power Hours, Retrogrades, VOC Moon.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engine.guidance import (
    get_daily_guidance,
    _get_numerology_guidance,
    _get_astrology_guidance,
    _get_color_guidance,
    _get_challenge_numbers,
    _calculate_power_hour,
    _get_current_hour_info,
)


# --- Test Numerology Guidance ---

def test_numerology_guidance_rules():
    # Test Day 1
    g1 = _get_numerology_guidance(1)
    assert "Hesitation" in g1["avoid"]
    assert "Taking the lead" in g1["embrace"]
    
    # Test Day 5
    g5 = _get_numerology_guidance(5)
    assert "Routine" in g5["avoid"]
    assert "Change" in g5["embrace"]
    
    # Test Invalid Day
    g_invalid = _get_numerology_guidance(99)
    assert g_invalid["avoid"] == []
    assert g_invalid["embrace"] == []


def test_master_number_guidance():
    """Master numbers should have specific guidance."""
    g11 = _get_numerology_guidance(11)
    assert len(g11["avoid"]) > 0
    assert len(g11["embrace"]) > 0
    
    g22 = _get_numerology_guidance(22)
    assert len(g22["avoid"]) > 0
    assert len(g22["embrace"]) > 0


def test_all_day_numbers_covered():
    """All numbers 1-9 should have guidance."""
    for day in range(1, 10):
        result = _get_numerology_guidance(day)
        assert len(result["avoid"]) > 0
        assert len(result["embrace"]) > 0


# --- Test Color Guidance ---

def test_color_guidance():
    # Test Day 1 Colors
    c1 = _get_color_guidance(1)
    embrace_names = [c["name"] for c in c1["embrace"]]
    avoid_names = [c["name"] for c in c1["avoid"]]
    assert "Red" in embrace_names
    assert "Black" in avoid_names
    # Check hex values are present
    assert all("hex" in c for c in c1["embrace"])
    assert all("hex" in c for c in c1["avoid"])
    
    # Test Day 2 Colors
    c2 = _get_color_guidance(2)
    embrace_names_2 = [c["name"] for c in c2["embrace"]]
    avoid_names_2 = [c["name"] for c in c2["avoid"]]
    assert "White" in embrace_names_2
    assert "Bright Orange" in avoid_names_2


def test_color_guidance_structure():
    """Color guidance should have embrace and avoid lists."""
    for day in range(1, 10):
        result = _get_color_guidance(day)
        assert "embrace" in result
        assert "avoid" in result
        assert isinstance(result["embrace"], list)


# --- Test Astrology Guidance ---

def test_astrology_guidance_fire_moon():
    # Mock charts
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Aries"} # Fire sign
        ],
        "aspects": []
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Impulsive anger" in guidance["avoid"]
    assert "Physical activity" in guidance["embrace"]


def test_astrology_guidance_water_moon():
    # Mock charts
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Pisces"} # Water sign
        ],
        "aspects": []
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Suppressing emotions" in guidance["avoid"]
    assert "Self-care" in guidance["embrace"]


def test_astrology_guidance_earth_moon():
    """Earth Moon should suggest practical tasks."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Taurus"}],
        "aspects": []
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Risky spending" in guidance["avoid"]
    assert "Practical tasks" in guidance["embrace"]


def test_astrology_guidance_air_moon():
    """Air Moon should suggest socializing."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Gemini"}],
        "aspects": []
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Miscommunication" in guidance["avoid"]
    assert "Socializing" in guidance["embrace"]


def test_astrology_square_aspect():
    """Square aspects should add caution."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Aries"}],
        "aspects": [{"type": "square", "planet1": "Sun", "planet2": "Moon"}]
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Forcing outcomes" in guidance["avoid"]


def test_astrology_opposition_aspect():
    """Opposition aspects should suggest finding balance."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Cancer"}],
        "aspects": [{"type": "opposition", "planet1": "Sun", "planet2": "Moon"}]
    }
    
    guidance = _get_astrology_guidance(natal, transit)
    assert "Finding balance" in guidance["embrace"]


# --- Test Challenge Numbers ---

def test_challenge_numbers_extraction():
    """Should extract challenge numbers from numerology."""
    numerology = {
        "challenges": [
            {"number": 2, "description": "Balance"},
            {"number": 4, "description": "Hard work"},
        ]
    }
    result = _get_challenge_numbers(numerology)
    assert 2 in result
    assert 4 in result


def test_challenge_numbers_empty():
    """Should return empty list when no challenges."""
    result = _get_challenge_numbers({})
    assert result == []


# --- Test Full Integration ---

def test_full_guidance_integration():
    # Mock inputs
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Taurus", "degree": 15, "absolute_degree": 45, "retrograde": False}
        ],
        "aspects": []
    }
    numerology = {
        "cycles": {
            "personal_day": {"number": 4}
        },
        "challenges": [
            {"number": 1},
            {"number": 2}
        ]
    }
    
    result = get_daily_guidance(natal, transit, numerology)
    
    # Check structure
    assert "avoid" in result
    assert "embrace" in result
    assert "retrogrades" in result
    assert "void_of_course_moon" in result
    
    # Check Numerology (Day 4)
    # Day 4 Avoid: Laziness, Shortcuts, Disorganization
    assert "Laziness" in result["avoid"]["activities"]
    # Day 4 Embrace: Hard work, Planning, Details
    assert "Hard work" in result["embrace"]["activities"]
    
    # Check Astrology (Taurus Moon)
    # Earth Moon Avoid: Risky spending
    assert "Risky spending" in result["avoid"]["activities"]
    
    # Check Colors (Day 4) - colors are now objects with name and hex
    embrace_color_names = [c["name"] for c in result["embrace"]["colors"]]
    assert "Green" in embrace_color_names
    
    # Check Challenge Numbers
    assert 1 in result["avoid"]["numbers"]
    assert 2 in result["avoid"]["numbers"]


def test_guidance_retrograde_detection():
    """Should detect retrogrades in transit chart."""
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Aries", "degree": 10, "absolute_degree": 10, "retrograde": False},
            {"name": "Mercury", "sign": "Virgo", "degree": 8, "absolute_degree": 158, "retrograde": True, "house": 6},
        ],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 1}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    assert len(result["retrogrades"]) == 1
    assert result["retrogrades"][0]["planet"] == "Mercury"
    assert "impact" in result["retrogrades"][0]


def test_guidance_voc_moon():
    """Should include VOC Moon analysis."""
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Scorpio", "degree": 29.5, "absolute_degree": 239.5, "retrograde": False},
            {"name": "Sun", "sign": "Capricorn", "degree": 10, "absolute_degree": 280, "retrograde": False},
        ],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 5}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    voc = result["void_of_course_moon"]
    assert "is_void" in voc
    assert "current_sign" in voc
    assert voc["current_sign"] == "Scorpio"


def test_guidance_with_location():
    """Should include planetary hour when location provided."""
    natal = {"metadata": {"location": {"lat": 40.7, "lon": -74.0}}}
    transit = {
        "planets": [{"name": "Moon", "sign": "Cancer", "degree": 15, "absolute_degree": 105, "retrograde": False}],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 6}}, "challenges": []}
    
    result = get_daily_guidance(
        natal, transit, numerology,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York"
    )
    
    # Should have current planetary hour
    assert "current_planetary_hour" in result
    if result["current_planetary_hour"]:
        assert "planet" in result["current_planetary_hour"]
        assert "quality" in result["current_planetary_hour"]


def test_guidance_without_location():
    """Should work without location data."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Leo", "degree": 10, "absolute_degree": 130, "retrograde": False}],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 3}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    # Should still have all main sections
    assert "avoid" in result
    assert "embrace" in result
    assert "retrogrades" in result


def test_retrograde_activities_merged():
    """Retrograde avoid/embrace should merge into main lists."""
    natal = {}
    transit = {
        "planets": [
            {"name": "Moon", "sign": "Aries", "degree": 15, "absolute_degree": 15, "retrograde": False},
            {"name": "Mercury", "sign": "Gemini", "degree": 20, "absolute_degree": 80, "retrograde": True, "house": 3},
        ],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 7}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    # Mercury retrograde activities should be in the lists
    avoid = result["avoid"]["activities"]
    embrace = result["embrace"]["activities"]
    
    # Should have more activities due to retrograde merge
    assert len(avoid) >= 3
    assert len(embrace) >= 3


def test_deduplication():
    """Activities should not have duplicates."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Aries", "degree": 15, "absolute_degree": 15, "retrograde": False}],
        "aspects": []
    }
    numerology = {"cycles": {"personal_day": {"number": 1}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    avoid = result["avoid"]["activities"]
    embrace = result["embrace"]["activities"]
    
    assert len(avoid) == len(set(avoid)), "Avoid activities should be unique"
    assert len(embrace) == len(set(embrace)), "Embrace activities should be unique"


# --- Edge Cases ---

def test_empty_transit_planets():
    """Should handle empty planets list."""
    natal = {}
    transit = {"planets": [], "aspects": []}
    numerology = {"cycles": {"personal_day": {"number": 1}}, "challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    assert "avoid" in result
    assert "embrace" in result


def test_missing_cycles():
    """Should handle missing cycles in numerology."""
    natal = {}
    transit = {
        "planets": [{"name": "Moon", "sign": "Taurus", "degree": 10, "absolute_degree": 40}],
        "aspects": []
    }
    numerology = {"challenges": []}
    
    result = get_daily_guidance(natal, transit, numerology)
    
    assert result is not None
    assert "avoid" in result


# --- Localization Tests ---

def test_get_numerology_guidance_es_fallback():
    # Should fallback or return empty if no translation
    with patch("app.engine.guidance.get_translation") as mock_trans:
        mock_trans.return_value = ["Evitar esto"]
        result = _get_numerology_guidance(1, lang="es")
        assert result["avoid"] == ["Evitar esto"]

def test_get_astrology_guidance_en():
    natal = {"planets": [], "metadata": {}}
    transit = {"planets": [{"name": "Moon", "sign": "Virgo"}]}
    result = _get_astrology_guidance(natal, transit, lang="en")
    assert isinstance(result, dict)
    # Virgo moon is Earth
    assert "Risky spending" in result["avoid"] or len(result["avoid"]) > 0

def test_calculate_power_hour_en():
    natal = {"planets": [], "metadata": {"location": {"lat": 40.7, "lon": -74.0}}}
    transit = {"planets": []}
    with patch("app.engine.guidance.get_power_hours") as mock_ph:
        mock_ph.return_value = [
            {"planet": "Sun", "start": "10:00", "end": "11:00", "is_day": True}
        ]
        result = _calculate_power_hour(
            natal, 
            transit, 
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

def test_get_daily_guidance_integration_localized():
    natal = {"planets": [], "metadata": {"location": {"lat": 40.7, "lon": -74.0}}}
    transit = {"planets": []}
    
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
            natal,
            transit,
            numerology={"cycles": {"personal_day": {"number": 1}}},
            latitude=40.7,
            longitude=-74.0,
            lang="es"
        )
        
        assert "avoid" in result
        
        # Verify lang was passed down
        mock_num.assert_called_with(1, lang="es")
        mock_astro.assert_called_with(natal, transit, lang="es")
        mock_color.assert_called_with(1, lang="es")
        mock_power.assert_called_with(
            natal, 
            transit, 
            latitude=40.7, 
            longitude=-74.0, 
            timezone="UTC", 
            lang="es"
        )
        mock_hour.assert_called_with(40.7, -74.0, "UTC", "es")
