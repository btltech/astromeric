"""
compatibility.py
Builds a compatibility report using synastry and numerology between two profiles.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from ..chart_service import build_natal_chart
from ..rule_engine import RuleEngine
from ..numerology_engine import build_numerology


def build_compatibility(person_a: Dict, person_b: Dict) -> Dict:
    chart_a = build_natal_chart(person_a)
    chart_b = build_natal_chart(person_b)
    numerology_a = build_numerology(person_a["name"], person_a["date_of_birth"], datetime.utcnow())
    numerology_b = build_numerology(person_b["name"], person_b["date_of_birth"], datetime.utcnow())
    engine = RuleEngine()
    result = engine.evaluate(
        "compatibility_romantic",
        chart_a,
        numerology=None,
        comparison_chart=chart_b,
        synastry_priority=_synastry_priority_pairs(),
    )
    return {
        "people": [
            {"name": person_a["name"], "dob": person_a["date_of_birth"]},
            {"name": person_b["name"], "dob": person_b["date_of_birth"]},
        ],
        "topic_scores": result["topic_scores"],
        "highlights": [b["source"] + ": " + b["text"] for b in result["selected_blocks"][:6]],
        "numerology": {"a": numerology_a, "b": numerology_b},
    }


def _synastry_priority_pairs():
    return [
        "Sun-Sun",
        "Sun-Moon",
        "Moon-Moon",
        "Moon-Venus",
        "Venus-Mars",
        "Sun-Asc",
        "Moon-Asc",
        "Sun-MC",
        "Moon-MC",
        "Mercury-Mercury",
        "Mars-Mars",
        "Saturn-Sun",
        "Saturn-Moon",
    ]
