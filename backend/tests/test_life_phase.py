"""
test_life_phase.py
------------------
Unit tests for get_life_phase() engine function.

NOTE: get_life_phase() takes a date_of_birth string ("YYYY-MM-DD") and
computes the user's age as of today. Tests use carefully chosen DOBs so the
resulting age falls reliably within a known phase.

Phase reference (from _LIFE_PHASES):
  0–6   "The Awakening"
  7–13  "The Building Years"
  14–20 "The First Jupiter Return"
  21–27 "The Saturn Opposition"
  28–32 "The Saturn Return"
  33–38 "The Expansion"
  39–44 "The Midlife Crossing"
  45–50 "The Chiron Return"
  51–58 "The Second Saturn Return"
  59–70 "The Elder's Power"
  71+   "The Sage"
"""

from datetime import date

import pytest
from app.engine.year_ahead import get_life_phase

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def dob_for_age(target_age: int) -> str:
    """Return a DOB string that produces exactly target_age years old today."""
    today = date.today()
    birth_year = today.year - target_age
    # Use Jan 1 so it's always been the birthday already this year
    return f"{birth_year}-01-01"


# ─────────────────────────────────────────────────────────────────────────────
# Structure
# ─────────────────────────────────────────────────────────────────────────────


class TestGetLifePhaseStructure:
    """Verify the structure of the returned life phase dict."""

    def test_returns_dict(self):
        result = get_life_phase(dob_for_age(30))
        assert isinstance(result, dict)

    def test_has_current_phase(self):
        result = get_life_phase(dob_for_age(30))
        assert "current_phase" in result

    def test_current_phase_has_required_fields(self):
        phase = get_life_phase(dob_for_age(30))["current_phase"]
        for field in (
            "name",
            "age",
            "min_age",
            "max_age",
            "duration",
            "narrative",
            "keywords",
            "progress_pct",
        ):
            assert field in phase, f"Missing field: {field}"

    def test_next_phase_present_or_none(self):
        result = get_life_phase(dob_for_age(30))
        assert "next_phase" in result
        if result["next_phase"] is not None:
            for field in ("name", "begins_in_years", "begins_at_age", "preview"):
                assert field in result["next_phase"]

    def test_keywords_is_list(self):
        phase = get_life_phase(dob_for_age(30))["current_phase"]
        assert isinstance(phase["keywords"], list)
        assert len(phase["keywords"]) >= 1

    def test_narrative_is_non_empty_string(self):
        phase = get_life_phase(dob_for_age(30))["current_phase"]
        assert isinstance(phase["narrative"], str)
        assert len(phase["narrative"]) > 10

    def test_progress_pct_in_range(self):
        phase = get_life_phase(dob_for_age(30))["current_phase"]
        assert 0 <= phase["progress_pct"] <= 100

    def test_age_reflects_dob(self):
        """age field must equal the computed age from the DOB."""
        target = 30
        phase = get_life_phase(dob_for_age(target))["current_phase"]
        assert phase["age"] == target

    def test_min_max_age_ordered(self):
        phase = get_life_phase(dob_for_age(30))["current_phase"]
        assert phase["min_age"] <= phase["max_age"]


# ─────────────────────────────────────────────────────────────────────────────
# Age → Phase mapping
# ─────────────────────────────────────────────────────────────────────────────


class TestLifePhaseAgeRanges:
    """Test that the correct life phase name is returned for each age band."""

    @pytest.mark.parametrize(
        "age,expected_name",
        [
            (3, "The Awakening"),
            (10, "The Building Years"),
            (17, "The First Jupiter Return"),
            (24, "The Saturn Opposition"),
            (30, "The Saturn Return"),
            (35, "The Expansion"),
            (42, "The Midlife Crossing"),
            (47, "The Chiron Return"),
            (54, "The Second Saturn Return"),
            (65, "The Elder's Power"),
            (75, "The Sage"),
        ],
    )
    def test_phase_name_at_age(self, age, expected_name):
        result = get_life_phase(dob_for_age(age))
        name = result["current_phase"]["name"]
        assert (
            name == expected_name
        ), f"At age {age} expected '{expected_name}', got '{name}'"

    def test_age_within_min_max(self):
        """Current age must fall within its own phase's age band."""
        for age in [3, 10, 17, 24, 30, 35, 42, 47, 54, 65, 75]:
            phase = get_life_phase(dob_for_age(age))["current_phase"]
            assert phase["min_age"] <= age <= phase["max_age"], (
                f"Age {age} not within [{phase['min_age']}, {phase['max_age']}] "
                f"for phase '{phase['name']}'"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Progress percentage
# ─────────────────────────────────────────────────────────────────────────────


class TestLifePhaseProgress:
    """Verify progress_pct calculation logic."""

    def test_at_phase_start_low_progress(self):
        """At the very start of a phase (min_age), progress should be 0 or very low."""
        # "The Saturn Return" starts at 28
        result = get_life_phase(dob_for_age(28))
        phase = result["current_phase"]
        assert phase["name"] == "The Saturn Return"
        assert phase["progress_pct"] == 0

    def test_at_phase_end_high_progress(self):
        """Near the end of a phase, progress should be close to 100."""
        # "The Saturn Return" ends at 32
        result = get_life_phase(dob_for_age(32))
        phase = result["current_phase"]
        assert phase["name"] == "The Saturn Return"
        assert phase["progress_pct"] >= 75

    def test_midpoint_progress(self):
        """At the midpoint of a phase, progress should be ~50%."""
        # "The Expansion" is 33-38, midpoint ~35 or 36
        result = get_life_phase(dob_for_age(35))
        phase = result["current_phase"]
        assert phase["name"] == "The Expansion"
        # progress_pct = (35-33) / (38-33) * 100 = 40%
        assert 30 <= phase["progress_pct"] <= 60


# ─────────────────────────────────────────────────────────────────────────────
# Next phase teaser
# ─────────────────────────────────────────────────────────────────────────────


class TestLifePhaseNextPhase:
    """Verify next_phase teaser information is correct."""

    def test_next_phase_begins_after_current_max(self):
        """next_phase.begins_at_age must be > current phase's max_age."""
        result = get_life_phase(dob_for_age(30))
        if result["next_phase"]:
            assert (
                result["next_phase"]["begins_at_age"]
                > result["current_phase"]["max_age"]
            )

    def test_next_phase_preview_non_empty(self):
        result = get_life_phase(dob_for_age(25))
        if result["next_phase"]:
            assert len(result["next_phase"]["preview"]) > 5

    def test_next_phase_begins_in_years_positive(self):
        result = get_life_phase(dob_for_age(30))
        if result["next_phase"]:
            assert result["next_phase"]["begins_in_years"] > 0

    def test_sage_phase_has_no_next(self):
        """The Sage (age 75+) should have no next phase."""
        result = get_life_phase(dob_for_age(80))
        assert result["next_phase"] is None


# ─────────────────────────────────────────────────────────────────────────────
# Edge cases
# ─────────────────────────────────────────────────────────────────────────────


class TestLifePhaseEdgeCases:
    """Edge cases: very young, very old, invalid input."""

    def test_newborn(self):
        """A 1-year-old should be in The Awakening."""
        result = get_life_phase(dob_for_age(1))
        assert result["current_phase"] is not None
        assert result["current_phase"]["name"] == "The Awakening"

    def test_very_old_age(self):
        """A 90-year-old should still get The Sage."""
        result = get_life_phase(dob_for_age(90))
        assert result["current_phase"]["name"] == "The Sage"

    def test_invalid_dob_returns_fallback(self):
        """An invalid DOB string should not crash — fallback age 30 applies."""
        result = get_life_phase("not-a-date")
        assert result["current_phase"] is not None
        # Fallback age is 30 → The Saturn Return
        assert result["current_phase"]["name"] == "The Saturn Return"

    def test_exact_phase_start_boundary(self):
        """Age exactly at phase start (28 = Saturn Return start) lands in that phase."""
        result = get_life_phase(dob_for_age(28))
        assert result["current_phase"]["min_age"] == 28

    def test_exact_phase_end_boundary(self):
        """Age exactly at phase end (32 = Saturn Return end) still in that phase."""
        result = get_life_phase(dob_for_age(32))
        assert result["current_phase"]["name"] == "The Saturn Return"
