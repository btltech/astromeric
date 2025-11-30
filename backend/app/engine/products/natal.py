from __future__ import annotations

from typing import Dict, Optional

from ..charts.engine import ChartEngine
from ..charts.models import Chart
from ..numerology import calculate_life_path_number
from ..numerology_extended import (
    calculate_expression_number,
    calculate_maturity_number,
    calculate_personality_number,
    calculate_soul_urge_number,
)
from ..rules import RuleEngine, RuleResult
from .types import ProfileInput
from .utils import build_chart_request


def _section_from_result(title: str, result: RuleResult, limit: int = 5) -> Dict:
    ordered = sorted(result.factors, key=lambda f: f.score, reverse=True)[:limit]
    highlights = [
        f"{f.label}: {f.meaning.text if f.meaning else ''}".strip() for f in ordered
    ]
    return {
        "title": title,
        "highlights": highlights,
        "topic_scores": result.topic_scores,
        "factors": [f.as_dict() for f in ordered],
    }


def _build_numerology(profile: ProfileInput) -> Dict:
    life_path = calculate_life_path_number(profile.date_of_birth)
    expression = calculate_expression_number(profile.name)
    soul = calculate_soul_urge_number(profile.name)
    personality = calculate_personality_number(profile.name)
    maturity = calculate_maturity_number(life_path, expression)
    return {
        "life_path": {"number": life_path, "label": "Life Path"},
        "expression": {"number": expression, "label": "Expression"},
        "soul_urge": {"number": soul, "label": "Soul Urge"},
        "personality": {"number": personality, "label": "Personality"},
        "maturity": {"number": maturity, "label": "Maturity"},
    }


def build_natal_profile(
    profile: ProfileInput,
    chart_engine: Optional[ChartEngine] = None,
    rule_engine: Optional[RuleEngine] = None,
) -> Dict:
    """Build structured natal profile using the shared engines."""
    chart_engine = chart_engine or ChartEngine()
    rule_engine = rule_engine or RuleEngine()

    chart_request = build_chart_request(profile, chart_type="natal")
    chart: Chart = chart_engine.compute_chart(chart_request)
    numerology = _build_numerology(profile)

    general = rule_engine.evaluate("natal_general", chart, numerology=numerology)
    love = rule_engine.evaluate(
        "natal_love", chart, numerology={"soul_urge": numerology["soul_urge"]}
    )
    career = rule_engine.evaluate(
        "natal_career", chart, numerology={"expression": numerology["expression"]}
    )

    return {
        "profile": {
            "name": profile.name,
            "dob": profile.date_of_birth,
            "time": profile.time_of_birth,
            "location": {
                "lat": profile.latitude,
                "lon": profile.longitude,
                "tz": profile.timezone,
            },
        },
        "chart": {
            "metadata": {
                "chart_type": chart.chart_type,
                "datetime": chart.datetime.isoformat(),
                "location": chart.location.__dict__,
                "provider": chart.metadata.get("provider"),
            },
            "planets": [p.__dict__ for p in chart.planets],
            "houses": [h.__dict__ for h in chart.houses],
            "aspects": [a.__dict__ for a in chart.aspects],
        },
        "sections": [
            _section_from_result("General personality", general),
            _section_from_result("Love & relationships", love),
            _section_from_result("Career & direction", career),
        ],
        "numerology": numerology,
    }
