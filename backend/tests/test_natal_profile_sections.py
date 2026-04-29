from unittest.mock import patch

from app.products.natal_profile import build_natal_profile
from app.rule_engine import RuleEngine


def _sample_chart(birth_time_assumed: bool = False):
    return {
        "metadata": {"birth_time_assumed": birth_time_assumed},
        "planets": [
            {"name": "Sun", "sign": "Aries", "house": 9, "dignity": "exaltation"},
            {"name": "Venus", "sign": "Taurus", "house": 10, "dignity": "domicile"},
        ],
        "points": [
            {
                "name": "Part of Fortune",
                "sign": "Aries",
                "house": 9,
                "absolute_degree": 10.0314,
                "chart_type": "day",
            }
        ],
        "houses": [],
        "aspects": [],
    }


def _sample_numerology():
    return {
        "life_path": {
            "number": 1,
            "meaning": "Life Path 1 asks you to lead with courage.",
        },
        "expression": {
            "number": 8,
            "meaning": "Expression 8 supports disciplined ambition.",
        },
        "soul_urge": {
            "number": 6,
            "meaning": "Soul Urge 6 wants loyalty, care, and steadiness.",
        },
        "meaning_blocks": [],
    }


def test_natal_sections_use_ranked_themes_and_include_enriched_fields():
    result = {
        "selected_blocks": [
            {
                "source": "House 10",
                "text": "Low-value insertion-order block.",
                "weight": 0.1,
            },
            {
                "source": "Sun in Aries",
                "text": "Core self is bold and direct. Take initiative.",
                "weight": 1.4,
            },
            {
                "source": "Part of Fortune in Aries",
                "text": "Natural flow favors bold, visible action.",
                "weight": 1.3,
            },
        ],
        "top_themes": [
            {
                "source": "Sun in Aries",
                "text": "Core self is bold and direct. Take initiative.",
                "weight": 1.4,
            },
            {
                "source": "Part of Fortune in Aries",
                "text": "Natural flow favors bold, visible action.",
                "weight": 1.3,
            },
            {
                "source": "House 10",
                "text": "Low-value insertion-order block.",
                "weight": 0.1,
            },
        ],
        "topic_scores": {"general": 10.2, "love": 8.4, "career": 11.7},
    }

    class FakeRuleEngine:
        def evaluate(self, *args, **kwargs):
            return result

    with patch(
        "app.products.natal_profile.build_natal_chart", return_value=_sample_chart()
    ), patch(
        "app.products.natal_profile.build_numerology", return_value=_sample_numerology()
    ), patch(
        "app.products.natal_profile.RuleEngine", return_value=FakeRuleEngine()
    ):
        profile = {
            "name": "Jane",
            "date_of_birth": "1991-04-03",
            "time_of_birth": "14:30",
        }
        natal = build_natal_profile(profile)

    overview = natal["sections"][0]
    assert overview["highlights"][0].startswith("Sun in Aries:")
    assert overview["summary"]
    assert overview["affirmation"]
    assert 1 <= overview["rating"] <= 5


def test_birth_time_assumed_filters_house_specific_highlights():
    result = {
        "selected_blocks": [
            {
                "source": "Mars house 10",
                "text": "Your public drive is highly visible.",
                "weight": 1.5,
            },
            {
                "source": "North Node in Capricorn",
                "text": "Growth comes through disciplined ambition.",
                "weight": 1.2,
            },
        ],
        "top_themes": [
            {
                "source": "Mars house 10",
                "text": "Your public drive is highly visible.",
                "weight": 1.5,
            },
            {
                "source": "North Node in Capricorn",
                "text": "Growth comes through disciplined ambition.",
                "weight": 1.2,
            },
        ],
        "topic_scores": {"general": 7.0, "love": 5.0, "career": 8.0},
    }

    class FakeRuleEngine:
        def evaluate(self, *args, **kwargs):
            return result

    with patch(
        "app.products.natal_profile.build_natal_chart",
        return_value=_sample_chart(birth_time_assumed=True),
    ), patch(
        "app.products.natal_profile.build_numerology", return_value=_sample_numerology()
    ), patch(
        "app.products.natal_profile.RuleEngine", return_value=FakeRuleEngine()
    ):
        profile = {"name": "Jane", "date_of_birth": "1991-04-03"}
        natal = build_natal_profile(profile)

    overview = natal["sections"][0]
    assert all("house 10" not in item.lower() for item in overview["highlights"])
    assert "data_quality_note" in overview


def test_rule_engine_includes_chart_points_in_selected_blocks():
    chart = {
        "planets": [],
        "points": [
            {
                "name": "Part of Fortune",
                "sign": "Aries",
                "house": 9,
                "absolute_degree": 10.0314,
                "chart_type": "day",
            }
        ],
        "aspects": [],
    }

    result = RuleEngine().evaluate("natal_general", chart, numerology=None, lang="en")

    assert any(
        block["source"].startswith("Part of Fortune in Aries")
        for block in result["selected_blocks"]
    )
