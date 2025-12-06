"""
Tests for Journal & Accountability Engine and API Endpoints.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.app.engine.journal import (
    add_journal_entry,
    record_outcome,
    calculate_accuracy_stats,
    get_reading_insights,
    analyze_prediction_patterns,
    get_journal_prompts,
    create_accountability_report,
    format_reading_for_journal,
    READING_CATEGORIES,
    FEEDBACK_EMOJI,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_readings():
    """Sample readings with various feedback."""
    base_date = datetime.now()
    return [
        {
            "id": 1,
            "scope": "daily",
            "date": (base_date - timedelta(days=0)).isoformat(),
            "feedback": "yes",
            "journal": "Great day, predictions were spot on!",
            "content": '{"theme": "Opportunity knocks"}'
        },
        {
            "id": 2,
            "scope": "daily",
            "date": (base_date - timedelta(days=1)).isoformat(),
            "feedback": "yes",
            "journal": "Another good day.",
            "content": '{"summary": "Focus on relationships"}'
        },
        {
            "id": 3,
            "scope": "weekly",
            "date": (base_date - timedelta(days=2)).isoformat(),
            "feedback": "partial",
            "journal": "",
            "content": '{"theme": "Career focus"}'
        },
        {
            "id": 4,
            "scope": "daily",
            "date": (base_date - timedelta(days=3)).isoformat(),
            "feedback": "no",
            "journal": "Didn't resonate today",
            "content": '{"summary": "Take it easy"}'
        },
        {
            "id": 5,
            "scope": "monthly",
            "date": (base_date - timedelta(days=4)).isoformat(),
            "feedback": None,
            "journal": "",
            "content": '{"theme": "New beginnings"}'
        }
    ]


@pytest.fixture
def empty_readings():
    """Empty readings list."""
    return []


@pytest.fixture
def unrated_readings():
    """Readings with no feedback."""
    return [
        {"id": 1, "scope": "daily", "date": "2024-01-01", "feedback": None, "journal": ""},
        {"id": 2, "scope": "daily", "date": "2024-01-02", "feedback": None, "journal": ""},
    ]


# =============================================================================
# Test add_journal_entry
# =============================================================================

class TestAddJournalEntry:
    """Tests for add_journal_entry function."""
    
    def test_basic_entry(self):
        """Test adding a basic journal entry."""
        result = add_journal_entry(1, "This is my journal entry.")
        
        assert result["reading_id"] == 1
        assert result["entry"] == "This is my journal entry."
        assert "timestamp" in result
        assert result["word_count"] == 5
        assert result["character_count"] == 25
    
    def test_entry_with_custom_timestamp(self):
        """Test entry with custom timestamp."""
        ts = datetime(2024, 1, 15, 10, 30)
        result = add_journal_entry(1, "Test entry", timestamp=ts)
        
        assert result["timestamp"] == "2024-01-15T10:30:00"
    
    def test_empty_entry(self):
        """Test empty entry."""
        result = add_journal_entry(1, "")
        
        assert result["word_count"] == 0
        assert result["character_count"] == 0
    
    def test_long_entry(self):
        """Test long journal entry."""
        long_text = " ".join(["word"] * 500)
        result = add_journal_entry(1, long_text)
        
        assert result["word_count"] == 500


# =============================================================================
# Test record_outcome
# =============================================================================

class TestRecordOutcome:
    """Tests for record_outcome function."""
    
    def test_record_yes_outcome(self):
        """Test recording a 'yes' outcome."""
        result = record_outcome(1, "yes")
        
        assert result["reading_id"] == 1
        assert result["outcome"] == "yes"
        assert result["outcome_emoji"] == "✅"
        assert "recorded_at" in result
    
    def test_record_no_outcome(self):
        """Test recording a 'no' outcome."""
        result = record_outcome(2, "no", notes="Didn't match at all")
        
        assert result["outcome"] == "no"
        assert result["outcome_emoji"] == "❌"
        assert result["notes"] == "Didn't match at all"
    
    def test_record_partial_outcome(self):
        """Test recording a 'partial' outcome."""
        result = record_outcome(3, "partial", categories=["career", "love"])
        
        assert result["outcome"] == "partial"
        assert result["outcome_emoji"] == "🔶"
        assert "career" in result["categories"]
        assert "love" in result["categories"]
    
    def test_default_categories(self):
        """Test default categories."""
        result = record_outcome(1, "yes")
        
        assert result["categories"] == ["general"]


# =============================================================================
# Test calculate_accuracy_stats
# =============================================================================

class TestCalculateAccuracyStats:
    """Tests for calculate_accuracy_stats function."""
    
    def test_with_sample_readings(self, sample_readings):
        """Test accuracy calculation with sample data."""
        result = calculate_accuracy_stats(sample_readings)
        
        assert result["total_readings"] == 5
        assert result["rated_readings"] == 4  # One has None feedback
        assert result["unrated_readings"] == 1
        # 2 yes (100%) + 1 partial (50%) + 1 no (0%) = 250/4 = 62.5%
        assert result["accuracy_rate"] == 62.5
        assert result["by_outcome"]["yes"] == 2
        assert result["by_outcome"]["no"] == 1
        assert result["by_outcome"]["partial"] == 1
    
    def test_empty_readings(self, empty_readings):
        """Test with empty readings list."""
        result = calculate_accuracy_stats(empty_readings)
        
        assert result["total_readings"] == 0
        assert result["rated_readings"] == 0
        assert result["accuracy_rate"] == 0.0
        assert result["trend"] == "neutral"
    
    def test_unrated_readings(self, unrated_readings):
        """Test with unrated readings."""
        result = calculate_accuracy_stats(unrated_readings)
        
        assert result["total_readings"] == 2
        assert result["rated_readings"] == 0
        assert result["accuracy_rate"] == 0.0
    
    def test_scope_breakdown(self, sample_readings):
        """Test accuracy by scope."""
        result = calculate_accuracy_stats(sample_readings)
        
        assert "daily" in result["by_scope"]
        assert "weekly" in result["by_scope"]
    
    def test_all_accurate(self):
        """Test with all accurate readings."""
        readings = [
            {"id": i, "scope": "daily", "date": f"2024-01-{i:02d}", "feedback": "yes"}
            for i in range(1, 6)
        ]
        result = calculate_accuracy_stats(readings)
        
        assert result["accuracy_rate"] == 100.0
    
    def test_all_inaccurate(self):
        """Test with all inaccurate readings."""
        readings = [
            {"id": i, "scope": "daily", "date": f"2024-01-{i:02d}", "feedback": "no"}
            for i in range(1, 6)
        ]
        result = calculate_accuracy_stats(readings)
        
        assert result["accuracy_rate"] == 0.0
    
    def test_trend_improving(self):
        """Test improving trend detection."""
        base = datetime.now()
        readings = [
            # Recent - all yes
            {"id": 1, "scope": "daily", "date": (base - timedelta(days=0)).isoformat(), "feedback": "yes"},
            {"id": 2, "scope": "daily", "date": (base - timedelta(days=1)).isoformat(), "feedback": "yes"},
            {"id": 3, "scope": "daily", "date": (base - timedelta(days=2)).isoformat(), "feedback": "yes"},
            # Older - all no
            {"id": 4, "scope": "daily", "date": (base - timedelta(days=10)).isoformat(), "feedback": "no"},
            {"id": 5, "scope": "daily", "date": (base - timedelta(days=11)).isoformat(), "feedback": "no"},
            {"id": 6, "scope": "daily", "date": (base - timedelta(days=12)).isoformat(), "feedback": "no"},
        ]
        result = calculate_accuracy_stats(readings)
        
        assert result["trend"] == "improving"
        assert result["trend_emoji"] == "📈"


# =============================================================================
# Test get_reading_insights
# =============================================================================

class TestGetReadingInsights:
    """Tests for get_reading_insights function."""
    
    def test_with_sample_readings(self, sample_readings):
        """Test insights with sample data."""
        result = get_reading_insights(sample_readings)
        
        assert result["total_journals"] == 3
        assert isinstance(result["insights"], list)
        assert len(result["insights"]) > 0
    
    def test_empty_readings(self, empty_readings):
        """Test with empty readings."""
        result = get_reading_insights(empty_readings)
        
        assert result["total_journals"] == 0
        assert result["best_scope"] is None
        assert result["journaling_streak"] == 0
    
    def test_journaling_streak_detection(self):
        """Test journaling streak counting."""
        today = datetime.now().date()
        readings = [
            {"id": 1, "date": today.isoformat(), "journal": "Entry 1", "feedback": "yes"},
            {"id": 2, "date": (today - timedelta(days=1)).isoformat(), "journal": "Entry 2", "feedback": "yes"},
            {"id": 3, "date": (today - timedelta(days=2)).isoformat(), "journal": "Entry 3", "feedback": "yes"},
        ]
        result = get_reading_insights(readings)
        
        assert result["journaling_streak"] == 3
    
    def test_broken_streak(self):
        """Test broken journaling streak."""
        today = datetime.now().date()
        readings = [
            {"id": 1, "date": today.isoformat(), "journal": "Entry 1", "feedback": "yes"},
            # Gap on day 1
            {"id": 2, "date": (today - timedelta(days=2)).isoformat(), "journal": "Entry 2", "feedback": "yes"},
        ]
        result = get_reading_insights(readings)
        
        assert result["journaling_streak"] == 1


# =============================================================================
# Test analyze_prediction_patterns
# =============================================================================

class TestAnalyzePredictionPatterns:
    """Tests for analyze_prediction_patterns function."""
    
    def test_with_sample_readings(self, sample_readings):
        """Test pattern analysis with sample data."""
        result = analyze_prediction_patterns(sample_readings)
        
        assert "patterns_found" in result
        assert "by_day" in result
        assert isinstance(result["sample_size"], int)
    
    def test_insufficient_data(self):
        """Test with insufficient data."""
        readings = [
            {"id": 1, "scope": "daily", "date": "2024-01-01", "feedback": "yes"},
        ]
        result = analyze_prediction_patterns(readings)
        
        assert result["patterns_found"] == False
        assert "Need at least 3" in result["message"]
    
    def test_day_of_week_patterns(self):
        """Test day-of-week pattern detection."""
        # Create readings across different days
        base = datetime(2024, 1, 8)  # Monday
        readings = [
            {"id": 1, "date": base.isoformat(), "feedback": "yes"},  # Monday
            {"id": 2, "date": (base + timedelta(days=7)).isoformat(), "feedback": "yes"},  # Monday
            {"id": 3, "date": (base + timedelta(days=1)).isoformat(), "feedback": "no"},  # Tuesday
            {"id": 4, "date": (base + timedelta(days=8)).isoformat(), "feedback": "no"},  # Tuesday
        ]
        result = analyze_prediction_patterns(readings)
        
        assert "by_day" in result
        if "Monday" in result["by_day"]:
            assert result["by_day"]["Monday"] == 100.0
        if "Tuesday" in result["by_day"]:
            assert result["by_day"]["Tuesday"] == 0.0


# =============================================================================
# Test get_journal_prompts
# =============================================================================

class TestGetJournalPrompts:
    """Tests for get_journal_prompts function."""
    
    def test_daily_prompts(self):
        """Test daily journal prompts."""
        prompts = get_journal_prompts("daily")
        
        assert len(prompts) >= 3
        assert all("text" in p and "category" in p for p in prompts)
    
    def test_weekly_prompts(self):
        """Test weekly journal prompts."""
        prompts = get_journal_prompts("weekly")
        
        assert len(prompts) >= 3
        assert any("week" in p["text"].lower() for p in prompts)
    
    def test_monthly_prompts(self):
        """Test monthly journal prompts."""
        prompts = get_journal_prompts("monthly")
        
        assert len(prompts) >= 3
        assert any("month" in p["text"].lower() for p in prompts)
    
    def test_theme_specific_prompts(self):
        """Test theme-specific prompt additions."""
        prompts = get_journal_prompts("daily", ["love", "career"])
        
        # Should have base prompts + theme prompts
        assert len(prompts) >= 4
    
    def test_invalid_scope_fallback(self):
        """Test fallback to daily for invalid scope."""
        prompts = get_journal_prompts("invalid")
        
        assert len(prompts) >= 3


# =============================================================================
# Test create_accountability_report
# =============================================================================

class TestCreateAccountabilityReport:
    """Tests for create_accountability_report function."""
    
    def test_with_sample_readings(self, sample_readings):
        """Test report generation with sample data."""
        result = create_accountability_report(sample_readings, "month")
        
        assert result["period"] == "month"
        assert "generated_at" in result
        assert "summary" in result
        assert "accuracy" in result
        assert "insights" in result
        assert "patterns" in result
        assert "recommendations" in result
    
    def test_summary_section(self, sample_readings):
        """Test summary section of report."""
        result = create_accountability_report(sample_readings, "week")
        summary = result["summary"]
        
        assert summary["total_readings"] == 5
        assert summary["with_feedback"] == 4
        assert summary["with_journal"] == 3
        assert "engagement_score" in summary
        assert "engagement_rating" in summary
    
    def test_empty_report(self, empty_readings):
        """Test report with no readings."""
        result = create_accountability_report(empty_readings, "month")
        
        assert result["summary"]["total_readings"] == 0
        assert result["summary"]["engagement_score"] == 0
    
    def test_recommendations_generated(self, sample_readings):
        """Test recommendations are generated."""
        result = create_accountability_report(sample_readings, "month")
        
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0


# =============================================================================
# Test format_reading_for_journal
# =============================================================================

class TestFormatReadingForJournal:
    """Tests for format_reading_for_journal function."""
    
    def test_basic_formatting(self):
        """Test basic reading formatting."""
        reading = {
            "id": 1,
            "scope": "daily",
            "date": "2024-01-15",
            "content": '{"theme": "New beginnings"}',
            "feedback": "yes",
            "journal": "Great day!"
        }
        result = format_reading_for_journal(reading)
        
        assert result["id"] == 1
        assert result["scope"] == "daily"
        assert result["scope_label"] == "Daily"
        assert result["has_journal"] == True
        assert result["feedback_emoji"] == "✅"
    
    def test_json_content_parsing(self):
        """Test JSON content is parsed."""
        reading = {
            "id": 1,
            "scope": "weekly",
            "date": "2024-01-15",
            "content": '{"summary": "Focus week"}',
            "feedback": None,
            "journal": ""
        }
        result = format_reading_for_journal(reading)
        
        assert result["content_summary"] == "Focus week"
    
    def test_long_journal_preview(self):
        """Test long journal is truncated in preview."""
        long_journal = "x" * 150
        reading = {
            "id": 1,
            "scope": "daily",
            "date": "2024-01-15",
            "content": "{}",
            "feedback": "partial",
            "journal": long_journal
        }
        result = format_reading_for_journal(reading)
        
        assert len(result["journal_preview"]) == 103  # 100 + "..."
        assert result["journal_full"] == long_journal
    
    def test_date_formatting(self):
        """Test date is formatted nicely."""
        reading = {
            "id": 1,
            "scope": "daily",
            "date": "2024-01-15T10:30:00",
            "content": "{}",
            "feedback": None,
            "journal": ""
        }
        result = format_reading_for_journal(reading)
        
        assert result["formatted_date"] == "January 15, 2024"


# =============================================================================
# Test READING_CATEGORIES and FEEDBACK_EMOJI
# =============================================================================

class TestConstants:
    """Tests for module constants."""
    
    def test_reading_categories_exist(self):
        """Test reading categories are defined."""
        assert len(READING_CATEGORIES) >= 5
        assert "transits" in READING_CATEGORIES
        assert "numerology" in READING_CATEGORIES
    
    def test_feedback_emoji_mapping(self):
        """Test feedback emoji mapping."""
        assert FEEDBACK_EMOJI["yes"] == "✅"
        assert FEEDBACK_EMOJI["no"] == "❌"
        assert FEEDBACK_EMOJI["partial"] == "🔶"
        assert FEEDBACK_EMOJI["pending"] == "⏳"


# =============================================================================
# Test API Endpoints (Mock)
# =============================================================================

class TestJournalAPIEndpoints:
    """Tests for Journal API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.app.main import api
        return TestClient(api)
    
    def test_get_prompts_daily(self, client):
        """Test getting daily journal prompts."""
        response = client.get("/journal/prompts?scope=daily")
        
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "daily"
        assert len(data["prompts"]) >= 3
    
    def test_get_prompts_weekly(self, client):
        """Test getting weekly journal prompts."""
        response = client.get("/journal/prompts?scope=weekly")
        
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "weekly"
    
    def test_get_prompts_with_themes(self, client):
        """Test getting prompts with themes."""
        response = client.get("/journal/prompts?scope=daily&themes=love,career")
        
        assert response.status_code == 200
        data = response.json()
        # Should have extra prompts for themes
        assert len(data["prompts"]) >= 4
    
    def test_get_prompts_invalid_scope(self, client):
        """Test invalid scope returns 422."""
        response = client.get("/journal/prompts?scope=invalid")
        
        assert response.status_code == 422
    
    def test_authenticated_endpoints_require_auth(self, client):
        """Test authenticated endpoints return 401 without auth."""
        # These should require authentication
        endpoints = [
            ("/journal/readings/1", "GET"),
            ("/journal/reading/1", "GET"),
            ("/journal/stats/1", "GET"),
            ("/journal/patterns/1", "GET"),
        ]
        
        for url, method in endpoints:
            if method == "GET":
                response = client.get(url)
            else:
                response = client.post(url)
            
            # Should be 401 or 403 (unauthorized)
            assert response.status_code in [401, 403, 422], f"Endpoint {url} should require auth"
    
    def test_post_entry_requires_auth(self, client):
        """Test POST /journal/entry requires authentication."""
        response = client.post(
            "/journal/entry",
            json={"reading_id": 1, "entry": "Test entry"}
        )
        
        assert response.status_code in [401, 403]
    
    def test_post_outcome_requires_auth(self, client):
        """Test POST /journal/outcome requires authentication."""
        response = client.post(
            "/journal/outcome",
            json={"reading_id": 1, "outcome": "yes"}
        )
        
        assert response.status_code in [401, 403]


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_malformed_date_handling(self):
        """Test handling of malformed dates."""
        readings = [
            {"id": 1, "scope": "daily", "date": "not-a-date", "feedback": "yes"},
            {"id": 2, "scope": "daily", "date": "", "feedback": "no"},
        ]
        # Should not raise exception
        result = calculate_accuracy_stats(readings)
        assert result["total_readings"] == 2
    
    def test_malformed_json_content(self):
        """Test handling of malformed JSON content."""
        reading = {
            "id": 1,
            "scope": "daily",
            "date": "2024-01-15",
            "content": "not valid json {",
            "feedback": "yes",
            "journal": ""
        }
        result = format_reading_for_journal(reading)
        
        # Should handle gracefully
        assert result["id"] == 1
    
    def test_unicode_journal_entry(self):
        """Test Unicode in journal entries."""
        result = add_journal_entry(1, "今日は素晴らしい日でした! 🌟✨")
        
        assert "今日は" in result["entry"]
        assert result["character_count"] > 0
    
    def test_very_large_readings_list(self):
        """Test with large number of readings."""
        base = datetime.now()
        readings = [
            {
                "id": i,
                "scope": "daily",
                "date": (base - timedelta(days=i)).isoformat(),
                "feedback": "yes" if i % 3 == 0 else "no" if i % 3 == 1 else "partial",
                "journal": f"Entry {i}" if i % 2 == 0 else ""
            }
            for i in range(500)
        ]
        
        # Should complete in reasonable time
        result = create_accountability_report(readings, "year")
        assert result["summary"]["total_readings"] == 500
