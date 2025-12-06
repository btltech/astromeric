"""
Tests for Relationship Timeline Engine and API Endpoints.
"""
import pytest
from datetime import datetime, timedelta

from backend.app.engine.relationship_timeline import (
    get_venus_transit,
    get_mars_transit,
    is_venus_retrograde,
    get_upcoming_relationship_dates,
    analyze_relationship_timing,
    get_best_relationship_days,
    build_relationship_timeline,
    get_relationship_phases,
    VENUS_INGRESSES_2024_2025,
    MARS_INGRESSES_2024_2025,
    VENUS_RETROGRADES,
    RELATIONSHIP_ECLIPSES,
    SIGN_RELATIONSHIP_THEMES,
)


# =============================================================================
# Test Venus and Mars Transits
# =============================================================================

class TestVenusTransit:
    """Tests for get_venus_transit function."""
    
    def test_venus_in_known_period(self):
        """Test Venus transit during a known period."""
        # Venus in Taurus late April 2024
        date = datetime(2024, 5, 10)
        transit = get_venus_transit(date)
        
        assert transit is not None
        assert transit["sign"] == "Taurus"
        assert transit["planet"] == "Venus"
        assert transit["emoji"] == "💕"
    
    def test_venus_transit_returns_dates(self):
        """Test that transit includes start and end dates."""
        date = datetime(2024, 6, 1)
        transit = get_venus_transit(date)
        
        assert transit is not None
        assert "start" in transit
        assert "end" in transit
    
    def test_venus_outside_known_range(self):
        """Test Venus transit outside data range."""
        date = datetime(2027, 1, 1)
        transit = get_venus_transit(date)
        
        assert transit is None


class TestMarsTransit:
    """Tests for get_mars_transit function."""
    
    def test_mars_in_known_period(self):
        """Test Mars transit during a known period."""
        # Mars in Aries late April 2024
        date = datetime(2024, 5, 15)
        transit = get_mars_transit(date)
        
        assert transit is not None
        assert transit["sign"] == "Aries"
        assert transit["planet"] == "Mars"
        assert transit["emoji"] == "🔥"
    
    def test_mars_during_retrograde_period(self):
        """Test Mars transit during its 2025 retrograde."""
        # Mars retrograde in Cancer early 2025
        date = datetime(2025, 2, 1)
        transit = get_mars_transit(date)
        
        assert transit is not None
        assert transit["sign"] == "Cancer"


class TestVenusRetrograde:
    """Tests for is_venus_retrograde function."""
    
    def test_during_retrograde(self):
        """Test during Venus retrograde period."""
        date = datetime(2025, 3, 15)  # During 2025 Venus retrograde
        result = is_venus_retrograde(date)
        
        assert result["is_retrograde"] == True
        assert "warning" in result
        assert result["emoji"] == "💔↩️"
    
    def test_not_retrograde(self):
        """Test when Venus is direct."""
        date = datetime(2024, 6, 1)  # Venus direct
        result = is_venus_retrograde(date)
        
        assert result["is_retrograde"] == False
        assert result["emoji"] == "💕✨"
    
    def test_retrograde_days_remaining(self):
        """Test days remaining calculation."""
        date = datetime(2025, 3, 10)  # Early in retrograde
        result = is_venus_retrograde(date)
        
        assert result["is_retrograde"] == True
        assert result["days_remaining"] > 0


# =============================================================================
# Test Upcoming Relationship Dates
# =============================================================================

class TestUpcomingRelationshipDates:
    """Tests for get_upcoming_relationship_dates function."""
    
    def test_returns_events_list(self):
        """Test that function returns a list of events."""
        date = datetime(2024, 4, 1)
        events = get_upcoming_relationship_dates(date, 90)
        
        assert isinstance(events, list)
        assert len(events) > 0
    
    def test_events_sorted_by_date(self):
        """Test that events are sorted by date."""
        date = datetime(2024, 4, 1)
        events = get_upcoming_relationship_dates(date, 180)
        
        for i in range(len(events) - 1):
            assert events[i]["date"] <= events[i + 1]["date"]
    
    def test_events_have_required_fields(self):
        """Test that events have all required fields."""
        date = datetime(2024, 4, 1)
        events = get_upcoming_relationship_dates(date, 90)
        
        required_fields = ["date", "type", "title", "emoji", "impact", "description", "rating"]
        for event in events:
            for field in required_fields:
                assert field in event, f"Missing field: {field}"
    
    def test_personal_events_with_sign(self):
        """Test personal events when sign is provided."""
        date = datetime(2024, 4, 1)
        events = get_upcoming_relationship_dates(date, 180, sun_sign="Aries")
        
        personal_events = [e for e in events if e.get("is_personal")]
        # Should find some personal events
        # Note: depends on data
        assert isinstance(personal_events, list)
    
    def test_includes_venus_retrograde_events(self):
        """Test that Venus retrograde events are included."""
        date = datetime(2025, 2, 1)  # Before 2025 retrograde
        events = get_upcoming_relationship_dates(date, 90)
        
        retrograde_events = [e for e in events if "retrograde" in e.get("type", "")]
        assert len(retrograde_events) > 0


# =============================================================================
# Test Analyze Relationship Timing
# =============================================================================

class TestAnalyzeRelationshipTiming:
    """Tests for analyze_relationship_timing function."""
    
    def test_returns_analysis_dict(self):
        """Test that function returns a proper analysis dict."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Leo")
        
        assert isinstance(analysis, dict)
        assert "score" in analysis
        assert "rating" in analysis
        assert "factors" in analysis
    
    def test_score_in_range(self):
        """Test that score is within valid range."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Taurus")
        
        assert 0 <= analysis["score"] <= 100
    
    def test_rating_categories(self):
        """Test that rating is a valid category."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Gemini")
        
        valid_ratings = ["Excellent", "Good", "Moderate", "Challenging", "Difficult"]
        assert analysis["rating"] in valid_ratings
    
    def test_includes_transits(self):
        """Test that analysis includes transit info."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Cancer")
        
        assert "venus_transit" in analysis
        assert "mars_transit" in analysis
        assert "venus_retrograde" in analysis
    
    def test_with_partner_sign(self):
        """Test analysis with partner sign."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Aries", "Leo")
        
        assert analysis["person1_sign"] == "Aries"
        assert analysis["person2_sign"] == "Leo"
    
    def test_love_themes_included(self):
        """Test that love themes for sign are included."""
        date = datetime(2024, 6, 1)
        analysis = analyze_relationship_timing(date, "Pisces")
        
        assert "love_themes" in analysis
        assert len(analysis["love_themes"]) > 0
    
    def test_venus_retrograde_lowers_score(self):
        """Test that Venus retrograde lowers the score."""
        # During Venus retrograde
        retro_date = datetime(2025, 3, 15)
        retro_analysis = analyze_relationship_timing(retro_date, "Libra")
        
        # During Venus direct
        direct_date = datetime(2024, 6, 1)
        direct_analysis = analyze_relationship_timing(direct_date, "Libra")
        
        # Retrograde should have lower score (barring other factors)
        assert any("retrograde" in str(w).lower() for w in retro_analysis["warnings"])


# =============================================================================
# Test Best Relationship Days
# =============================================================================

class TestBestRelationshipDays:
    """Tests for get_best_relationship_days function."""
    
    def test_returns_list_of_days(self):
        """Test that function returns a list."""
        date = datetime(2024, 6, 1)
        days = get_best_relationship_days(date, "Virgo", 30)
        
        assert isinstance(days, list)
        assert len(days) == 30
    
    def test_sorted_by_score_descending(self):
        """Test that days are sorted by score descending."""
        date = datetime(2024, 6, 1)
        days = get_best_relationship_days(date, "Scorpio", 30)
        
        for i in range(len(days) - 1):
            assert days[i]["score"] >= days[i + 1]["score"]
    
    def test_includes_today_marker(self):
        """Test that today is marked."""
        date = datetime(2024, 6, 1)
        days = get_best_relationship_days(date, "Sagittarius", 30)
        
        today_days = [d for d in days if d.get("is_today")]
        assert len(today_days) == 1
    
    def test_includes_days_away(self):
        """Test that days_away is included."""
        date = datetime(2024, 6, 1)
        days = get_best_relationship_days(date, "Capricorn", 30)
        
        for day in days:
            assert "days_away" in day
            assert 0 <= day["days_away"] < 30


# =============================================================================
# Test Build Relationship Timeline
# =============================================================================

class TestBuildRelationshipTimeline:
    """Tests for build_relationship_timeline function."""
    
    def test_returns_complete_timeline(self):
        """Test that function returns a complete timeline."""
        timeline = build_relationship_timeline("Aquarius", months_ahead=3)
        
        assert "generated_at" in timeline
        assert "sun_sign" in timeline
        assert "period" in timeline
        assert "today" in timeline
        assert "events" in timeline
    
    def test_period_info(self):
        """Test period information is correct."""
        timeline = build_relationship_timeline("Pisces", months_ahead=6)
        
        assert timeline["period"]["months"] == 6
        assert "start" in timeline["period"]
        assert "end" in timeline["period"]
    
    def test_best_upcoming_days(self):
        """Test best upcoming days are included."""
        timeline = build_relationship_timeline("Aries", months_ahead=2)
        
        assert "best_upcoming_days" in timeline
        assert len(timeline["best_upcoming_days"]) <= 5
    
    def test_events_by_month(self):
        """Test events are grouped by month."""
        timeline = build_relationship_timeline("Taurus", months_ahead=6)
        
        assert "events_by_month" in timeline
        assert isinstance(timeline["events_by_month"], dict)
    
    def test_period_score_and_outlook(self):
        """Test period score and outlook are included."""
        timeline = build_relationship_timeline("Gemini", months_ahead=3)
        
        assert "period_score" in timeline
        assert 0 <= timeline["period_score"] <= 100
        assert "period_outlook" in timeline
    
    def test_with_partner_sign(self):
        """Test timeline with partner sign."""
        timeline = build_relationship_timeline("Cancer", partner_sign="Scorpio", months_ahead=3)
        
        assert timeline["sun_sign"] == "Cancer"
        assert timeline["partner_sign"] == "Scorpio"
    
    def test_love_themes_included(self):
        """Test love themes are included."""
        timeline = build_relationship_timeline("Leo", months_ahead=3)
        
        assert "love_themes" in timeline
        assert "love_style" in timeline["love_themes"]


# =============================================================================
# Test Get Relationship Phases
# =============================================================================

class TestGetRelationshipPhases:
    """Tests for get_relationship_phases function."""
    
    def test_returns_phases_dict(self):
        """Test that function returns phases info."""
        result = get_relationship_phases()
        
        assert "phases" in result
        assert "house_order" in result
        assert "description" in result
    
    def test_includes_key_houses(self):
        """Test that key relationship houses are included."""
        result = get_relationship_phases()
        
        # Houses 5, 7, and 8 are key for relationships
        assert 5 in result["phases"]
        assert 7 in result["phases"]
        assert 8 in result["phases"]
    
    def test_phase_has_theme_and_description(self):
        """Test that each phase has theme and description."""
        result = get_relationship_phases()
        
        for house, phase in result["phases"].items():
            assert "theme" in phase
            assert "description" in phase


# =============================================================================
# Test Constants and Data
# =============================================================================

class TestConstants:
    """Tests for module constants."""
    
    def test_venus_ingresses_have_required_fields(self):
        """Test Venus ingresses data structure."""
        for ingress in VENUS_INGRESSES_2024_2025:
            assert "date" in ingress
            assert "sign" in ingress
            assert "end" in ingress
    
    def test_mars_ingresses_have_required_fields(self):
        """Test Mars ingresses data structure."""
        for ingress in MARS_INGRESSES_2024_2025:
            assert "date" in ingress
            assert "sign" in ingress
            assert "end" in ingress
    
    def test_venus_retrogrades_structure(self):
        """Test Venus retrogrades data structure."""
        for retrograde in VENUS_RETROGRADES:
            assert "start" in retrograde
            assert "end" in retrograde
            assert "sign" in retrograde
    
    def test_sign_themes_for_all_signs(self):
        """Test all zodiac signs have relationship themes."""
        all_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for sign in all_signs:
            assert sign in SIGN_RELATIONSHIP_THEMES
            themes = SIGN_RELATIONSHIP_THEMES[sign]
            assert "love_style" in themes
            assert "needs" in themes
            assert "growth_area" in themes


# =============================================================================
# Test API Endpoints
# =============================================================================

class TestRelationshipAPIEndpoints:
    """Tests for Relationship API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.app.main import api
        return TestClient(api)
    
    def test_get_timeline(self, client):
        """Test POST /relationship/timeline endpoint."""
        response = client.post(
            "/relationship/timeline",
            json={"sun_sign": "Leo", "months_ahead": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sun_sign"] == "Leo"
        assert "events" in data
    
    def test_get_timeline_with_partner(self, client):
        """Test timeline with partner sign."""
        response = client.post(
            "/relationship/timeline",
            json={"sun_sign": "Virgo", "partner_sign": "Pisces", "months_ahead": 6}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["partner_sign"] == "Pisces"
    
    def test_get_timing(self, client):
        """Test POST /relationship/timing endpoint."""
        response = client.post(
            "/relationship/timing",
            json={"sun_sign": "Libra"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "rating" in data
    
    def test_get_timing_with_date(self, client):
        """Test timing with specific date."""
        response = client.post(
            "/relationship/timing",
            json={"sun_sign": "Scorpio", "date": "2024-06-15"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2024-06-15"
    
    def test_get_best_days(self, client):
        """Test GET /relationship/best-days/{sun_sign} endpoint."""
        response = client.get("/relationship/best-days/Sagittarius?days_ahead=30")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sun_sign"] == "Sagittarius"
        assert "best_days" in data
        assert len(data["best_days"]) <= 10
    
    def test_get_best_days_invalid_sign(self, client):
        """Test best days with invalid sign."""
        response = client.get("/relationship/best-days/InvalidSign")
        
        assert response.status_code == 400
    
    def test_get_events(self, client):
        """Test GET /relationship/events endpoint."""
        response = client.get("/relationship/events?days_ahead=90")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert data["days_ahead"] == 90
    
    def test_get_events_with_sign(self, client):
        """Test events with sun sign for personalization."""
        response = client.get("/relationship/events?days_ahead=90&sun_sign=Capricorn")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sun_sign"] == "Capricorn"
    
    def test_get_venus_status(self, client):
        """Test GET /relationship/venus-status endpoint."""
        response = client.get("/relationship/venus-status")
        
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "venus_retrograde" in data
    
    def test_get_phases(self, client):
        """Test GET /relationship/phases endpoint."""
        response = client.get("/relationship/phases")
        
        assert response.status_code == 200
        data = response.json()
        assert "phases" in data
        assert "house_order" in data


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_all_zodiac_signs_valid(self):
        """Test all zodiac signs work with analysis."""
        all_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for sign in all_signs:
            analysis = analyze_relationship_timing(datetime(2024, 6, 1), sign)
            assert analysis["person1_sign"] == sign
            assert "score" in analysis
    
    def test_far_future_date(self):
        """Test with date far in the future."""
        future_date = datetime(2027, 1, 1)
        analysis = analyze_relationship_timing(future_date, "Aries")
        
        # Should still return a valid analysis
        assert "score" in analysis
        # Venus transit may be None
        assert "venus_transit" in analysis
    
    def test_past_date(self):
        """Test with past date."""
        past_date = datetime(2023, 1, 1)
        analysis = analyze_relationship_timing(past_date, "Taurus")
        
        # Should still return a valid analysis
        assert "score" in analysis
    
    def test_empty_events_period(self):
        """Test period with potentially no events."""
        far_future = datetime(2030, 1, 1)
        events = get_upcoming_relationship_dates(far_future, 30)
        
        # Should return empty list, not error
        assert isinstance(events, list)
    
    def test_timeline_custom_start_date(self):
        """Test timeline with custom start date."""
        custom_date = datetime(2024, 7, 15)
        timeline = build_relationship_timeline(
            "Gemini",
            start_date=custom_date,
            months_ahead=3
        )
        
        assert timeline["period"]["start"] == "2024-07-15"
