"""
forecast.py
Builds daily/weekly forecasts using transit-to-natal aspects, numerology cycles, and rule engine.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from ..chart_service import build_natal_chart, build_transit_chart
from ..rule_engine import RuleEngine
from ..numerology_engine import build_numerology


def build_forecast(profile: Dict, scope: str = "daily") -> Dict:
    anchor = datetime.utcnow()
    natal = build_natal_chart(profile)
    transit = build_transit_chart(profile, anchor)
    numerology = build_numerology(profile["name"], profile["date_of_birth"], anchor)
    engine = RuleEngine()

    transit_filter = _transit_planets(scope)
    synastry_priority = _synastry_priority_pairs()

    result = engine.evaluate(
        f"{scope}_forecast",
        natal,
        numerology=numerology,
        comparison_chart=transit,
        transit_planet_filter=transit_filter,
        synastry_priority=synastry_priority,
    )

    smoothed = _smooth_topic_scores(
        profile,
        natal,
        numerology,
        anchor,
        scope,
        engine,
        transit_filter,
        synastry_priority,
    )

    return {
        "scope": scope,
        "date": anchor.date().isoformat(),
        "sections": _sections(result, smoothed),
        "theme": _top_theme(result),
        "numerology": numerology,
        "charts": {"natal": natal, "transit": transit},
        "ratings": _ratings(smoothed),
    }


def _sections(result: Dict, smoothed_scores: Dict) -> list:
    blocks = result["selected_blocks"]
    themes = [b["source"] + ": " + b["text"] for b in blocks[:5]]
    return [
        {"title": "Overview", "highlights": themes, "topic_scores": smoothed_scores},
    ]


def _top_theme(result: Dict) -> str:
    if not result["top_themes"]:
        return "Steady"
    return result["top_themes"][0]["text"]


def _ratings(topic_scores: Dict) -> Dict:
    ratings = {}
    for key, val in topic_scores.items():
        # Map to 1-5 with soft ceilings/floors
        scaled = 3 + max(-1.4, min(1.4, val))  # center at 3, compress extremes
        ratings[key] = max(1, min(5, int(round(scaled))))
    return ratings


def _smooth_topic_scores(
    profile: Dict,
    natal: Dict,
    numerology: Dict,
    anchor: datetime,
    scope: str,
    engine: RuleEngine,
    transit_filter: List[str],
    synastry_priority: List[str],
) -> Dict:
    # simple 3-point smoothing: day before, current, day after
    dates = [anchor - timedelta(days=1), anchor, anchor + timedelta(days=1)]
    scores_list = []
    for d in dates:
        transit = build_transit_chart(profile, d)
        res = engine.evaluate(
            f"{scope}_forecast",
            natal,
            numerology=numerology,
            comparison_chart=transit,
            transit_planet_filter=transit_filter,
            synastry_priority=synastry_priority,
        )
        scores_list.append(res["topic_scores"])
    smoothed: Dict[str, float] = {}
    for key in set().union(*scores_list):
        vals = [s.get(key, 0.0) for s in scores_list]
        smoothed[key] = round(sum(vals) / len(vals), 3)
    return smoothed


def _transit_planets(scope: str) -> List[str]:
    if scope == "daily":
        return ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    if scope == "weekly":
        return [
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
            "Sun",
            "Venus",
            "Mercury",
        ]
    return []


def _synastry_priority_pairs() -> List[str]:
    pairs = [
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
    ]
    return pairs
