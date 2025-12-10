"""
compatibility.py
Builds a compatibility report using synastry and numerology between two profiles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..chart_service import build_natal_chart
from ..numerology_engine import build_numerology
from ..rule_engine import RuleEngine


def build_compatibility(person_a: Dict, person_b: Dict) -> Dict:
    chart_a = build_natal_chart(person_a)
    chart_b = build_natal_chart(person_b)
    numerology_a = build_numerology(
        person_a["name"], person_a["date_of_birth"], datetime.now(timezone.utc)
    )
    numerology_b = build_numerology(
        person_b["name"], person_b["date_of_birth"], datetime.now(timezone.utc)
    )
    engine = RuleEngine()
    result = engine.evaluate(
        "compatibility_romantic",
        chart_a,
        numerology=None,
        comparison_chart=chart_b,
        synastry_priority=_synastry_priority_pairs(),
    )
    strengths, challenges = _split_synastry_blocks(result["selected_blocks"])
    return {
        "people": [
            {"name": person_a["name"], "dob": person_a["date_of_birth"]},
            {"name": person_b["name"], "dob": person_b["date_of_birth"]},
        ],
        "topic_scores": result["topic_scores"],
        "strengths": strengths,
        "challenges": challenges,
        "advice": _compatibility_advice(result["topic_scores"]),
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


def _split_synastry_blocks(blocks):
    strengths = []
    challenges = []
    for block in blocks:
        # Clean text only - no technical source prefixes
        entry = block['text']
        tags = block.get("tags", [])
        if "challenge" in tags or block["weights"].get("challenge", 0) > 0.5:
            challenges.append(entry)
        elif "support" in tags or block["weights"].get("love", 0) > 0.4:
            strengths.append(entry)
        if len(strengths) >= 5 and len(challenges) >= 5:
            break
    return strengths[:5], challenges[:5]


def _compatibility_advice(topic_scores: Dict[str, float]) -> str:
    love = topic_scores.get("love", 0)
    challenge = topic_scores.get("challenge", 0)
    if love >= challenge:
        return "Lean into the supportive aspects that already flow—celebrate what feels easy."
    return "Name the sticking points early and build structure around them so chemistry has room to grow."
