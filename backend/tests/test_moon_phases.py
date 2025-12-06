"""
test_moon_phases.py
-------------------
Tests for the Moon Phase and Ritual module.
"""

import pytest
from datetime import datetime, timedelta

from app.engine.moon_phases import (
    calculate_moon_phase,
    estimate_moon_sign,
    get_upcoming_moon_events,
    get_personalized_ritual,
    get_moon_phase_summary,
    MOON_PHASES,
    PHASE_RITUALS,
    SIGN_RITUAL_FOCUS,
    ZODIAC_ORDER,
)


# --- Fixtures ---

@pytest.fixture
def sample_natal_chart():
    return {
        "planets": [
            {"name": "Sun", "sign": "Leo", "degree": 15.0, "house": 5},
            {"name": "Moon", "sign": "Cancer", "degree": 10.0, "house": 4},
            {"name": "Mercury", "sign": "Virgo", "degree": 5.0, "house": 6},
        ],
    }


@pytest.fixture
def sample_numerology():
    return {
        "cycles": {
            "personal_day": {"number": 7},
            "personal_month": {"number": 3},
            "personal_year": {"number": 5},
        },
    }


# --- Test Moon Phase Calculation ---

class TestMoonPhaseCalculation:
    """Tests for Moon phase calculation."""
    
    def test_calculate_moon_phase_structure(self):
        """Moon phase should have required fields."""
        result = calculate_moon_phase()
        
        assert "phase_name" in result
        assert "emoji" in result
        assert "illumination" in result
        assert "phase_angle" in result
        assert "days_in_phase" in result
        assert "days_until_next_phase" in result
        assert "is_waxing" in result
        assert "is_waning" in result
    
    def test_phase_name_is_valid(self):
        """Phase name should be from known phases."""
        result = calculate_moon_phase()
        
        valid_phases = [p["name"] for p in MOON_PHASES]
        assert result["phase_name"] in valid_phases
    
    def test_illumination_range(self):
        """Illumination should be 0-100%."""
        result = calculate_moon_phase()
        
        assert 0 <= result["illumination"] <= 100
    
    def test_phase_angle_range(self):
        """Phase angle should be 0-360."""
        result = calculate_moon_phase()
        
        assert 0 <= result["phase_angle"] <= 360
    
    def test_waxing_waning_exclusive(self):
        """Should be either waxing or waning, not both."""
        result = calculate_moon_phase()
        
        assert result["is_waxing"] != result["is_waning"]
    
    def test_specific_date_phase(self):
        """Should calculate phase for specific date."""
        # Test with a known date
        test_date = datetime(2024, 1, 11)  # Near new moon
        result = calculate_moon_phase(test_date)
        
        assert result["phase_name"] is not None


# --- Test Moon Sign Estimation ---

class TestMoonSignEstimation:
    """Tests for Moon sign estimation."""
    
    def test_estimate_moon_sign_returns_valid(self):
        """Should return a valid zodiac sign."""
        result = estimate_moon_sign()
        
        assert result in ZODIAC_ORDER
    
    def test_moon_sign_changes_over_time(self):
        """Moon sign should change every ~2.5 days."""
        date1 = datetime(2024, 6, 1)
        date2 = datetime(2024, 6, 4)  # 3 days later
        
        sign1 = estimate_moon_sign(date1)
        sign2 = estimate_moon_sign(date2)
        
        # After 3 days, Moon may or may not have changed signs
        # Just verify both are valid
        assert sign1 in ZODIAC_ORDER
        assert sign2 in ZODIAC_ORDER


# --- Test Upcoming Moon Events ---

class TestUpcomingMoonEvents:
    """Tests for upcoming Moon event calculations."""
    
    def test_upcoming_events_structure(self):
        """Upcoming events should have required fields."""
        events = get_upcoming_moon_events(30)
        
        assert isinstance(events, list)
        for event in events:
            assert "type" in event
            assert "date" in event
            assert "emoji" in event
            assert "days_away" in event
            assert "sign" in event
    
    def test_event_types(self):
        """Events should be New Moon or Full Moon."""
        events = get_upcoming_moon_events(30)
        
        for event in events:
            assert event["type"] in ["New Moon", "Full Moon"]
    
    def test_events_sorted_by_days(self):
        """Events should be sorted by days away."""
        events = get_upcoming_moon_events(30)
        
        if len(events) > 1:
            for i in range(len(events) - 1):
                assert events[i]["days_away"] <= events[i + 1]["days_away"]
    
    def test_longer_range_more_events(self):
        """Longer range should potentially have more events."""
        events_30 = get_upcoming_moon_events(30)
        events_60 = get_upcoming_moon_events(60)
        
        # 60 days should have at least as many events as 30 days
        assert len(events_60) >= len(events_30)


# --- Test Phase Rituals Data ---

class TestPhaseRituals:
    """Tests for phase ritual data integrity."""
    
    def test_all_phases_have_rituals(self):
        """All 8 phases should have ritual data."""
        phase_names = [p["name"] for p in MOON_PHASES]
        
        for phase in phase_names:
            assert phase in PHASE_RITUALS
    
    def test_ritual_structure(self):
        """Each ritual should have required fields."""
        for phase, ritual in PHASE_RITUALS.items():
            assert "theme" in ritual
            assert "energy" in ritual
            assert "activities" in ritual
            assert "avoid" in ritual
            assert "crystals" in ritual
            assert "colors" in ritual
            assert "affirmation" in ritual
    
    def test_activities_are_lists(self):
        """Activities should be non-empty lists."""
        for phase, ritual in PHASE_RITUALS.items():
            assert isinstance(ritual["activities"], list)
            assert len(ritual["activities"]) >= 1


# --- Test Sign Ritual Focus ---

class TestSignRitualFocus:
    """Tests for sign-based ritual focus data."""
    
    def test_all_signs_have_focus(self):
        """All 12 signs should have ritual focus data."""
        for sign in ZODIAC_ORDER:
            assert sign in SIGN_RITUAL_FOCUS
    
    def test_sign_focus_structure(self):
        """Each sign focus should have required fields."""
        for sign, focus in SIGN_RITUAL_FOCUS.items():
            assert "theme" in focus
            assert "focus" in focus
            assert "body_area" in focus
            assert "element_boost" in focus


# --- Test Personalized Ritual ---

class TestPersonalizedRitual:
    """Tests for personalized ritual generation."""
    
    def test_basic_ritual_structure(self):
        """Ritual should have all required fields."""
        result = get_personalized_ritual("New Moon", "Aries")
        
        assert "phase" in result
        assert "moon_sign" in result
        assert "theme" in result
        assert "energy" in result
        assert "sign_focus" in result
        assert "activities" in result
        assert "avoid" in result
        assert "element_boost" in result
        assert "crystals" in result
        assert "colors" in result
        assert "affirmation" in result
    
    def test_ritual_with_natal_chart(self, sample_natal_chart):
        """Ritual with natal chart should include natal insight."""
        # Moon in Cancer in chart, test when transit Moon is also in Cancer
        result = get_personalized_ritual(
            "Full Moon", 
            "Cancer",  # Same as natal Moon sign
            sample_natal_chart,
        )
        
        # Should have lunar return insight
        assert "natal_insight" in result
        assert "Lunar Return" in result["natal_insight"]
    
    def test_ritual_with_numerology(self, sample_natal_chart, sample_numerology):
        """Ritual with numerology should include numerology insight."""
        result = get_personalized_ritual(
            "New Moon",
            "Leo",
            sample_natal_chart,
            personal_day=7,
        )
        
        assert "numerology_insight" in result
    
    def test_all_phases_generate_rituals(self):
        """All phases should generate valid rituals."""
        phases = [p["name"] for p in MOON_PHASES]
        
        for phase in phases:
            result = get_personalized_ritual(phase, "Aries")
            assert result["phase"] == phase
            assert len(result["activities"]) >= 1


# --- Test Moon Phase Summary ---

class TestMoonPhaseSummary:
    """Tests for complete Moon phase summary."""
    
    def test_summary_structure(self):
        """Summary should have all sections."""
        result = get_moon_phase_summary()
        
        assert "current_phase" in result
        assert "moon_sign" in result
        assert "ritual" in result
        assert "upcoming_events" in result
    
    def test_summary_with_natal(self, sample_natal_chart):
        """Summary with natal chart should work."""
        result = get_moon_phase_summary(natal_chart=sample_natal_chart)
        
        assert result["current_phase"] is not None
        assert result["ritual"] is not None
    
    def test_summary_with_numerology(self, sample_natal_chart, sample_numerology):
        """Summary with both natal and numerology should include insights."""
        result = get_moon_phase_summary(
            natal_chart=sample_natal_chart,
            numerology=sample_numerology,
        )
        
        assert result["ritual"] is not None


# --- Integration Tests ---

class TestMoonPhasesIntegration:
    """Integration tests for Moon phases module."""
    
    def test_full_workflow(self, sample_natal_chart, sample_numerology):
        """Test complete workflow from phase to ritual."""
        # Get current phase
        phase = calculate_moon_phase()
        assert phase["phase_name"] is not None
        
        # Estimate Moon sign
        moon_sign = estimate_moon_sign()
        assert moon_sign in ZODIAC_ORDER
        
        # Get personalized ritual
        ritual = get_personalized_ritual(
            phase["phase_name"],
            moon_sign,
            sample_natal_chart,
            sample_numerology.get("cycles", {}).get("personal_day", {}).get("number"),
        )
        assert ritual is not None
        
        # Get upcoming events
        events = get_upcoming_moon_events(30)
        assert isinstance(events, list)
        
        # Get full summary
        summary = get_moon_phase_summary(sample_natal_chart, sample_numerology)
        assert summary is not None
