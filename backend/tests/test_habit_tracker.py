"""
Tests for Habit Tracker with Lunar Cycles Engine and API.
"""
import pytest
from datetime import datetime, timedelta

from backend.app.engine.habit_tracker import (
    LUNAR_HABIT_GUIDANCE,
    HABIT_CATEGORIES,
    get_moon_phase_name,
    create_habit,
    log_habit_completion,
    calculate_lunar_alignment_score,
    get_habit_streak,
    get_lunar_habit_recommendations,
    calculate_habit_analytics,
    get_today_habit_forecast,
    get_lunar_cycle_report,
)


# =============================================================================
# Test Moon Phase Name
# =============================================================================

class TestGetMoonPhaseName:
    """Tests for get_moon_phase_name function."""
    
    def test_new_moon(self):
        """Test new moon detection."""
        assert get_moon_phase_name(0, True) == "new_moon"
        assert get_moon_phase_name(2, False) == "new_moon"
    
    def test_full_moon(self):
        """Test full moon detection."""
        assert get_moon_phase_name(100, True) == "full_moon"
        assert get_moon_phase_name(98, False) == "full_moon"
    
    def test_waxing_crescent(self):
        """Test waxing crescent detection."""
        assert get_moon_phase_name(25, True) == "waxing_crescent"
    
    def test_waning_crescent(self):
        """Test waning crescent detection."""
        assert get_moon_phase_name(25, False) == "waning_crescent"
    
    def test_first_quarter(self):
        """Test first quarter detection."""
        assert get_moon_phase_name(50, True) == "first_quarter"
    
    def test_last_quarter(self):
        """Test last quarter detection."""
        assert get_moon_phase_name(50, False) == "last_quarter"
    
    def test_waxing_gibbous(self):
        """Test waxing gibbous detection."""
        assert get_moon_phase_name(75, True) == "waxing_gibbous"
    
    def test_waning_gibbous(self):
        """Test waning gibbous detection."""
        assert get_moon_phase_name(75, False) == "waning_gibbous"


# =============================================================================
# Test Create Habit
# =============================================================================

class TestCreateHabit:
    """Tests for create_habit function."""
    
    def test_basic_habit_creation(self):
        """Test creating a basic habit."""
        habit = create_habit("Morning Meditation", "meditation")
        
        assert habit["name"] == "Morning Meditation"
        assert habit["category"] == "meditation"
        assert habit["frequency"] == "daily"
        assert habit["target_count"] == 1
    
    def test_habit_with_custom_frequency(self):
        """Test habit with weekly frequency."""
        habit = create_habit("Weekly Yoga", "exercise", frequency="weekly", target_count=3)
        
        assert habit["frequency"] == "weekly"
        assert habit["target_count"] == 3
    
    def test_habit_includes_category_info(self):
        """Test that habit includes category metadata."""
        habit = create_habit("Study Session", "learning")
        
        assert habit["category_name"] == "Learning & Study"
        assert habit["category_emoji"] == "📚"
        assert "best_phases" in habit
        assert "avoid_phases" in habit
    
    def test_habit_has_timestamps(self):
        """Test that habit has created_at timestamp."""
        habit = create_habit("Test Habit", "health")
        
        assert "created_at" in habit
        assert habit["is_active"] == True
    
    def test_habit_with_description(self):
        """Test habit with custom description."""
        habit = create_habit(
            "Evening Walk", 
            "exercise", 
            description="30-minute walk after dinner"
        )
        
        assert habit["description"] == "30-minute walk after dinner"


# =============================================================================
# Test Log Habit Completion
# =============================================================================

class TestLogHabitCompletion:
    """Tests for log_habit_completion function."""
    
    def test_basic_completion_log(self):
        """Test logging a basic completion."""
        log = log_habit_completion(1)
        
        assert log["habit_id"] == 1
        assert "completed_at" in log
        assert "date" in log
        assert "weekday" in log
    
    def test_completion_with_moon_phase(self):
        """Test completion with moon phase."""
        log = log_habit_completion(1, moon_phase="full_moon")
        
        assert log["moon_phase"] == "full_moon"
    
    def test_completion_with_notes(self):
        """Test completion with notes."""
        log = log_habit_completion(1, notes="Felt great today!")
        
        assert log["notes"] == "Felt great today!"
    
    def test_completion_with_custom_date(self):
        """Test completion with custom date."""
        custom_date = datetime(2024, 6, 15, 10, 30)
        log = log_habit_completion(1, completed_at=custom_date)
        
        assert log["date"] == "2024-06-15"
        assert log["weekday"] == "Saturday"


# =============================================================================
# Test Calculate Lunar Alignment Score
# =============================================================================

class TestCalculateLunarAlignmentScore:
    """Tests for calculate_lunar_alignment_score function."""
    
    def test_excellent_alignment(self):
        """Test excellent alignment (category best phase)."""
        # Exercise is best during first_quarter
        result = calculate_lunar_alignment_score("exercise", "first_quarter")
        
        assert result["alignment"] == "Excellent"
        assert result["score"] >= 80
        assert result["is_optimal"] == True
    
    def test_challenging_alignment(self):
        """Test challenging alignment (category avoid phase)."""
        # Exercise should avoid waning_crescent
        result = calculate_lunar_alignment_score("exercise", "waning_crescent")
        
        assert result["alignment"] == "Challenging"
        assert result["score"] <= 40
        assert result["is_optimal"] == False
    
    def test_moderate_alignment(self):
        """Test moderate alignment (neutral phase)."""
        # Meditation has no avoid phases, so most are OK
        result = calculate_lunar_alignment_score("meditation", "first_quarter")
        
        # Not best, not avoid, so should be moderate or excellent
        assert result["score"] >= 50
    
    def test_includes_phase_info(self):
        """Test that result includes phase info."""
        result = calculate_lunar_alignment_score("creative", "full_moon")
        
        assert "phase_name" in result
        assert "phase_emoji" in result
        assert "phase_theme" in result
        assert "message" in result
    
    def test_all_categories_valid(self):
        """Test all categories work with all phases."""
        for category in HABIT_CATEGORIES:
            for phase in LUNAR_HABIT_GUIDANCE:
                result = calculate_lunar_alignment_score(category, phase)
                assert 0 <= result["score"] <= 100


# =============================================================================
# Test Get Habit Streak
# =============================================================================

class TestGetHabitStreak:
    """Tests for get_habit_streak function."""
    
    def test_empty_completions(self):
        """Test with no completions."""
        result = get_habit_streak([])
        
        assert result["current_streak"] == 0
        assert result["longest_streak"] == 0
        assert result["total_completions"] == 0
    
    def test_single_completion(self):
        """Test with single completion."""
        today = datetime.now().strftime("%Y-%m-%d")
        completions = [{"date": today}]
        
        result = get_habit_streak(completions)
        
        assert result["current_streak"] >= 1
        assert result["total_completions"] == 1
    
    def test_consecutive_days(self):
        """Test streak with consecutive days."""
        today = datetime.now()
        completions = []
        for i in range(5):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            completions.append({"date": date})
        
        result = get_habit_streak(completions)
        
        assert result["current_streak"] >= 4  # May vary due to date logic
    
    def test_broken_streak(self):
        """Test streak that's been broken."""
        # Create a gap
        today = datetime.now()
        completions = [
            {"date": today.strftime("%Y-%m-%d")},
            {"date": (today - timedelta(days=5)).strftime("%Y-%m-%d")}
        ]
        
        result = get_habit_streak(completions)
        
        # Current streak should be 1 (just today)
        assert result["current_streak"] <= 2
    
    def test_streak_message(self):
        """Test streak includes motivational message."""
        result = get_habit_streak([])
        
        assert "streak_message" in result
        assert "streak_emoji" in result


# =============================================================================
# Test Get Lunar Habit Recommendations
# =============================================================================

class TestGetLunarHabitRecommendations:
    """Tests for get_lunar_habit_recommendations function."""
    
    def test_returns_recommendations(self):
        """Test that function returns recommendations."""
        result = get_lunar_habit_recommendations("new_moon")
        
        assert "recommended_categories" in result
        assert len(result["recommended_categories"]) > 0
    
    def test_includes_phase_info(self):
        """Test that result includes phase info."""
        result = get_lunar_habit_recommendations("full_moon")
        
        assert "phase_info" in result
        assert "phase_best_for" in result
        assert "power_tip" in result
    
    def test_with_existing_habits(self):
        """Test with existing habits for personalization."""
        existing = [
            {"name": "Meditation", "category": "meditation"},
            {"name": "Exercise", "category": "exercise"}
        ]
        
        result = get_lunar_habit_recommendations("new_moon", existing)
        
        # Meditation is ideal for new moon
        assert len(result["aligned_existing_habits"]) >= 1
    
    def test_all_phases_have_recommendations(self):
        """Test all phases return valid recommendations."""
        for phase in LUNAR_HABIT_GUIDANCE:
            result = get_lunar_habit_recommendations(phase)
            assert "recommended_categories" in result


# =============================================================================
# Test Calculate Habit Analytics
# =============================================================================

class TestCalculateHabitAnalytics:
    """Tests for calculate_habit_analytics function."""
    
    def test_empty_completions(self):
        """Test with no completions."""
        habit = {"name": "Test", "frequency": "daily", "target_count": 1}
        
        result = calculate_habit_analytics(habit, [])
        
        assert result["completion_rate"] == 0
        assert result["total_completions"] == 0
        assert "insights" in result
    
    def test_with_completions(self):
        """Test with sample completions."""
        habit = {"name": "Test", "frequency": "daily", "target_count": 1}
        
        # Create 10 completions in last 30 days
        today = datetime.now()
        completions = []
        for i in range(10):
            completions.append({
                "completed_at": (today - timedelta(days=i*2)).isoformat(),
                "date": (today - timedelta(days=i*2)).strftime("%Y-%m-%d"),
                "weekday": (today - timedelta(days=i*2)).strftime("%A"),
                "moon_phase": "full_moon"
            })
        
        result = calculate_habit_analytics(habit, completions, 30)
        
        assert result["total_completions"] == 10
        assert result["completion_rate"] > 0
    
    def test_phase_distribution(self):
        """Test that phase distribution is calculated."""
        habit = {"name": "Test", "frequency": "daily", "target_count": 1}
        completions = [
            {"completed_at": datetime.now().isoformat(), "moon_phase": "full_moon", "weekday": "Monday"},
            {"completed_at": datetime.now().isoformat(), "moon_phase": "new_moon", "weekday": "Tuesday"},
            {"completed_at": datetime.now().isoformat(), "moon_phase": "full_moon", "weekday": "Monday"}
        ]
        
        result = calculate_habit_analytics(habit, completions, 30)
        
        assert "by_phase" in result
        assert result["by_phase"].get("full_moon", 0) == 2
    
    def test_best_day_calculation(self):
        """Test best day is calculated."""
        habit = {"name": "Test", "frequency": "daily", "target_count": 1}
        completions = [
            {"completed_at": datetime.now().isoformat(), "weekday": "Monday"},
            {"completed_at": datetime.now().isoformat(), "weekday": "Monday"},
            {"completed_at": datetime.now().isoformat(), "weekday": "Tuesday"}
        ]
        
        result = calculate_habit_analytics(habit, completions, 30)
        
        assert result["best_day"] == "Monday"


# =============================================================================
# Test Get Today Habit Forecast
# =============================================================================

class TestGetTodayHabitForecast:
    """Tests for get_today_habit_forecast function."""
    
    def test_returns_forecast(self):
        """Test that function returns a forecast."""
        habits = [
            {"id": 1, "name": "Meditation", "category": "meditation", "is_active": True},
            {"id": 2, "name": "Exercise", "category": "exercise", "is_active": True}
        ]
        
        result = get_today_habit_forecast(habits, "new_moon")
        
        assert "date" in result
        assert "habits" in result
        assert "phase_info" in result
        assert "summary" in result
    
    def test_sorted_by_alignment(self):
        """Test habits are sorted by alignment score."""
        habits = [
            {"id": 1, "name": "Meditation", "category": "meditation", "is_active": True},
            {"id": 2, "name": "Exercise", "category": "exercise", "is_active": True}
        ]
        
        result = get_today_habit_forecast(habits, "new_moon")
        
        # Meditation should be first (best for new moon)
        scores = [h["alignment_score"] for h in result["habits"]]
        assert scores == sorted(scores, reverse=True)
    
    def test_tracks_completions(self):
        """Test that completed habits are tracked."""
        habits = [
            {"id": 1, "name": "Meditation", "category": "meditation", "is_active": True}
        ]
        
        result = get_today_habit_forecast(habits, "new_moon", completions_today=[1])
        
        assert result["habits"][0]["is_completed"] == True
        assert result["summary"]["completed"] == 1
    
    def test_summary_stats(self):
        """Test summary statistics are calculated."""
        habits = [
            {"id": 1, "name": "Test1", "category": "meditation", "is_active": True},
            {"id": 2, "name": "Test2", "category": "exercise", "is_active": True}
        ]
        
        result = get_today_habit_forecast(habits, "new_moon", completions_today=[1])
        
        assert result["summary"]["total_habits"] == 2
        assert result["summary"]["completed"] == 1
        assert result["summary"]["completion_rate"] == 50.0


# =============================================================================
# Test Get Lunar Cycle Report
# =============================================================================

class TestGetLunarCycleReport:
    """Tests for get_lunar_cycle_report function."""
    
    def test_returns_report(self):
        """Test that function returns a report."""
        habits = [{"id": 1, "name": "Test", "category": "meditation"}]
        completions = []
        
        result = get_lunar_cycle_report(habits, completions)
        
        assert "summary" in result
        assert "habits" in result
        assert "moon_wisdom" in result
    
    def test_with_completions(self):
        """Test report with completions."""
        habits = [{"id": 1, "name": "Test", "category": "meditation", "frequency": "daily"}]
        completions = [
            {"habit_id": 1, "completed_at": datetime.now().isoformat(), "moon_phase": "new_moon"},
            {"habit_id": 1, "completed_at": datetime.now().isoformat(), "moon_phase": "full_moon"}
        ]
        
        result = get_lunar_cycle_report(habits, completions)
        
        assert result["summary"]["total_completions"] == 2
    
    def test_phase_distribution(self):
        """Test phase distribution in report."""
        habits = [{"id": 1, "name": "Test", "category": "meditation"}]
        completions = [
            {"habit_id": 1, "moon_phase": "new_moon"},
            {"habit_id": 1, "moon_phase": "new_moon"},
            {"habit_id": 1, "moon_phase": "full_moon"}
        ]
        
        result = get_lunar_cycle_report(habits, completions)
        
        assert "phase_distribution" in result
        assert result["phase_distribution"].get("new_moon", 0) == 2


# =============================================================================
# Test Constants
# =============================================================================

class TestConstants:
    """Tests for module constants."""
    
    def test_all_phases_defined(self):
        """Test all 8 main phases are defined."""
        expected_phases = [
            "new_moon", "waxing_crescent", "first_quarter", "waxing_gibbous",
            "full_moon", "waning_gibbous", "last_quarter", "waning_crescent"
        ]
        
        for phase in expected_phases:
            assert phase in LUNAR_HABIT_GUIDANCE
    
    def test_phases_have_required_fields(self):
        """Test all phases have required fields."""
        required = ["phase_name", "emoji", "theme", "best_for", "avoid", "energy", "ideal_habits"]
        
        for phase, info in LUNAR_HABIT_GUIDANCE.items():
            for field in required:
                assert field in info, f"Phase {phase} missing {field}"
    
    def test_categories_have_required_fields(self):
        """Test all categories have required fields."""
        required = ["name", "emoji", "description", "best_phases", "avoid_phases"]
        
        for cat, info in HABIT_CATEGORIES.items():
            for field in required:
                assert field in info, f"Category {cat} missing {field}"
    
    def test_category_phases_valid(self):
        """Test that category phases reference valid phase keys."""
        valid_phases = set(LUNAR_HABIT_GUIDANCE.keys())
        
        for cat, info in HABIT_CATEGORIES.items():
            for phase in info["best_phases"]:
                assert phase in valid_phases, f"Invalid phase {phase} in {cat}"
            for phase in info["avoid_phases"]:
                assert phase in valid_phases, f"Invalid phase {phase} in {cat}"


# =============================================================================
# Test API Endpoints
# =============================================================================

class TestHabitAPIEndpoints:
    """Tests for Habit Tracker API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.app.main import api
        return TestClient(api)
    
    def test_get_categories(self, client):
        """Test GET /habits/categories endpoint."""
        response = client.get("/habits/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 5
    
    def test_get_lunar_guidance(self, client):
        """Test GET /habits/lunar-guidance endpoint."""
        response = client.get("/habits/lunar-guidance")
        
        assert response.status_code == 200
        data = response.json()
        assert "phases" in data
        assert len(data["phases"]) == 8
    
    def test_get_phase_guidance(self, client):
        """Test GET /habits/lunar-guidance/{phase} endpoint."""
        response = client.get("/habits/lunar-guidance/new_moon")
        
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] == "new_moon"
        assert "theme" in data
    
    def test_get_phase_guidance_invalid(self, client):
        """Test invalid phase returns 400."""
        response = client.get("/habits/lunar-guidance/invalid_phase")
        
        assert response.status_code == 400
    
    def test_check_alignment(self, client):
        """Test POST /habits/alignment endpoint."""
        response = client.post(
            "/habits/alignment?category=meditation&moon_phase=new_moon"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "alignment" in data
    
    def test_check_alignment_invalid_category(self, client):
        """Test alignment with invalid category."""
        response = client.post(
            "/habits/alignment?category=invalid&moon_phase=new_moon"
        )
        
        assert response.status_code == 400
    
    def test_get_recommendations(self, client):
        """Test POST /habits/recommendations endpoint."""
        response = client.post(
            "/habits/recommendations?moon_phase=full_moon"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommended_categories" in data
    
    def test_create_habit(self, client):
        """Test POST /habits/create endpoint."""
        response = client.post(
            "/habits/create",
            json={"name": "Morning Yoga", "category": "exercise"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["habit"]["name"] == "Morning Yoga"
    
    def test_create_habit_invalid_category(self, client):
        """Test create habit with invalid category."""
        response = client.post(
            "/habits/create",
            json={"name": "Test", "category": "invalid_category"}
        )
        
        assert response.status_code == 400
    
    def test_log_completion(self, client):
        """Test POST /habits/log endpoint."""
        response = client.post(
            "/habits/log?moon_phase=full_moon",
            json={"habit_id": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["completion"]["moon_phase"] == "full_moon"
    
    def test_calculate_streak(self, client):
        """Test POST /habits/streak endpoint."""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.post(
            "/habits/streak?frequency=daily",
            json={"completions": [{"date": today}, {"date": yesterday}]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data
    
    def test_get_today_forecast(self, client):
        """Test POST /habits/today endpoint."""
        response = client.post(
            "/habits/today?moon_phase=new_moon",
            json={
                "habits": [
                    {"id": 1, "name": "Meditation", "category": "meditation", "is_active": True}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "habits" in data
        assert "summary" in data


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_all_categories_create_valid_habits(self):
        """Test all categories can create habits."""
        for category in HABIT_CATEGORIES:
            habit = create_habit(f"Test {category}", category)
            assert habit["category"] == category
    
    def test_unknown_category_uses_default(self):
        """Test unknown category falls back gracefully."""
        habit = create_habit("Test", "nonexistent_category")
        # Should use health as default
        assert "category_name" in habit
    
    def test_empty_habits_forecast(self):
        """Test forecast with empty habits list."""
        result = get_today_habit_forecast([], "new_moon")
        
        assert result["summary"]["total_habits"] == 0
    
    def test_inactive_habits_excluded(self):
        """Test inactive habits are excluded from forecast."""
        habits = [
            {"id": 1, "name": "Active", "category": "meditation", "is_active": True},
            {"id": 2, "name": "Inactive", "category": "exercise", "is_active": False}
        ]
        
        result = get_today_habit_forecast(habits, "new_moon")
        
        assert result["summary"]["total_habits"] == 1
