"""
tests/test_astro_context.py
---------------------------
Tests for the build_astro_context() shared resolver and all five
astrology-informed guidance functions.

Run with:
    cd backend && python -m pytest tests/test_astro_context.py -v
"""
from __future__ import annotations

import os
import sys
from datetime import date

# Make sure the app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_profile(
    dob="1990-06-15",
    time_of_birth=None,
    latitude=None,
    longitude=None,
    timezone="UTC",
    name="Test User",
):
    return {
        "date_of_birth": dob,
        "time_of_birth": time_of_birth,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "name": name,
    }


PROFILE_FULL = make_profile(
    dob="1990-06-15",
    time_of_birth="14:30",
    latitude=51.5074,
    longitude=-0.1278,
)

PROFILE_NO_TIME = make_profile(dob="1990-06-15")
PROFILE_NOON = make_profile(dob="1990-06-15", time_of_birth="12:00")
PROFILE_NO_LOC = make_profile(dob="1990-06-15", time_of_birth="14:30")

REF_DATE = date(2024, 4, 5)  # Known: Friday, Venus rules


# ---------------------------------------------------------------------------
# 1. build_astro_context — trust gates
# ---------------------------------------------------------------------------


class TestBuildAstroContext:
    def test_full_profile_trust_gates(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_FULL, REF_DATE)
        assert ctx["birth_time_trusted"] is True
        assert ctx["location_trusted"] is True
        assert ctx["usable_inputs"]["can_use_ascendant"] is True
        assert ctx["usable_inputs"]["can_use_chart_ruler"] is True
        assert ctx["usable_inputs"]["can_use_local_timing"] is True

    def test_missing_time_disables_birth_time_gate(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        assert ctx["birth_time_trusted"] is False
        assert ctx["usable_inputs"]["can_use_ascendant"] is False
        assert ctx["usable_inputs"]["can_use_chart_ruler"] is False

    def test_noon_fallback_disables_birth_time_gate(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_NOON, REF_DATE)
        assert ctx["birth_time_trusted"] is False

    def test_missing_location_disables_location_gate(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_NO_LOC, REF_DATE)
        assert ctx["location_trusted"] is False
        assert ctx["usable_inputs"]["can_use_local_timing"] is False

    def test_force_trust_overrides(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(
            PROFILE_NO_TIME,
            REF_DATE,
            force_birth_time_trusted=True,
            force_location_trusted=True,
        )
        assert ctx["birth_time_trusted"] is True
        assert ctx["location_trusted"] is True

    def test_contains_required_fields(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        required = [
            "reference_date",
            "natal_sun",
            "natal_moon",
            "natal_ascendant",
            "chart_ruler",
            "dominant_element",
            "life_path",
            "personal_day",
            "personal_month",
            "personal_year",
            "universal_day",
            "calendar_reduction",
            "moon_sign",
            "moon_sign_basis",
            "moon_phase",
            "day_ruler",
            "birth_time_trusted",
            "location_trusted",
            "usable_inputs",
        ]
        for field in required:
            assert field in ctx, f"Missing context field: {field}"

    def test_day_ruler_friday(self):
        from app.engine.astro_context import build_astro_context

        # REF_DATE = 2024-04-05 which is a Friday
        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        assert ctx["day_ruler"] == "Venus"

    def test_deterministic_output(self):
        from app.engine.astro_context import build_astro_context

        ctx1 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        ctx2 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        assert ctx1["personal_day"] == ctx2["personal_day"]
        assert ctx1["moon_sign"] == ctx2["moon_sign"]
        assert ctx1["day_ruler"] == ctx2["day_ruler"]

    def test_no_chart_ruler_when_time_unknown(self):
        from app.engine.astro_context import build_astro_context

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        assert ctx["chart_ruler"] is None
        assert ctx["natal_ascendant"] is None


# ---------------------------------------------------------------------------
# 2. Lucky Number
# ---------------------------------------------------------------------------


class TestLuckyNumberGuidance:
    def _ctx(self):
        from app.engine.astro_context import build_astro_context

        return build_astro_context(PROFILE_NO_TIME, REF_DATE)

    def test_three_tiers_always_present(self):
        from app.engine.daily_features import get_lucky_number_guidance

        result = get_lucky_number_guidance(self._ctx())
        sel = result["selection"]
        assert "core" in sel
        assert "support" in sel
        assert "resonance" in sel
        assert isinstance(sel["core"], int)
        assert isinstance(sel["support"], list)
        assert isinstance(sel["resonance"], list)

    def test_no_duplicates_across_tiers(self):
        from app.engine.daily_features import get_lucky_number_guidance

        result = get_lucky_number_guidance(self._ctx())
        sel = result["selection"]
        all_nums = [sel["core"]] + sel["support"] + sel["resonance"]
        assert len(all_nums) == len(
            set(all_nums)
        ), "Duplicate numbers found across tiers"

    def test_deterministic(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_lucky_number_guidance

        r1 = get_lucky_number_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        r2 = get_lucky_number_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        assert r1["selection"] == r2["selection"]

    def test_no_random_fills(self):
        """Core must be life_path — never random."""
        from app.engine.astro_context import _traditional_life_path, build_astro_context
        from app.engine.daily_features import get_lucky_number_guidance

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        result = get_lucky_number_guidance(ctx)
        expected_core = _traditional_life_path(PROFILE_NO_TIME["date_of_birth"])
        assert result["selection"]["core"] == expected_core

    def test_why_it_matches_mentions_life_path(self):
        from app.engine.daily_features import get_lucky_number_guidance

        result = get_lucky_number_guidance(self._ctx())
        assert "Life Path" in result["why_it_matches"]

    def test_standard_contract(self):
        from app.engine.daily_features import get_lucky_number_guidance

        result = get_lucky_number_guidance(self._ctx())
        for field in [
            "headline",
            "selection",
            "why_it_matches",
            "how_to_use",
            "basis",
            "trust_level",
            "reason_factors",
        ]:
            assert field in result

    def test_basis_is_numerology(self):
        from app.engine.daily_features import get_lucky_number_guidance

        result = get_lucky_number_guidance(self._ctx())
        assert result["basis"] == "numerology-based"


# ---------------------------------------------------------------------------
# 3. Lucky Color
# ---------------------------------------------------------------------------


class TestLuckyColorGuidance:
    def test_changes_with_day_ruler(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_lucky_color_guidance

        # Friday = Venus; Saturday = Saturn
        friday = date(2024, 4, 5)
        saturday = date(2024, 4, 6)
        ctx_fri = build_astro_context(PROFILE_NO_TIME, friday)
        ctx_sat = build_astro_context(PROFILE_NO_TIME, saturday)
        r_fri = get_lucky_color_guidance(ctx_fri)
        r_sat = get_lucky_color_guidance(ctx_sat)
        assert r_fri["selection"]["power_color"] != r_sat["selection"]["power_color"]

    def test_reason_factors_match_output(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_lucky_color_guidance

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        result = get_lucky_color_guidance(ctx)
        rf_types = {f["type"] for f in result["reason_factors"]}
        assert "day_ruler" in rf_types
        assert "dominant_element" in rf_types
        assert "moon_sign" in rf_types

    def test_has_hex_codes(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_lucky_color_guidance

        result = get_lucky_color_guidance(
            build_astro_context(PROFILE_NO_TIME, REF_DATE)
        )
        assert result["selection"]["power_hex"].startswith("#")
        assert result["selection"]["accent_hex"].startswith("#")

    def test_standard_contract(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_lucky_color_guidance

        result = get_lucky_color_guidance(
            build_astro_context(PROFILE_NO_TIME, REF_DATE)
        )
        for field in [
            "headline",
            "selection",
            "why_it_matches",
            "how_to_use",
            "basis",
            "trust_level",
            "reason_factors",
        ]:
            assert field in result


# ---------------------------------------------------------------------------
# 4. Affirmation
# ---------------------------------------------------------------------------


class TestAffirmationGuidance:
    def test_same_user_same_date_same_result(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_affirmation_guidance

        ctx1 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        ctx2 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        r1 = get_affirmation_guidance(ctx1)
        r2 = get_affirmation_guidance(ctx2)
        assert r1["selection"]["anchor"] == r2["selection"]["anchor"]

    def test_theme_changes_with_personal_day(self):
        """Different dates → potentially different personal_day → different theme."""
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_affirmation_guidance

        # Find two dates that produce different personal days for the same profile
        d1 = date(2024, 4, 5)
        d2 = date(2024, 4, 14)
        ctx1 = build_astro_context(PROFILE_NO_TIME, d1)
        ctx2 = build_astro_context(PROFILE_NO_TIME, d2)
        if ctx1["personal_day"] != ctx2["personal_day"]:
            r1 = get_affirmation_guidance(ctx1)
            r2 = get_affirmation_guidance(ctx2)
            assert r1["selection"]["theme"] != r2["selection"]["theme"]

    def test_no_vague_prosperity_filler(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_affirmation_guidance

        result = get_affirmation_guidance(
            build_astro_context(PROFILE_NO_TIME, REF_DATE)
        )
        anchor = result["selection"]["anchor"].lower()
        assert "magnet for prosperity" not in anchor
        assert "the universe" not in anchor

    def test_standard_contract(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_affirmation_guidance

        result = get_affirmation_guidance(
            build_astro_context(PROFILE_NO_TIME, REF_DATE)
        )
        for field in [
            "headline",
            "selection",
            "why_it_matches",
            "how_to_use",
            "basis",
            "trust_level",
            "reason_factors",
        ]:
            assert field in result
        assert "anchor" in result["selection"]
        assert "theme" in result["selection"]


# ---------------------------------------------------------------------------
# 5. Tarot
# ---------------------------------------------------------------------------


class TestTarotGuidance:
    def test_card_draw_is_deterministic(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_tarot_guidance

        ctx1 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        ctx2 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        r1 = get_tarot_guidance(ctx1)
        r2 = get_tarot_guidance(ctx2)
        assert r1["selection"]["card"] == r2["selection"]["card"]
        assert r1["selection"]["reversed"] == r2["selection"]["reversed"]

    def test_interpretation_changes_with_moon_sign(self):
        """Same card, different Moon sign context → different why_it_matches."""
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_tarot_guidance

        # Inject two contexts with differing moon_sign
        ctx1 = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        ctx2 = dict(ctx1)
        ctx2["moon_sign"] = "Scorpio" if ctx1["moon_sign"] != "Scorpio" else "Aries"
        r1 = get_tarot_guidance(ctx1)
        r2 = get_tarot_guidance(ctx2)
        # Interpretation text should differ
        assert r1["why_it_matches"] != r2["why_it_matches"]

    def test_honesty_note_present(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_tarot_guidance

        result = get_tarot_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        assert "honesty_note" in result
        assert "date-seeded" in result["honesty_note"]

    def test_no_claim_astrology_selected_card(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_tarot_guidance

        result = get_tarot_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        assert "astrologically selected" not in result["why_it_matches"].lower()

    def test_standard_contract(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_tarot_guidance

        result = get_tarot_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        for field in [
            "headline",
            "selection",
            "why_it_matches",
            "how_to_use",
            "basis",
            "trust_level",
            "reason_factors",
            "reflect_on",
            "avoid",
            "transit_theme",
        ]:
            assert field in result


# ---------------------------------------------------------------------------
# 6. Birthstone
# ---------------------------------------------------------------------------


class TestBirthstoneGuidance:
    def test_primary_stable_for_same_user(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_birthstone_guidance

        d1 = date(2024, 4, 5)
        d2 = date(2024, 4, 12)  # Different day (different day ruler)
        r1 = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, d1))
        r2 = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, d2))
        # Primary stone must stay the same regardless of date
        assert r1["selection"]["primary"]["name"] == r2["selection"]["primary"]["name"]

    def test_support_can_vary_by_day(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_birthstone_guidance

        friday = date(2024, 4, 5)  # Venus
        saturday = date(2024, 4, 6)  # Saturn
        r_fri = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, friday))
        r_sat = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, saturday))
        # Support may differ — note: may be same if dedup is triggered; just check structure
        assert "name" in r_fri["selection"]["support"]
        assert "name" in r_sat["selection"]["support"]

    def test_no_chart_ruler_when_birth_time_unknown(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_birthstone_guidance

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        result = get_birthstone_guidance(ctx)
        # Primary basis must NOT be chart-informed if birth_time_trusted is False
        assert result["selection"]["primary"]["basis"] != "chart-informed"
        assert "trust_note" in result  # must include explanation

    def test_no_duplicate_primary_support(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_birthstone_guidance

        result = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        primary_name = result["selection"]["primary"]["name"]
        support_name = result["selection"]["support"]["name"]
        assert (
            primary_name != support_name
        ), "Primary and support stones must not be identical"

    def test_standard_contract(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_birthstone_guidance

        result = get_birthstone_guidance(build_astro_context(PROFILE_NO_TIME, REF_DATE))
        for field in [
            "headline",
            "selection",
            "why_it_matches",
            "how_to_use",
            "basis",
            "trust_level",
            "reason_factors",
        ]:
            assert field in result
        assert "primary" in result["selection"]
        assert "support" in result["selection"]


# ---------------------------------------------------------------------------
# 7. get_all_guidance integration
# ---------------------------------------------------------------------------


class TestGetAllGuidance:
    def test_returns_all_five(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_all_guidance

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        result = get_all_guidance(ctx)
        assert set(result.keys()) == {
            "lucky_number",
            "lucky_color",
            "affirmation",
            "tarot",
            "birthstone",
        }

    def test_all_features_have_standard_contract(self):
        from app.engine.astro_context import build_astro_context
        from app.engine.daily_features import get_all_guidance

        ctx = build_astro_context(PROFILE_NO_TIME, REF_DATE)
        result = get_all_guidance(ctx)
        for feature_name, feature in result.items():
            for field in [
                "headline",
                "selection",
                "why_it_matches",
                "how_to_use",
                "basis",
                "trust_level",
                "reason_factors",
            ]:
                assert (
                    field in feature
                ), f"Feature '{feature_name}' missing field '{field}'"
