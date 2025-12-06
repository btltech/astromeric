"""
Test suite for the Timing Advisor module.
Tests timing recommendations, score calculations, and best day finding.
"""

import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock

from app.engine.timing_advisor import (
    ACTIVITY_PROFILES,
    calculate_timing_score,
    find_best_days,
    get_timing_advice,
    get_available_activities,
)


class TestActivityProfiles:
    """Test activity profile configuration."""
    
    def test_all_activities_have_required_fields(self):
        """All activity profiles should have required configuration."""
        required_fields = [
            "name",
            "favorable_planets",
            "unfavorable_planets",
            "favorable_moon_phases",
            "unfavorable_moon_phases",
            "favorable_moon_signs",
            "avoid_retrograde",
            "avoid_voc_moon",
            "best_personal_days",
            "avoid_personal_days",
            "weight_factors",
        ]
        
        for activity, profile in ACTIVITY_PROFILES.items():
            for field in required_fields:
                assert field in profile, f"Activity '{activity}' missing field '{field}'"
    
    def test_activities_have_valid_planets(self):
        """All activities should have valid planet lists."""
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Neptune", "Uranus", "Pluto"]
        
        for activity, profile in ACTIVITY_PROFILES.items():
            for planet in profile["favorable_planets"]:
                assert planet in valid_planets, f"Activity '{activity}' has invalid planet '{planet}'"
            for planet in profile["unfavorable_planets"]:
                assert planet in valid_planets, f"Activity '{activity}' has invalid unfavorable planet '{planet}'"
    
    def test_activities_have_valid_moon_phases(self):
        """All activities should have valid moon phase lists."""
        valid_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
                       "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
        
        for activity, profile in ACTIVITY_PROFILES.items():
            for phase in profile["favorable_moon_phases"]:
                assert phase in valid_phases, f"Activity '{activity}' has invalid moon phase '{phase}'"
            for phase in profile["unfavorable_moon_phases"]:
                assert phase in valid_phases, f"Activity '{activity}' has invalid unfavorable moon phase '{phase}'"
    
    def test_expected_activities_exist(self):
        """Verify expected activities are configured."""
        expected = [
            "business_meeting",
            "travel",
            "romance_date",
            "signing_contracts",
            "job_interview",
            "starting_project",
            "creative_work",
            "medical_procedure",
            "financial_decision",
            "meditation_spiritual",
        ]
        
        for activity in expected:
            assert activity in ACTIVITY_PROFILES, f"Expected activity '{activity}' not found"
    
    def test_weight_factors_sum_to_one(self):
        """Test that weight factors approximately sum to 1."""
        for activity, profile in ACTIVITY_PROFILES.items():
            weights = profile["weight_factors"]
            total = sum(weights.values())
            assert 0.99 <= total <= 1.01, f"Activity '{activity}' weights sum to {total}, expected ~1.0"
    
    def test_activity_names_are_human_readable(self):
        """Test that activity names are properly formatted."""
        for activity, profile in ACTIVITY_PROFILES.items():
            name = profile["name"]
            assert len(name) > 0, f"Activity '{activity}' has empty name"
            assert " " in name or name.istitle(), f"Activity '{activity}' name '{name}' should be human-readable"


class TestGetAvailableActivities:
    """Test the available activities listing function."""
    
    def test_returns_list(self):
        """Test that available activities returns a list."""
        result = get_available_activities()
        assert isinstance(result, list)
        assert len(result) == len(ACTIVITY_PROFILES)
    
    def test_each_activity_has_id_and_name(self):
        """Test that each activity has id and name."""
        result = get_available_activities()
        for activity in result:
            assert "id" in activity
            assert "name" in activity
            assert activity["id"] in ACTIVITY_PROFILES


class TestCalculateTimingScore:
    """Test timing score calculations."""
    
    @pytest.fixture
    def sample_transit_chart(self):
        """Create a sample transit chart for testing."""
        return {
            "planets": [
                {"name": "Sun", "sign": "Aries", "degree": 15.0, "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "degree": 10.0, "retrograde": False},
                {"name": "Mercury", "sign": "Gemini", "degree": 5.0, "retrograde": False},
                {"name": "Venus", "sign": "Taurus", "degree": 20.0, "retrograde": False},
                {"name": "Mars", "sign": "Leo", "degree": 8.0, "retrograde": False},
                {"name": "Jupiter", "sign": "Sagittarius", "degree": 12.0, "retrograde": False},
                {"name": "Saturn", "sign": "Capricorn", "degree": 25.0, "retrograde": False},
            ],
            "houses": [],
            "aspects": [],
        }
    
    def test_returns_dict_with_expected_keys(self, sample_transit_chart):
        """Test that calculate_timing_score returns expected structure."""
        now = datetime.now(ZoneInfo("UTC"))
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        assert isinstance(result, dict)
        assert "activity" in result
        assert "score" in result
        assert "rating" in result
        assert "breakdown" in result
        assert "warnings" in result
        assert "recommendations" in result
        assert "best_hours" in result
    
    def test_score_in_valid_range(self, sample_transit_chart):
        """Test that score is between 0 and 100."""
        now = datetime.now(ZoneInfo("UTC"))
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        assert 0 <= result["score"] <= 100
    
    def test_breakdown_contains_all_factors(self, sample_transit_chart):
        """Test that breakdown includes all scoring factors."""
        now = datetime.now(ZoneInfo("UTC"))
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        breakdown = result["breakdown"]
        assert "planetary_hour" in breakdown
        assert "moon_phase" in breakdown
        assert "moon_sign" in breakdown
        assert "retrograde" in breakdown
        assert "voc_moon" in breakdown
    
    def test_rating_matches_score(self, sample_transit_chart):
        """Test that rating matches score thresholds."""
        now = datetime.now(ZoneInfo("UTC"))
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        score = result["score"]
        rating = result["rating"]
        
        if score >= 80:
            assert rating == "Excellent"
        elif score >= 65:
            assert rating == "Good"
        elif score >= 50:
            assert rating == "Moderate"
        else:
            assert rating == "Challenging"
    
    def test_personal_day_affects_score(self, sample_transit_chart):
        """Test that personal day number affects the score."""
        now = datetime.now(ZoneInfo("UTC"))
        
        # Business meeting: best personal days are 1, 4, 8
        result_good_day = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            personal_day=1,  # Favorable
        )
        
        result_bad_day = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            personal_day=7,  # Avoid
        )
        
        assert "personal_day" in result_good_day["breakdown"]
        assert result_good_day["breakdown"]["personal_day"] > result_bad_day["breakdown"]["personal_day"]
    
    def test_all_activities_can_be_scored(self, sample_transit_chart):
        """Test that all activities can be scored without error."""
        now = datetime.now(ZoneInfo("UTC"))
        
        for activity in ACTIVITY_PROFILES.keys():
            result = calculate_timing_score(
                activity=activity,
                date=now,
                transit_chart=sample_transit_chart,
                latitude=40.7128,
                longitude=-74.006,
            )
            
            assert result["activity"] == ACTIVITY_PROFILES[activity]["name"]
            assert 0 <= result["score"] <= 100
    
    def test_best_hours_included(self, sample_transit_chart):
        """Test that best hours are included in result."""
        now = datetime.now(ZoneInfo("UTC"))
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        assert "best_hours" in result
        assert isinstance(result["best_hours"], list)


class TestRetrogradeEffect:
    """Test retrograde planet effects on scoring."""
    
    def test_mercury_retrograde_affects_contracts(self):
        """Test that Mercury retrograde lowers signing_contracts score."""
        now = datetime.now(ZoneInfo("UTC"))
        
        # Chart without retrograde
        chart_no_retro = {
            "planets": [
                {"name": "Mercury", "sign": "Gemini", "retrograde": False},
                {"name": "Sun", "sign": "Leo", "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "retrograde": False},
            ]
        }
        
        # Chart with Mercury retrograde
        chart_retro = {
            "planets": [
                {"name": "Mercury", "sign": "Gemini", "retrograde": True},
                {"name": "Sun", "sign": "Leo", "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "retrograde": False},
            ]
        }
        
        score_no_retro = calculate_timing_score(
            activity="signing_contracts",
            date=now,
            transit_chart=chart_no_retro,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        score_retro = calculate_timing_score(
            activity="signing_contracts",
            date=now,
            transit_chart=chart_retro,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        # Retrograde should lower the score for contracts
        assert score_retro["breakdown"]["retrograde"] < score_no_retro["breakdown"]["retrograde"]
    
    def test_creative_work_unaffected_by_retrograde(self):
        """Test that creative work is less affected by retrogrades."""
        now = datetime.now(ZoneInfo("UTC"))
        
        chart_retro = {
            "planets": [
                {"name": "Mercury", "sign": "Gemini", "retrograde": True},
                {"name": "Sun", "sign": "Leo", "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "retrograde": False},
            ]
        }
        
        # Creative work has empty avoid_retrograde list
        result = calculate_timing_score(
            activity="creative_work",
            date=now,
            transit_chart=chart_retro,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        # Should still have decent retrograde score since creative_work doesn't avoid any
        assert result["breakdown"]["retrograde"] >= 70


class TestFindBestDays:
    """Test best day finding functionality."""
    
    @pytest.fixture
    def sample_transit_chart(self):
        return {
            "planets": [
                {"name": "Sun", "sign": "Aries", "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "retrograde": False},
                {"name": "Mercury", "sign": "Gemini", "retrograde": False},
            ]
        }
    
    def test_returns_sorted_list(self, sample_transit_chart):
        """Test that best days are sorted by score descending."""
        result = find_best_days(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            days_ahead=7,
        )
        
        assert isinstance(result, list)
        # Verify sorted descending by score
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)
    
    def test_respects_days_ahead(self, sample_transit_chart):
        """Test that days_ahead parameter limits results."""
        result = find_best_days(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            days_ahead=5,
        )
        
        assert len(result) == 5
    
    def test_includes_weekday(self, sample_transit_chart):
        """Test that results include weekday information."""
        result = find_best_days(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            days_ahead=3,
        )
        
        for day in result:
            assert "weekday" in day
            assert day["weekday"] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    def test_personal_year_affects_scoring(self, sample_transit_chart):
        """Test that personal year/day cycle affects scoring."""
        result = find_best_days(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
            days_ahead=7,
            personal_day_cycle=1,  # Personal Year 1
        )
        
        # Each day should have personal_day score in breakdown
        for day in result:
            assert "personal_day" in day["breakdown"]


class TestGetTimingAdvice:
    """Test the main timing advice function."""
    
    @pytest.fixture
    def sample_transit_chart(self):
        return {
            "planets": [
                {"name": "Sun", "sign": "Aries", "retrograde": False},
                {"name": "Moon", "sign": "Cancer", "retrograde": False},
                {"name": "Mercury", "sign": "Gemini", "retrograde": False},
            ]
        }
    
    def test_returns_complete_advice(self, sample_transit_chart):
        """Test that get_timing_advice returns complete structure."""
        result = get_timing_advice(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        assert "activity" in result
        assert "today" in result
        assert "best_upcoming" in result
        assert "today_is_best" in result
        assert "all_days" in result
        assert "advice" in result
    
    def test_today_has_required_fields(self, sample_transit_chart):
        """Test that today's score has all required fields."""
        result = get_timing_advice(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        today = result["today"]
        assert "score" in today
        assert "rating" in today
        assert "breakdown" in today
        assert "weekday" in today
    
    def test_advice_is_generated(self, sample_transit_chart):
        """Test that human-readable advice is generated."""
        result = get_timing_advice(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        advice = result["advice"]
        assert isinstance(advice, str)
        assert len(advice) > 10  # Should be a meaningful sentence
    
    def test_all_days_limited_to_five(self, sample_transit_chart):
        """Test that all_days is limited to top 5."""
        result = get_timing_advice(
            activity="business_meeting",
            transit_chart=sample_transit_chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        assert len(result["all_days"]) <= 5
    
    def test_works_for_all_activities(self, sample_transit_chart):
        """Test that advice works for all activity types."""
        for activity in ACTIVITY_PROFILES.keys():
            result = get_timing_advice(
                activity=activity,
                transit_chart=sample_transit_chart,
                latitude=40.7128,
                longitude=-74.006,
            )
            
            assert result["activity"] == ACTIVITY_PROFILES[activity]["name"]
            assert "today" in result
            assert "advice" in result


class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    def test_timing_advice_endpoint_structure(self):
        """Test the expected structure from timing advice endpoint."""
        from fastapi.testclient import TestClient
        from app.main import api
        
        client = TestClient(api)
        
        response = client.post("/timing/advice", json={
            "activity": "business_meeting",
            "latitude": 40.7128,
            "longitude": -74.006,
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "activity" in data
        assert "today" in data
        assert "best_upcoming" in data
        assert "advice" in data
    
    def test_best_days_endpoint_structure(self):
        """Test the expected structure from best days endpoint."""
        from fastapi.testclient import TestClient
        from app.main import api
        
        client = TestClient(api)
        
        response = client.post("/timing/best-days", json={
            "activity": "business_meeting",
            "days_ahead": 5,
            "latitude": 40.7128,
            "longitude": -74.006,
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "activity" in data
        assert "activity_name" in data
        assert "best_days" in data
        assert len(data["best_days"]) == 5
    
    def test_activities_list_endpoint(self):
        """Test the activities listing endpoint."""
        from fastapi.testclient import TestClient
        from app.main import api
        
        client = TestClient(api)
        
        response = client.get("/timing/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert len(data["activities"]) == len(ACTIVITY_PROFILES)
    
    def test_invalid_activity_returns_400(self):
        """Test that invalid activity returns 400 error."""
        from fastapi.testclient import TestClient
        from app.main import api
        
        client = TestClient(api)
        
        response = client.post("/timing/advice", json={
            "activity": "invalid_activity",
            "latitude": 40.7128,
            "longitude": -74.006,
        })
        
        assert response.status_code == 400
        assert "Invalid activity" in response.json()["detail"]
    
    def test_endpoint_with_profile(self):
        """Test timing endpoint with user profile for personalization."""
        from fastapi.testclient import TestClient
        from app.main import api
        
        client = TestClient(api)
        
        response = client.post("/timing/advice", json={
            "activity": "business_meeting",
            "latitude": 40.7128,
            "longitude": -74.006,
            "profile": {
                "name": "Test User",
                "date_of_birth": "1990-05-15",
                "time_of_birth": "14:30",
                "latitude": 40.7128,
                "longitude": -74.006,
                "timezone": "America/New_York",
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "today" in data


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_empty_transit_chart(self):
        """Test that empty transit chart is handled gracefully."""
        now = datetime.now(ZoneInfo("UTC"))
        
        result = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart={"planets": []},
            latitude=40.7128,
            longitude=-74.006,
        )
        
        # Should still return a valid score
        assert "score" in result
        assert 0 <= result["score"] <= 100
    
    def test_default_activity_fallback(self):
        """Test that unknown activity defaults to business_meeting."""
        now = datetime.now(ZoneInfo("UTC"))
        
        result = calculate_timing_score(
            activity="unknown_activity",
            date=now,
            transit_chart={"planets": []},
            latitude=40.7128,
            longitude=-74.006,
        )
        
        # Should use business_meeting as fallback
        assert result["activity"] == "Business Meeting"
    
    def test_different_timezones(self):
        """Test calculations work with different timezones."""
        chart = {"planets": []}
        
        result_utc = calculate_timing_score(
            activity="business_meeting",
            date=datetime.now(ZoneInfo("UTC")),
            transit_chart=chart,
            latitude=40.7128,
            longitude=-74.006,
            timezone="UTC",
        )
        
        result_la = calculate_timing_score(
            activity="business_meeting",
            date=datetime.now(ZoneInfo("America/Los_Angeles")),
            transit_chart=chart,
            latitude=34.0522,
            longitude=-118.2437,
            timezone="America/Los_Angeles",
        )
        
        # Both should return valid results
        assert "score" in result_utc
        assert "score" in result_la
    
    def test_different_locations(self):
        """Test calculations work with different locations."""
        now = datetime.now(ZoneInfo("UTC"))
        chart = {"planets": []}
        
        # New York
        result_ny = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=chart,
            latitude=40.7128,
            longitude=-74.006,
        )
        
        # Tokyo
        result_tokyo = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=chart,
            latitude=35.6762,
            longitude=139.6503,
        )
        
        # London
        result_london = calculate_timing_score(
            activity="business_meeting",
            date=now,
            transit_chart=chart,
            latitude=51.5074,
            longitude=-0.1278,
        )
        
        # All should return valid results
        assert "score" in result_ny
        assert "score" in result_tokyo
        assert "score" in result_london
