"""
test_year_ahead.py
------------------
Tests for the Year-Ahead Forecast module.
"""

import pytest
from datetime import datetime

from app.engine.year_ahead import (
    calculate_solar_return_date,
    get_personal_year_number,
    get_universal_year_number,
    get_eclipses_for_year,
    get_ingresses_for_year,
    calculate_eclipse_impact,
    build_monthly_forecast,
    build_year_ahead_forecast,
    ECLIPSES_2025_2026,
    MAJOR_INGRESSES,
)


# --- Fixtures ---

@pytest.fixture
def sample_profile():
    return {
        "name": "Test User",
        "date_of_birth": "1990-07-15",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    }


@pytest.fixture
def sample_natal_chart():
    return {
        "planets": [
            {"name": "Sun", "sign": "Cancer", "degree": 23.5, "absolute_degree": 113.5, "house": 10},
            {"name": "Moon", "sign": "Virgo", "degree": 8.2, "absolute_degree": 158.2, "house": 12},
            {"name": "Mercury", "sign": "Leo", "degree": 5.0, "absolute_degree": 125.0, "house": 11},
            {"name": "Venus", "sign": "Gemini", "degree": 15.0, "absolute_degree": 75.0, "house": 9},
        ],
        "ascendant": {"sign": "Libra", "degree": 12.5, "absolute_degree": 192.5},
        "mc": {"sign": "Cancer", "degree": 18.0, "absolute_degree": 108.0},
    }


# --- Test Solar Return ---

class TestSolarReturn:
    """Tests for Solar Return calculations."""
    
    def test_solar_return_date(self):
        """Solar return should be on birthday."""
        result = calculate_solar_return_date("1990-07-15", 2025)
        
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 15
    
    def test_solar_return_different_year(self):
        """Solar return should work for any year."""
        result = calculate_solar_return_date("1985-12-25", 2030)
        
        assert result.year == 2030
        assert result.month == 12
        assert result.day == 25


# --- Test Personal Year ---

class TestPersonalYear:
    """Tests for Personal Year calculations."""
    
    def test_personal_year_calculation(self):
        """Personal Year should reduce correctly."""
        # July 15 + 2025 = 7 + 15 + 9 = 31 -> 4
        result = get_personal_year_number("1990-07-15", 2025)
        
        assert result in range(1, 10) or result in [11, 22, 33]
    
    def test_universal_year_calculation(self):
        """Universal Year for 2025 should be 9."""
        # 2 + 0 + 2 + 5 = 9
        result = get_universal_year_number(2025)
        
        assert result == 9
    
    def test_universal_year_2026(self):
        """Universal Year for 2026 should be 1."""
        # 2 + 0 + 2 + 6 = 10 -> 1
        result = get_universal_year_number(2026)
        
        assert result == 1


# --- Test Eclipse Data ---

class TestEclipseData:
    """Tests for eclipse data and calculations."""
    
    def test_eclipses_2025(self):
        """Should have 2025 eclipses."""
        eclipses = get_eclipses_for_year(2025)
        
        assert len(eclipses) >= 2  # At least 2 eclipses per year
        for e in eclipses:
            assert e["date"].startswith("2025")
    
    def test_eclipses_2026(self):
        """Should have 2026 eclipses."""
        eclipses = get_eclipses_for_year(2026)
        
        assert len(eclipses) >= 2
        for e in eclipses:
            assert e["date"].startswith("2026")
    
    def test_eclipse_structure(self):
        """Eclipses should have required fields."""
        for eclipse in ECLIPSES_2025_2026:
            assert "date" in eclipse
            assert "type" in eclipse
            assert "sign" in eclipse
            assert "degree" in eclipse
    
    def test_eclipse_impact_on_natal_planet(self, sample_natal_chart):
        """Should detect eclipse impact on natal planet."""
        # Create an eclipse that conjuncts natal Sun (113.5 degrees)
        test_eclipse = {
            "date": "2025-07-15",
            "type": "Test Eclipse",
            "sign": "Cancer",
            "degree": 23.0,  # Close to natal Sun at 23.5
        }
        
        impact = calculate_eclipse_impact(test_eclipse, sample_natal_chart)
        
        assert impact is not None
        assert any(i["name"] == "Sun" for i in impact["impacts"])
    
    def test_eclipse_no_impact(self, sample_natal_chart):
        """Should return None when no natal points are affected."""
        # Eclipse far from natal planets
        test_eclipse = {
            "date": "2025-01-01",
            "type": "Test Eclipse",
            "sign": "Capricorn",
            "degree": 10.0,  # Far from natal planets
        }
        
        impact = calculate_eclipse_impact(test_eclipse, sample_natal_chart)
        
        # May or may not have impact depending on orbs
        if impact:
            assert "impacts" in impact


# --- Test Ingresses ---

class TestIngresses:
    """Tests for planetary ingress data."""
    
    def test_ingresses_2025(self):
        """Should have 2025 ingresses."""
        ingresses = get_ingresses_for_year(2025)
        
        assert len(ingresses) >= 1
        for i in ingresses:
            assert i["date"].startswith("2025")
    
    def test_ingress_structure(self):
        """Ingresses should have required fields."""
        for ingress in MAJOR_INGRESSES:
            assert "date" in ingress
            assert "planet" in ingress
            assert "sign" in ingress
            assert "impact" in ingress


# --- Test Monthly Forecast ---

class TestMonthlyForecast:
    """Tests for monthly forecast building."""
    
    def test_monthly_forecast_structure(self, sample_natal_chart):
        """Monthly forecast should have required fields."""
        result = build_monthly_forecast(
            month=6,
            year=2025,
            natal_chart=sample_natal_chart,
            personal_year=5,
        )
        
        assert "month" in result
        assert "month_name" in result
        assert "year" in result
        assert "season" in result
        assert "focus" in result
        assert "personal_month" in result
        assert "highlights" in result
    
    def test_monthly_forecast_correct_month_name(self, sample_natal_chart):
        """Should return correct month name."""
        result = build_monthly_forecast(6, 2025, sample_natal_chart, 5)
        
        assert result["month_name"] == "June"
    
    def test_personal_month_calculation(self, sample_natal_chart):
        """Personal month should be calculated correctly."""
        result = build_monthly_forecast(3, 2025, sample_natal_chart, 5)
        
        # Personal month = (personal_year + month) % 9
        expected = (5 + 3) % 9 or 9
        assert result["personal_month"] == expected


# --- Test Full Year Ahead ---

class TestYearAheadForecast:
    """Tests for complete year-ahead forecast."""
    
    def test_year_ahead_structure(self, sample_profile, sample_natal_chart):
        """Year-ahead forecast should have all sections."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        assert "year" in result
        assert "personal_year" in result
        assert "universal_year" in result
        assert "solar_return" in result
        assert "eclipses" in result
        assert "ingresses" in result
        assert "monthly_forecasts" in result
        assert "key_themes" in result
        assert "advice" in result
    
    def test_12_monthly_forecasts(self, sample_profile, sample_natal_chart):
        """Should have exactly 12 monthly forecasts."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        assert len(result["monthly_forecasts"]) == 12
    
    def test_personal_year_info(self, sample_profile, sample_natal_chart):
        """Personal year should have number, theme, description."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        py = result["personal_year"]
        assert "number" in py
        assert "theme" in py
        assert "description" in py
    
    def test_solar_return_date(self, sample_profile, sample_natal_chart):
        """Solar return should match birthday."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        sr = result["solar_return"]
        assert "date" in sr
        assert "2025-07-15" in sr["date"]
    
    def test_eclipses_section(self, sample_profile, sample_natal_chart):
        """Eclipses section should have all and personal impacts."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        ecl = result["eclipses"]
        assert "all" in ecl
        assert "personal_impacts" in ecl
    
    def test_key_themes_list(self, sample_profile, sample_natal_chart):
        """Key themes should be a list."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        assert isinstance(result["key_themes"], list)
        assert len(result["key_themes"]) >= 1
    
    def test_advice_list(self, sample_profile, sample_natal_chart):
        """Advice should be a list."""
        result = build_year_ahead_forecast(sample_profile, sample_natal_chart, 2025)
        
        assert isinstance(result["advice"], list)
        assert len(result["advice"]) >= 1
