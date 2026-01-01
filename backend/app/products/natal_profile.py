"""
natal_profile.py
Builds a structured natal profile using chart + numerology + rule engine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..chart_service import build_natal_chart
from ..numerology_engine import build_numerology
from ..rule_engine import RuleEngine


def build_natal_profile(profile: Dict, lang: str = "en") -> Dict:
    chart = build_natal_chart(profile)
    numerology = build_numerology(
        profile["name"], profile["date_of_birth"], datetime.now(timezone.utc)
    )
    engine = RuleEngine()
    general = engine.evaluate("natal_general", chart, numerology=numerology, lang=lang)
    love = engine.evaluate("natal_love", chart, numerology=numerology, lang=lang)
    career = engine.evaluate("natal_career", chart, numerology=numerology, lang=lang)
    return {
        "metadata": chart["metadata"],
        "sections": [
            _section("Overview", general),
            _section("Love & Relationships", love),
            _section("Career & Money", career),
        ],
        "numerology": numerology,
        "chart": chart,
    }


def _section(title: str, result: Dict) -> Dict:
    return {
        "title": title,
        "topic_scores": result["topic_scores"],
        "highlights": [
            b["source"] + ": " + b["text"] for b in result["selected_blocks"][:3]
        ],
        "top_themes": result["top_themes"],
    }
