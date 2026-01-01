from __future__ import annotations

from typing import Dict, Optional
from app.interpretation.translations import get_translation

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


def _section_from_result(title: str, result: RuleResult, limit: int = 5, lang: str = "en") -> Dict:
    ordered = sorted(result.factors, key=lambda f: f.score, reverse=True)[:limit]
    highlights = [
        f"{f.label}: {f.meaning.text if f.meaning else ''}".strip() for f in ordered
    ]
    
    # Localize title
    title_key_map = {
        "General personality": "general",
        "Love & relationships": "love",
        "Career & direction": "career"
    }
    key = f"section_title_{title_key_map.get(title, 'general')}"
    localized_title = get_translation(lang, "natal_sections", key)
    if not localized_title:
        localized_title = title
        
    return {
        "title": localized_title,
        "highlights": highlights,
        "topic_scores": result.topic_scores,
        "factors": [f.as_dict() for f in ordered],
    }


def _build_numerology(profile: ProfileInput, lang: str = "en") -> Dict:
    life_path = calculate_life_path_number(profile.date_of_birth)
    expression = calculate_expression_number(profile.name)
    soul = calculate_soul_urge_number(profile.name)
    personality = calculate_personality_number(profile.name)
    maturity = calculate_maturity_number(life_path, expression)
    
    def get_label(key, default):
        return get_translation(lang, "numerology_labels", key) or default

    return {
        "life_path": {"number": life_path, "label": get_label("life_path", "Life Path")},
        "expression": {"number": expression, "label": get_label("expression", "Expression")},
        "soul_urge": {"number": soul, "label": get_label("soul_urge", "Soul Urge")},
        "personality": {"number": personality, "label": get_label("personality", "Personality")},
        "maturity": {"number": maturity, "label": get_label("maturity", "Maturity")},
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
    lang = profile.language
    numerology = _build_numerology(profile, lang=lang)

    general = rule_engine.evaluate("natal_general", chart, numerology=numerology, lang=lang)
    love = rule_engine.evaluate(
        "natal_love", chart, numerology={"soul_urge": numerology["soul_urge"]}, lang=lang
    )
    career = rule_engine.evaluate(
        "natal_career", chart, numerology={"expression": numerology["expression"]}, lang=lang
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
            _section_from_result("General personality", general, lang=lang),
            _section_from_result("Love & relationships", love, lang=lang),
            _section_from_result("Career & direction", career, lang=lang),
        ],
        "numerology": numerology,
    }
