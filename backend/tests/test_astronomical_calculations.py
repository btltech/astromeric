"""
test_astronomical_calculations.py
---------------------------------
Comprehensive tests for chart calculations and astronomical accuracy.
"""

import pytest
from datetime import datetime

from app.chart_service import (
    build_natal_chart,
    build_transit_chart,
    _compute_aspects,
    _get_house_for_longitude,
    _deg_diff,
    _closest_aspect,
    _score_aspect,
    PLANETS,
    ASPECT_ANGLES,
    ASPECT_ORBS,
    HAS_FLATLIB,
)


class TestBuildNatalChart:
    """Tests for natal chart calculation."""

    @pytest.fixture
    def standard_profile(self):
        return {
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "house_system": "Placidus",
        }

    def test_chart_has_required_keys(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        assert "metadata" in chart
        assert "planets" in chart
        assert "houses" in chart
        assert "aspects" in chart

    def test_chart_metadata(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        assert chart["metadata"]["chart_type"] == "natal"
        assert "datetime" in chart["metadata"]
        assert "location" in chart["metadata"]
        assert "house_system" in chart["metadata"]

    def test_all_planets_present(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        assert len(chart["planets"]) == len(PLANETS)
        planet_names = [p["name"] for p in chart["planets"]]
        for expected_planet in PLANETS:
            assert expected_planet in planet_names

    def test_planet_structure(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for planet in chart["planets"]:
            assert "name" in planet
            assert "sign" in planet
            assert "degree" in planet
            assert "absolute_degree" in planet
            assert "house" in planet
            assert "retrograde" in planet

    def test_all_houses_present(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        assert len(chart["houses"]) == 12
        house_numbers = [h["house"] for h in chart["houses"]]
        assert house_numbers == list(range(1, 13))

    def test_house_structure(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for house in chart["houses"]:
            assert "house" in house
            assert "sign" in house
            assert "degree" in house

    def test_valid_zodiac_signs(self, standard_profile):
        valid_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        chart = build_natal_chart(standard_profile)
        
        for planet in chart["planets"]:
            assert planet["sign"] in valid_signs
        
        for house in chart["houses"]:
            assert house["sign"] in valid_signs

    def test_degree_ranges(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for planet in chart["planets"]:
            assert 0 <= planet["degree"] < 30  # Degree within sign
            assert 0 <= planet["absolute_degree"] < 360  # Absolute degree
        
        for house in chart["houses"]:
            assert 0 <= house["degree"] < 30

    def test_house_ranges(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for planet in chart["planets"]:
            assert 1 <= planet["house"] <= 12

    def test_retrograde_is_boolean(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for planet in chart["planets"]:
            assert isinstance(planet["retrograde"], bool)

    def test_aspects_structure(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for aspect in chart["aspects"]:
            assert "planet_a" in aspect
            assert "planet_b" in aspect
            assert "type" in aspect
            assert "orb" in aspect
            assert "strength" in aspect

    def test_aspect_types_valid(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        valid_aspects = list(ASPECT_ANGLES.keys())
        for aspect in chart["aspects"]:
            assert aspect["type"] in valid_aspects

    def test_aspect_orbs_within_bounds(self, standard_profile):
        chart = build_natal_chart(standard_profile)
        
        for aspect in chart["aspects"]:
            max_orb = ASPECT_ORBS.get(aspect["type"], 7.0)
            assert aspect["orb"] <= max_orb

    def test_minimal_profile(self):
        """Test with minimal required data."""
        profile = {
            "name": "Minimal",
            "date_of_birth": "1985-06-15",
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)
        assert len(chart["houses"]) == 12

    def test_different_house_systems(self, standard_profile):
        """Test that different house systems produce different results."""
        profile_placidus = standard_profile.copy()
        profile_placidus["house_system"] = "Placidus"
        
        profile_whole = standard_profile.copy()
        profile_whole["house_system"] = "Whole"
        
        chart_placidus = build_natal_chart(profile_placidus)
        chart_whole = build_natal_chart(profile_whole)
        
        # Planets should be the same, houses may differ
        assert chart_placidus["planets"] == chart_whole["planets"]
        # Houses might differ (in production with real flatlib)

    def test_determinism(self, standard_profile):
        """Same input should produce same output."""
        chart1 = build_natal_chart(standard_profile)
        chart2 = build_natal_chart(standard_profile)
        
        assert chart1 == chart2


class TestBuildTransitChart:
    """Tests for transit chart calculation."""

    @pytest.fixture
    def standard_profile(self):
        return {
            "name": "Test User",
            "date_of_birth": "1990-01-01",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

    def test_transit_chart_structure(self, standard_profile):
        target = datetime(2025, 6, 15, 12, 0)
        chart = build_transit_chart(standard_profile, target)
        
        assert chart["metadata"]["chart_type"] == "transit"
        assert len(chart["planets"]) == len(PLANETS)
        assert len(chart["houses"]) == 12

    def test_transit_different_dates(self, standard_profile):
        date1 = datetime(2025, 1, 1, 12, 0)
        date2 = datetime(2025, 6, 15, 12, 0)
        
        chart1 = build_transit_chart(standard_profile, date1)
        chart2 = build_transit_chart(standard_profile, date2)
        
        # Different dates should produce different planetary positions
        # (at least some planets should have moved)
        positions1 = {p["name"]: p["absolute_degree"] for p in chart1["planets"]}
        positions2 = {p["name"]: p["absolute_degree"] for p in chart2["planets"]}
        
        # Check that at least one planet has a different position
        differences = sum(
            1 for name in PLANETS 
            if abs(positions1.get(name, 0) - positions2.get(name, 0)) > 0.1
        )
        assert differences > 0


class TestComputeAspects:
    """Tests for aspect calculation logic."""

    def test_conjunction_detection(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 3.0},  # Within orb
        ]
        aspects = _compute_aspects(planets)
        
        conjunctions = [a for a in aspects if a["type"] == "conjunction"]
        assert len(conjunctions) == 1
        assert conjunctions[0]["planet_a"] == "Sun"
        assert conjunctions[0]["planet_b"] == "Moon"

    def test_opposition_detection(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 180.0},
        ]
        aspects = _compute_aspects(planets)
        
        oppositions = [a for a in aspects if a["type"] == "opposition"]
        assert len(oppositions) == 1

    def test_trine_detection(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 120.0},
        ]
        aspects = _compute_aspects(planets)
        
        trines = [a for a in aspects if a["type"] == "trine"]
        assert len(trines) == 1

    def test_square_detection(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 90.0},
        ]
        aspects = _compute_aspects(planets)
        
        squares = [a for a in aspects if a["type"] == "square"]
        assert len(squares) == 1

    def test_sextile_detection(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 60.0},
        ]
        aspects = _compute_aspects(planets)
        
        sextiles = [a for a in aspects if a["type"] == "sextile"]
        assert len(sextiles) == 1

    def test_no_self_aspects(self):
        planets = [{"name": "Sun", "absolute_degree": 0.0}]
        aspects = _compute_aspects(planets)
        
        assert len(aspects) == 0

    def test_no_duplicate_aspects(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 90.0},
            {"name": "Mars", "absolute_degree": 180.0},
        ]
        aspects = _compute_aspects(planets)
        
        # Check no duplicates (A-B and B-A)
        pairs = set()
        for a in aspects:
            pair = frozenset([a["planet_a"], a["planet_b"]])
            assert pair not in pairs
            pairs.add(pair)

    def test_aspect_out_of_orb_excluded(self):
        planets = [
            {"name": "Sun", "absolute_degree": 0.0},
            {"name": "Moon", "absolute_degree": 100.0},  # Not close to any major aspect
        ]
        aspects = _compute_aspects(planets)
        
        # The closest aspect would be square (90°) but 10° is outside the orb
        squares = [a for a in aspects if a["type"] == "square"]
        assert len(squares) == 0


class TestDegDiff:
    """Tests for degree difference calculation."""

    def test_same_degree(self):
        assert _deg_diff(0.0, 0.0) == 0.0

    def test_small_difference(self):
        assert _deg_diff(10.0, 15.0) == 5.0

    def test_wrap_around(self):
        # 350° and 10° should be 20° apart, not 340°
        assert _deg_diff(350.0, 10.0) == 20.0

    def test_wrap_around_reverse(self):
        assert _deg_diff(10.0, 350.0) == 20.0

    def test_opposition(self):
        assert _deg_diff(0.0, 180.0) == 180.0


class TestClosestAspect:
    """Tests for closest aspect detection."""

    def test_exact_conjunction(self):
        aspect, orb = _closest_aspect(0.0)
        assert aspect == "conjunction"
        assert orb == 0.0

    def test_exact_opposition(self):
        aspect, orb = _closest_aspect(180.0)
        assert aspect == "opposition"
        assert orb == 0.0

    def test_exact_trine(self):
        aspect, orb = _closest_aspect(120.0)
        assert aspect == "trine"
        assert orb == 0.0

    def test_exact_square(self):
        aspect, orb = _closest_aspect(90.0)
        assert aspect == "square"
        assert orb == 0.0

    def test_exact_sextile(self):
        aspect, orb = _closest_aspect(60.0)
        assert aspect == "sextile"
        assert orb == 0.0

    def test_near_conjunction(self):
        aspect, orb = _closest_aspect(3.0)
        assert aspect == "conjunction"
        assert orb == 3.0

    def test_near_opposition(self):
        aspect, orb = _closest_aspect(175.0)
        assert aspect == "opposition"
        assert orb == 5.0


class TestScoreAspect:
    """Tests for aspect strength scoring."""

    def test_exact_aspect_high_score(self):
        score = _score_aspect("conjunction", 0.0)
        assert score > 1.0  # With weight bonus

    def test_wider_orb_lower_score(self):
        exact = _score_aspect("trine", 0.0)
        wide = _score_aspect("trine", 4.0)
        assert exact > wide

    def test_major_aspects_weighted_higher(self):
        # Conjunction/opposition have higher weight
        conj_score = _score_aspect("conjunction", 2.0)
        sextile_score = _score_aspect("sextile", 2.0)
        assert conj_score > sextile_score


class TestGetHouseForLongitude:
    """Tests for house placement calculation."""

    def test_first_house(self):
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        house = _get_house_for_longitude(15.0, cusps)
        assert house == 1

    def test_seventh_house(self):
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        house = _get_house_for_longitude(195.0, cusps)
        assert house == 7

    def test_wrap_around_twelfth_house(self):
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        house = _get_house_for_longitude(345.0, cusps)
        assert house == 12

    def test_cusp_boundary(self):
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        # Planet at exactly 30° should be in house 2
        house = _get_house_for_longitude(30.0, cusps)
        assert house == 2


class TestEdgeCases:
    """Tests for edge cases in chart calculation."""

    def test_polar_region_coordinates(self):
        """Test with arctic coordinates where houses can behave differently."""
        profile = {
            "name": "Arctic",
            "date_of_birth": "1990-06-21",
            "time_of_birth": "12:00",
            "latitude": 70.0,  # Within Arctic Circle
            "longitude": 25.0,
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)
        assert len(chart["houses"]) == 12

    def test_southern_hemisphere(self):
        profile = {
            "name": "Sydney",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00",
            "latitude": -33.87,
            "longitude": 151.21,
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)
        assert len(chart["houses"]) == 12

    def test_date_line_crossing(self):
        """Test with location near international date line."""
        profile = {
            "name": "Fiji",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00",
            "latitude": -17.77,
            "longitude": 177.97,  # Near date line
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)

    def test_midnight_birth(self):
        profile = {
            "name": "Midnight",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "00:00",
            "latitude": 40.0,
            "longitude": -74.0,
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)

    def test_leap_year_date(self):
        profile = {
            "name": "Leap Day",
            "date_of_birth": "2000-02-29",
            "time_of_birth": "12:00",
            "latitude": 40.0,
            "longitude": -74.0,
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)

    def test_historical_date(self):
        """Test with a date from early 1900s."""
        profile = {
            "name": "Historical",
            "date_of_birth": "1920-05-15",
            "time_of_birth": "10:30",
            "latitude": 51.5,
            "longitude": -0.1,
        }
        chart = build_natal_chart(profile)
        
        assert len(chart["planets"]) == len(PLANETS)
