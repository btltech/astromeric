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
    birth_time_assumed = chart["metadata"].get("birth_time_assumed", False)
    numerology = build_numerology(
        profile["name"], profile["date_of_birth"], datetime.now(timezone.utc)
    )
    engine = RuleEngine()
    general = engine.evaluate("natal_general", chart, numerology=numerology, lang=lang)
    love = engine.evaluate("natal_love", chart, numerology=numerology, lang=lang)
    career = engine.evaluate("natal_career", chart, numerology=numerology, lang=lang)

    sections = [
        _section("Overview", general, birth_time_assumed),
        _section("Love & Relationships", love, birth_time_assumed),
        _section("Career & Money", career, birth_time_assumed),
    ]

    return {
        "metadata": chart["metadata"],
        "sections": sections,
        "numerology": numerology,
        "chart": chart,
    }


def _section(title: str, result: Dict, birth_time_assumed: bool = False) -> Dict:
    highlights = [b["source"] + ": " + b["text"] for b in result["selected_blocks"][:3]]

    # When birth time is unknown, filter out house-specific interpretations
    # so we don't mislead users with inaccurate house placements.
    if birth_time_assumed:
        highlights = [
            h for h in highlights
            if not any(
                kw in h.lower()
                for kw in ["house", "ascendant", "rising", "midheaven", "angular"]
            )
        ] or highlights[:1]  # always keep at least one highlight

    section = {
        "title": title,
        "topic_scores": result["topic_scores"],
        "highlights": highlights,
        "top_themes": result["top_themes"],
    }
    if birth_time_assumed:
        section["data_quality_note"] = (
            "This reading is based on your Sun and Moon signs. "
            "Add your exact birth time for house-specific insights."
        )
    return section
