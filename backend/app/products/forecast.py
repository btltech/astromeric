"""
forecast.py
Builds daily/weekly forecasts using transit-to-natal aspects, numerology cycles, and rule engine.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from ..chart_service import build_natal_chart, build_transit_chart
from ..numerology_engine import build_numerology
from ..rule_engine import RuleEngine


def build_forecast(profile: Dict, scope: str = "daily") -> Dict:
    anchor = datetime.now(timezone.utc)
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
        "sections": _sections(result, smoothed, numerology),
        "theme": _top_theme(result),
        "numerology": numerology,
        "charts": {"natal": natal, "transit": transit},
        "ratings": _ratings(smoothed, numerology),
    }


def _sections(result: Dict, smoothed_scores: Dict, numerology: Dict) -> list:
    blocks = result["selected_blocks"]
    sections = []
    sections.append(
        _topic_section("Overview", None, blocks, smoothed_scores, numerology)
    )
    sections.append(
        _topic_section(
            "Love & Relationships", "love", blocks, smoothed_scores, numerology
        )
    )
    sections.append(
        _topic_section("Career & Money", "career", blocks, smoothed_scores, numerology)
    )
    sections.append(
        _topic_section(
            "Emotional & Spiritual", "emotional", blocks, smoothed_scores, numerology
        )
    )
    return sections


def _top_theme(result: Dict) -> str:
    if not result["top_themes"]:
        return "Steady"
    return result["top_themes"][0]["text"]


def _ratings(topic_scores: Dict, numerology: Dict) -> Dict:
    ratings = {}
    base = {"love": 2.0, "career": 1.8, "emotional": 2.0, "general": 1.9}
    bias = _numerology_bias(numerology)
    for key, val in topic_scores.items():
        scaled = base.get(key, 1.8) + max(-1.2, min(1.2, val)) + bias.get(key, 0.0)
        floor = 2 if key == "love" else 1
        ratings[key] = max(floor, min(5, int(round(scaled))))
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
    if scope == "weekly":
        delta = 3
    elif scope == "monthly":
        delta = 10
    else:
        delta = 1
    dates = [anchor - timedelta(days=delta), anchor, anchor + timedelta(days=delta)]
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
    if scope == "monthly":
        return [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
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
        "Saturn-Sun",
        "Saturn-Moon",
        "Mercury-Sun",
        "Mercury-Moon",
        "Saturn-Venus",
    ]
    return pairs


def _topic_section(
    title: str,
    topic_key: Optional[str],
    blocks: List[Dict],
    scores: Dict,
    numerology: Dict,
) -> Dict:
    if topic_key:
        relevant = [
            b
            for b in blocks
            if topic_key in b.get("weights", {}) or topic_key in b.get("tags", [])
        ]
    else:
        relevant = blocks
    highlights = [b["source"] + ": " + b["text"] for b in relevant[:4]]
    numerology_note = _numerology_hook(topic_key, numerology)
    if numerology_note:
        highlights.append(numerology_note)
    return {
        "title": title,
        "highlights": highlights or ["Quiet sky; stay present."],
        "topic_scores": scores,
    }


def _numerology_bias(numerology: Dict) -> Dict[str, float]:
    biases = {"love": 0.0, "career": 0.0, "emotional": 0.0, "general": 0.0}
    pd = numerology.get("cycles", {}).get("personal_day", {}).get("number")
    if pd in [2, 6]:
        biases["love"] += 0.2
    if pd in [8, 4]:
        biases["career"] += 0.2
    if pd in [7, 9]:
        biases["emotional"] += 0.2
    return biases


def _numerology_hook(topic: Optional[str], numerology: Dict) -> Optional[str]:
    if not topic:
        return None
    key_map = {
        "love": "personal_day",
        "career": "personal_year",
        "emotional": "personal_month",
    }
    target = key_map.get(topic)
    if not target:
        return None
    cycle = numerology.get("cycles", {}).get(target)
    if not cycle:
        return None
    number = cycle.get("number")
    meaning = cycle.get("meaning")
    if number is None or not meaning:
        return None
    return f"Numerology {target.replace('_', ' ')} {number}: {meaning}"
