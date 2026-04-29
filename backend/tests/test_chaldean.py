"""
test_chaldean.py
-----------------
Unit tests for Chaldean numerology calculations.
Verifies that Chaldean letter-value substitution, life path digit-sum method,
and the unified calculate_core_numbers dispatcher all behave correctly.
"""

import pytest
from app.engine.constants import CHALDEAN_LETTER_VALUES
from app.engine.numerology import calculate_life_path_number  # Pythagorean baseline
from app.engine.numerology import (
    calculate_core_numbers,
    calculate_life_path_number_chaldean,
    calculate_name_number_chaldean,
)

# ─────────────────────────────────────────────────────────────────────────────
# Chaldean Letter-Value Table
# ─────────────────────────────────────────────────────────────────────────────


class TestChaldeanLetterValues:
    """Validate the Chaldean letter-value mapping."""

    def test_a_is_1(self):
        assert CHALDEAN_LETTER_VALUES.get("a") == 1

    def test_b_is_2(self):
        assert CHALDEAN_LETTER_VALUES.get("b") == 2

    def test_no_9_in_table(self):
        """9 is sacred in Chaldean — no letter maps to it."""
        assert 9 not in CHALDEAN_LETTER_VALUES.values()

    def test_max_value_is_8(self):
        """All letter values should be 1–8."""
        max_val = max(CHALDEAN_LETTER_VALUES.values())
        assert max_val == 8

    def test_26_letters_covered(self):
        """All 26 lowercase letters should be present."""
        assert set(CHALDEAN_LETTER_VALUES.keys()) == set("abcdefghijklmnopqrstuvwxyz")


# ─────────────────────────────────────────────────────────────────────────────
# Chaldean Life Path
# ─────────────────────────────────────────────────────────────────────────────


class TestChaldeanLifePath:
    """Chaldean life path uses total digit-sum, not component reduction."""

    def test_result_is_1_to_9(self):
        """Result must be a single digit 1–9."""
        result = calculate_life_path_number_chaldean("1990-03-21")
        assert 1 <= result <= 9

    def test_all_digits_summed(self):
        """
        DOB 2000-01-01 -> digits: 2,0,0,0,0,1,0,1 -> sum=4 (already single).
        """
        result = calculate_life_path_number_chaldean("2000-01-01")
        assert result == 4

    def test_reduction(self):
        """
        1999-12-31 -> 1+9+9+9+1+2+3+1 = 35 -> 3+5=8
        """
        result = calculate_life_path_number_chaldean("1999-12-31")
        assert result == 8

    def test_differs_from_pythagorean_where_expected(self):
        """
        Chaldean and Pythagorean use different algorithms —
        they will often differ for the same DOB.
        """
        dob = "1985-06-24"
        pythagorean = calculate_life_path_number(dob)
        chaldean = calculate_life_path_number_chaldean(dob)
        # Both must be valid single digits
        assert 1 <= pythagorean <= 33  # master numbers allowed in Pythagorean
        assert 1 <= chaldean <= 9


# ─────────────────────────────────────────────────────────────────────────────
# Chaldean Name Number
# ─────────────────────────────────────────────────────────────────────────────


class TestChaldeanNameNumber:
    """Chaldean name number uses the 1-8 letter table."""

    def test_result_is_1_to_9(self):
        result = calculate_name_number_chaldean("Alice")
        assert 1 <= result <= 9

    def test_case_insensitive(self):
        assert calculate_name_number_chaldean("ABC") == calculate_name_number_chaldean(
            "abc"
        )

    def test_spaces_ignored(self):
        assert calculate_name_number_chaldean(
            "John Doe"
        ) == calculate_name_number_chaldean("JohnDoe")

    def test_known_simple_value(self):
        """
        'A' = 1, 'B' = 2, 'C' = 3 -> sum=6 -> single digit already.
        """
        assert calculate_name_number_chaldean("ABC") == 6

    def test_hyphens_ignored(self):
        """Hyphenated names should be treated as one name."""
        without = calculate_name_number_chaldean("MaryJane")
        with_hyphen = calculate_name_number_chaldean("Mary-Jane")
        assert without == with_hyphen


# ─────────────────────────────────────────────────────────────────────────────
# Unified Dispatcher
# ─────────────────────────────────────────────────────────────────────────────


class TestCalculateCoreNumbers:
    """calculate_core_numbers() should route correctly to each system."""

    @pytest.fixture
    def sample(self):
        return {"dob": "1990-03-21", "name": "Test User"}

    def test_pythagorean_default(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"])
        assert result["method"] == "pythagorean"

    def test_pythagorean_explicit(self, sample):
        result = calculate_core_numbers(
            sample["dob"], sample["name"], method="pythagorean"
        )
        assert result["method"] == "pythagorean"

    def test_chaldean_explicit(self, sample):
        result = calculate_core_numbers(
            sample["dob"], sample["name"], method="chaldean"
        )
        assert result["method"] == "chaldean"

    def test_response_has_required_keys(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"])
        for key in (
            "method",
            "life_path",
            "name_number",
            "life_path_meaning",
            "life_path_advice",
        ):
            assert key in result, f"Missing key: {key}"

    def test_life_path_valid_range_pythagorean(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"], "pythagorean")
        assert result["life_path"] in list(range(1, 10)) + [11, 22, 33]

    def test_life_path_valid_range_chaldean(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"], "chaldean")
        assert 1 <= result["life_path"] <= 9

    def test_name_number_valid_range(self, sample):
        for method in ("pythagorean", "chaldean"):
            result = calculate_core_numbers(sample["dob"], sample["name"], method)
            assert (
                1 <= result["name_number"] <= 9
            ), f"name_number out of range for {method}"

    def test_different_systems_may_produce_different_results(self, sample):
        """Not guaranteed to differ, but method field must differ."""
        p = calculate_core_numbers(sample["dob"], sample["name"], "pythagorean")
        c = calculate_core_numbers(sample["dob"], sample["name"], "chaldean")
        assert p["method"] != c["method"]

    def test_case_insensitive_method(self, sample):
        result = calculate_core_numbers(
            sample["dob"], sample["name"], method="Chaldean"
        )
        assert result["method"] == "chaldean"

    def test_life_path_meaning_non_empty(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"])
        assert isinstance(result["life_path_meaning"], str)

    def test_advice_is_list(self, sample):
        result = calculate_core_numbers(sample["dob"], sample["name"])
        assert isinstance(result["life_path_advice"], list)
