from __future__ import annotations

from typing import Dict, Optional

from ..charts.engine import ChartEngine
from ..rules import RuleEngine, RuleResult
from ..compatibility import calculate_numerology_compatibility
from .types import ProfileInput
from .utils import build_chart_request
from .natal import _build_numerology, _section_from_result


def _compat_summary(result: RuleResult) -> Dict:
    ordered = sorted(result.factors, key=lambda f: f.score, reverse=True)
    strengths = [
        f.label for f in ordered if "support" in f.topic_scores or f.score > 0.6
    ][:5]
    challenges = [f.label for f in ordered if f.topic_scores.get("challenge")][:5]
    return {
        "topic_scores": result.topic_scores,
        "strengths": strengths,
        "challenges": challenges,
        "factors": [f.as_dict() for f in ordered[:8]],
    }


def build_compatibility_report(
    person_a: ProfileInput,
    person_b: ProfileInput,
    relationship_type: str = "romantic",
    chart_engine: Optional[ChartEngine] = None,
    rule_engine: Optional[RuleEngine] = None,
) -> Dict:
    chart_engine = chart_engine or ChartEngine()
    rule_engine = rule_engine or RuleEngine()

    chart_a = chart_engine.compute_chart(build_chart_request(person_a, "natal"))
    chart_b = chart_engine.compute_chart(build_chart_request(person_b, "natal"))
    synastry = chart_engine.build_synastry(chart_a, chart_b)

    numerology_a = _build_numerology(person_a)
    numerology_b = _build_numerology(person_b)
    numerology_pair = calculate_numerology_compatibility(
        person_a.name,
        person_a.date_of_birth,
        person_b.name,
        person_b.date_of_birth,
    )

    query = f"compatibility_{relationship_type}"
    result = rule_engine.evaluate(query, chart_a, synastry_aspects=synastry)

    return {
        "relationship_type": relationship_type,
        "people": [
            {
                "name": person_a.name,
                "dob": person_a.date_of_birth,
                "chart": {"planets": [p.__dict__ for p in chart_a.planets]},
            },
            {
                "name": person_b.name,
                "dob": person_b.date_of_birth,
                "chart": {"planets": [p.__dict__ for p in chart_b.planets]},
            },
        ],
        "synastry_aspects": [a.__dict__ for a in synastry],
        "summary": _compat_summary(result),
        "sections": [
            _section_from_result("Relationship dynamics", result, limit=6),
        ],
        "numerology": {
            "person_a": numerology_a,
            "person_b": numerology_b,
            "compatibility": numerology_pair,
        },
    }
