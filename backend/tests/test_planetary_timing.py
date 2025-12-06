"""
test_planetary_timing.py
------------------------
Tests for the planetary timing module: Power Hours, Retrogrades, VOC Moon.
"""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from app.engine.planetary_timing import (
    CHALDEAN_ORDER,
    DAY_RULERS,
    calculate_sunrise_sunset,
    calculate_planetary_hours,
    get_current_planetary_hour,
    get_power_hours,
    detect_retrogrades,
    calculate_void_of_course_moon,
)


# --- Fixtures ---

@pytest.fixture
def sample_location():
    """New York City coordinates."""
    return {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    }


@pytest.fixture
def sample_transit_chart_with_retrogrades():
    """Transit chart with Mercury and Venus retrograde."""
    return {
        "planets": [
            {"name": "Sun", "sign": "Leo", "degree": 15.5, "absolute_degree": 135.5, "retrograde": False, "house": 10},
            {"name": "Moon", "sign": "Taurus", "degree": 22.3, "absolute_degree": 52.3, "retrograde": False, "house": 7},
            {"name": "Mercury", "sign": "Virgo", "degree": 8.2, "absolute_degree": 158.2, "retrograde": True, "house": 11},
            {"name": "Venus", "sign": "Leo", "degree": 28.9, "absolute_degree": 148.9, "retrograde": True, "house": 10},
            {"name": "Mars", "sign": "Gemini", "degree": 12.1, "absolute_degree": 72.1, "retrograde": False, "house": 8},
            {"name": "Jupiter", "sign": "Taurus", "degree": 5.4, "absolute_degree": 35.4, "retrograde": False, "house": 7},
            {"name": "Saturn", "sign": "Pisces", "degree": 18.7, "absolute_degree": 348.7, "retrograde": False, "house": 5},
        ],
        "aspects": [],
    }


@pytest.fixture
def sample_transit_chart_no_retrogrades():
    """Transit chart with no retrogrades."""
    return {
        "planets": [
            {"name": "Sun", "sign": "Aries", "degree": 10.0, "absolute_degree": 10.0, "retrograde": False, "house": 1},
            {"name": "Moon", "sign": "Cancer", "degree": 15.0, "absolute_degree": 105.0, "retrograde": False, "house": 4},
            {"name": "Mercury", "sign": "Aries", "degree": 5.0, "absolute_degree": 5.0, "retrograde": False, "house": 1},
            {"name": "Venus", "sign": "Taurus", "degree": 20.0, "absolute_degree": 50.0, "retrograde": False, "house": 2},
        ],
        "aspects": [],
    }


@pytest.fixture
def sample_transit_chart_voc_moon():
    """Transit chart with Moon in late degree (potentially VOC)."""
    return {
        "planets": [
            {"name": "Sun", "sign": "Capricorn", "degree": 10.0, "absolute_degree": 280.0, "retrograde": False},
            {"name": "Moon", "sign": "Scorpio", "degree": 29.5, "absolute_degree": 239.5, "retrograde": False},  # Late degree
            {"name": "Mercury", "sign": "Capricorn", "degree": 15.0, "absolute_degree": 285.0, "retrograde": False},
            {"name": "Venus", "sign": "Aquarius", "degree": 5.0, "absolute_degree": 305.0, "retrograde": False},
            {"name": "Mars", "sign": "Sagittarius", "degree": 20.0, "absolute_degree": 260.0, "retrograde": False},
        ],
        "aspects": [],
    }


@pytest.fixture
def sample_transit_chart_active_moon():
    """Transit chart with active Moon (early degree, many aspects)."""
    return {
        "planets": [
            {"name": "Sun", "sign": "Aries", "degree": 15.0, "absolute_degree": 15.0, "retrograde": False},
            {"name": "Moon", "sign": "Aries", "degree": 10.0, "absolute_degree": 10.0, "retrograde": False},  # Early degree, conjunct Sun
            {"name": "Mercury", "sign": "Aries", "degree": 12.0, "absolute_degree": 12.0, "retrograde": False},
            {"name": "Venus", "sign": "Taurus", "degree": 10.0, "absolute_degree": 40.0, "retrograde": False},  # Sextile Moon
        ],
        "aspects": [],
    }


# --- Test Chaldean Order ---

class TestChaldeanOrder:
    """Tests for planetary hours Chaldean order."""
    
    def test_chaldean_order_length(self):
        """Chaldean order should have 7 planets."""
        assert len(CHALDEAN_ORDER) == 7
    
    def test_chaldean_order_contents(self):
        """Chaldean order should include all classical planets."""
        expected = {"Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"}
        assert set(CHALDEAN_ORDER) == expected
    
    def test_chaldean_order_sequence(self):
        """Chaldean order should start with Saturn."""
        assert CHALDEAN_ORDER[0] == "Saturn"
        assert CHALDEAN_ORDER[3] == "Sun"
        assert CHALDEAN_ORDER[6] == "Moon"
    
    def test_day_rulers_complete(self):
        """Day rulers should cover all 7 days."""
        assert len(DAY_RULERS) == 7
        for i in range(7):
            assert i in DAY_RULERS


# --- Test Sunrise/Sunset Calculation ---

class TestSunriseSunset:
    """Tests for sunrise/sunset calculations."""
    
    def test_calculate_sunrise_sunset_returns_tuple(self, sample_location):
        """Should return a tuple of two datetimes."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        result = calculate_sunrise_sunset(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], datetime)
        assert isinstance(result[1], datetime)
    
    def test_sunrise_before_sunset(self, sample_location):
        """Sunrise should be before sunset."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        sunrise, sunset = calculate_sunrise_sunset(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert sunrise < sunset


# --- Test Planetary Hours Calculation ---

class TestPlanetaryHours:
    """Tests for planetary hours calculation."""
    
    def test_calculate_planetary_hours_returns_24(self, sample_location):
        """Should return exactly 24 planetary hours."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        hours = calculate_planetary_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert len(hours) == 24
    
    def test_planetary_hours_structure(self, sample_location):
        """Each planetary hour should have required fields."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        hours = calculate_planetary_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        
        for hour in hours:
            assert "hour_number" in hour
            assert "planet" in hour
            assert "start" in hour
            assert "end" in hour
            assert "is_day" in hour
            assert hour["planet"] in CHALDEAN_ORDER
    
    def test_12_day_hours_12_night_hours(self, sample_location):
        """Should have 12 day hours and 12 night hours."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        hours = calculate_planetary_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        
        day_hours = [h for h in hours if h["is_day"]]
        night_hours = [h for h in hours if not h["is_day"]]
        
        assert len(day_hours) == 12
        assert len(night_hours) == 12
    
    def test_sunday_starts_with_sun(self, sample_location):
        """Sunday's first planetary hour should be ruled by Sun."""
        # June 23, 2024 is a Sunday
        date = datetime(2024, 6, 23, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        hours = calculate_planetary_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert hours[0]["planet"] == "Sun"
    
    def test_saturday_starts_with_saturn(self, sample_location):
        """Saturday's first planetary hour should be ruled by Saturn."""
        # June 22, 2024 is a Saturday
        date = datetime(2024, 6, 22, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        hours = calculate_planetary_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert hours[0]["planet"] == "Saturn"


# --- Test Current Planetary Hour ---

class TestCurrentPlanetaryHour:
    """Tests for getting current planetary hour."""
    
    def test_get_current_planetary_hour_returns_dict(self, sample_location):
        """Should return a dictionary with planet info."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        result = get_current_planetary_hour(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        
        assert isinstance(result, dict)
        assert "planet" in result
        assert "start" in result
        assert "end" in result
        assert "is_day" in result
    
    def test_current_hour_planet_in_chaldean_order(self, sample_location):
        """Returned planet should be from Chaldean order."""
        date = datetime(2024, 6, 21, 14, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        result = get_current_planetary_hour(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert result["planet"] in CHALDEAN_ORDER


# --- Test Power Hours ---

class TestPowerHours:
    """Tests for power hours (favorable planetary hours)."""
    
    def test_get_power_hours_default_planets(self, sample_location):
        """Should return only Sun, Jupiter, Venus hours by default."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        power_hours = get_power_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        
        for ph in power_hours:
            assert ph["planet"] in ["Sun", "Jupiter", "Venus"]
    
    def test_get_power_hours_custom_planets(self, sample_location):
        """Should filter by custom favorable planets."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        power_hours = get_power_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"],
            favorable_planets=["Moon", "Mercury"]
        )
        
        for ph in power_hours:
            assert ph["planet"] in ["Moon", "Mercury"]
    
    def test_power_hours_structure(self, sample_location):
        """Power hours should have proper structure."""
        date = datetime(2024, 6, 21, 12, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        power_hours = get_power_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        
        for ph in power_hours:
            assert "planet" in ph
            assert "start" in ph
            assert "end" in ph


# --- Test Retrograde Detection ---

class TestRetrogrades:
    """Tests for retrograde detection."""
    
    def test_detect_retrogrades_with_retrogrades(self, sample_transit_chart_with_retrogrades):
        """Should detect Mercury and Venus retrograde."""
        retrogrades = detect_retrogrades(sample_transit_chart_with_retrogrades)
        
        assert len(retrogrades) == 2
        planets = [r["planet"] for r in retrogrades]
        assert "Mercury" in planets
        assert "Venus" in planets
    
    def test_detect_retrogrades_no_retrogrades(self, sample_transit_chart_no_retrogrades):
        """Should return empty list when no retrogrades."""
        retrogrades = detect_retrogrades(sample_transit_chart_no_retrogrades)
        assert len(retrogrades) == 0
    
    def test_retrograde_structure(self, sample_transit_chart_with_retrogrades):
        """Retrograde info should have required fields."""
        retrogrades = detect_retrogrades(sample_transit_chart_with_retrogrades)
        
        for retro in retrogrades:
            assert "planet" in retro
            assert "sign" in retro
            assert "general_impact" in retro
            assert "activities_avoid" in retro
            assert "activities_embrace" in retro
    
    def test_retrograde_has_house_impact(self, sample_transit_chart_with_retrogrades):
        """Retrogrades with house info should have house impact."""
        retrogrades = detect_retrogrades(sample_transit_chart_with_retrogrades)
        
        for retro in retrogrades:
            assert "house" in retro
            assert "house_impact" in retro
    
    def test_mercury_retrograde_specific_impacts(self, sample_transit_chart_with_retrogrades):
        """Mercury retrograde should have specific known impacts."""
        retrogrades = detect_retrogrades(sample_transit_chart_with_retrogrades)
        mercury = next(r for r in retrogrades if r["planet"] == "Mercury")
        
        assert "Communication" in mercury["general_impact"] or "delays" in mercury["general_impact"]
        assert len(mercury["activities_avoid"]) > 0


# --- Test Void-of-Course Moon ---

class TestVoidOfCourseMoon:
    """Tests for void-of-course Moon detection."""
    
    def test_voc_moon_structure(self, sample_transit_chart_voc_moon):
        """VOC Moon result should have required fields."""
        result = calculate_void_of_course_moon(sample_transit_chart_voc_moon)
        
        assert "is_void" in result
        assert "current_sign" in result
        assert "advice" in result
    
    def test_voc_moon_late_degree_detected(self, sample_transit_chart_voc_moon):
        """Moon in late degree should potentially be detected as VOC."""
        result = calculate_void_of_course_moon(sample_transit_chart_voc_moon)
        
        # Moon at 29.5 Scorpio with no close aspects should be VOC
        assert result["moon_degree"] == 29.5
        assert result["current_sign"] == "Scorpio"
    
    def test_active_moon_not_voc(self, sample_transit_chart_active_moon):
        """Moon in early degree with aspects should not be VOC."""
        result = calculate_void_of_course_moon(sample_transit_chart_active_moon)
        
        # Moon at 10 degrees with applying aspects should not be VOC
        assert result["is_void"] is False
        assert "active" in result["advice"].lower()
    
    def test_voc_moon_next_sign(self, sample_transit_chart_voc_moon):
        """VOC Moon should indicate next sign."""
        result = calculate_void_of_course_moon(sample_transit_chart_voc_moon)
        
        # After Scorpio comes Sagittarius
        assert result["next_sign"] == "Sagittarius"
    
    def test_voc_moon_hours_until_change(self, sample_transit_chart_voc_moon):
        """If VOC, should estimate hours until sign change."""
        result = calculate_void_of_course_moon(sample_transit_chart_voc_moon)
        
        if result["is_void"]:
            assert "hours_until_sign_change" in result
            assert result["hours_until_sign_change"] is not None
    
    def test_voc_moon_missing_moon(self):
        """Should handle chart with no Moon gracefully."""
        chart = {"planets": [{"name": "Sun", "sign": "Aries"}]}
        result = calculate_void_of_course_moon(chart)
        
        assert result["is_void"] is False
        assert result["current_sign"] == "Unknown"


# --- Integration Tests ---

class TestPlanetaryTimingIntegration:
    """Integration tests combining multiple functions."""
    
    def test_full_timing_calculation(self, sample_location, sample_transit_chart_with_retrogrades):
        """Test full timing calculation workflow."""
        date = datetime(2024, 6, 21, 14, 0, tzinfo=ZoneInfo(sample_location["timezone"]))
        
        # Get current hour
        current_hour = get_current_planetary_hour(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert current_hour["planet"] in CHALDEAN_ORDER
        
        # Get power hours
        power_hours = get_power_hours(
            date,
            sample_location["latitude"],
            sample_location["longitude"],
            sample_location["timezone"]
        )
        assert len(power_hours) > 0
        
        # Detect retrogrades
        retrogrades = detect_retrogrades(sample_transit_chart_with_retrogrades)
        assert len(retrogrades) == 2
        
        # Check VOC Moon
        voc = calculate_void_of_course_moon(sample_transit_chart_with_retrogrades)
        assert "is_void" in voc
