from __future__ import annotations

import hashlib
from typing import Dict, Optional

from ..charts.engine import ChartEngine
from ..interpretation import (
    ACTIONS,
    AFFIRMATIONS,
    ASPECT_TEMPLATES,
    HOUSE_BLURBS,
    NUMEROLOGY_OVERLAYS,
    PLANET_TONES,
)
from ..numerology_extended import (
    calculate_personal_day,
    calculate_personal_month,
    calculate_personal_year,
)
from ..rules import RuleEngine, RuleResult
from .natal import _build_numerology
from .types import ProfileInput
from .utils import build_chart_request, pick_scope_date


def _summarise(result: RuleResult, scope: str) -> Dict:
    ordered = sorted(result.factors, key=lambda f: f.score, reverse=True)
    headline = ordered[0].meaning.text if ordered and ordered[0].meaning else ""
    return {
        "scope": scope,
        "headline": headline,
        "top_factors": [f.as_dict() for f in ordered[:5]],
        "topic_scores": result.topic_scores,
    }


def _numerology_cycles(profile: ProfileInput, target_date: str) -> Dict:
    year = int(target_date.split("-")[0])
    month = int(target_date.split("-")[1])
    day = int(target_date.split("-")[2])
    personal_year = calculate_personal_year(profile.date_of_birth, year)
    personal_month = calculate_personal_month(personal_year, month)
    personal_day = calculate_personal_day(personal_month, day)
    return {
        "personal_year": {"number": personal_year, "label": "Personal Year"},
        "personal_month": {"number": personal_month, "label": "Personal Month"},
        "personal_day": {"number": personal_day, "label": "Personal Day"},
    }


def build_forecast(
    profile: ProfileInput,
    scope: str = "daily",
    target_date: Optional[str] = None,
    chart_engine: Optional[ChartEngine] = None,
    rule_engine: Optional[RuleEngine] = None,
) -> Dict:
    """Build daily/weekly/monthly forecasts on the shared engine."""
    chart_engine = chart_engine or ChartEngine()
    rule_engine = rule_engine or RuleEngine()

    anchor_date = pick_scope_date(scope, target_date)
    natal_request = build_chart_request(profile, chart_type="natal")
    transit_request = build_chart_request(
        profile, chart_type="transit", target_date=anchor_date, time_override="12:00"
    )

    natal_chart = chart_engine.compute_chart(natal_request)
    transit_chart = chart_engine.compute_chart(transit_request)
    transit_aspects = chart_engine.build_synastry(transit_chart, natal_chart)

    numerology_core = _build_numerology(profile)
    numerology_cycles = _numerology_cycles(profile, anchor_date)
    numerology = {**numerology_core, **numerology_cycles}

    query_type = f"{scope}_forecast"
    result = rule_engine.evaluate(
        query_type, natal_chart, transit_aspects=transit_aspects, numerology=numerology
    )

    seed = hashlib.md5(
        f"{profile.name}{profile.date_of_birth}{anchor_date}{scope}".encode()
    ).hexdigest()

    structured = {
        "profile": {"name": profile.name, "dob": profile.date_of_birth},
        "scope": scope,
        "date": anchor_date,
        "summary": _summarise(result, scope),
        "sections": _build_sections(result, numerology, transit_aspects, seed),
        "natal_chart": {
            "planets": [p.__dict__ for p in natal_chart.planets],
            "houses": [h.__dict__ for h in natal_chart.houses],
        },
        "transit_chart": {
            "planets": [p.__dict__ for p in transit_chart.planets],
        },
        "transits": [a.__dict__ for a in transit_aspects],
        "numerology": numerology,
    }
    return structured


# ------------ Narrative helpers -------------


def _build_sections(
    result: RuleResult, numerology: Dict, transit_aspects: list, seed: str
) -> list:
    return [
        _build_topic_section("Overview", result, "general"),
        _build_topic_section(
            "Love & Relationships", result, "love", affirmation_key="love"
        ),
        _build_topic_section("Work & Money", result, "career", affirmation_key="work"),
        _build_topic_section(
            "Emotional / Spiritual", result, "emotional", affirmation_key="emotional"
        ),
        _standout_transit_section(transit_aspects),
        _numerology_overlay_section(numerology),
        _actions_section(seed),
    ]


def _normalize_rating(score: float) -> int:
    # Simple clamp and scale: assume topic scores cluster 0-5
    val = max(0.5, min(5.0, score))
    return int(round(val))


def _top_factors(result: RuleResult, topic: str, limit: int = 3):
    ranked = sorted(
        result.factors,
        key=lambda f: f.topic_scores.get(topic, 0) * f.score,
        reverse=True,
    )
    return ranked[:limit]


def _build_topic_section(
    title: str, result: RuleResult, topic: str, affirmation_key: str = "overview"
) -> Dict:
    factors = _top_factors(result, topic)
    explanations = [_format_factor(f) for f in factors if f]
    rating = _normalize_rating(result.topic_scores.get(topic, 0))
    return {
        "title": title,
        "rating": rating,
        "highlights": explanations,
        "affirmation": AFFIRMATIONS.get(affirmation_key, AFFIRMATIONS["overview"]),
    }


def _format_factor(factor) -> str:
    kind = factor.context.get("kind")
    if kind in ["transit", "synastry"]:
        template = ASPECT_TEMPLATES.get(
            factor.label.split()[1], "A key alignment stirs movement."
        )
        a, _, b = factor.label.partition(" ")
        house_note = ""
        if factor.meaning and "house" in factor.meaning.tags:
            house_note = f" in house {factor.context.get('house', '')}"
        return f"{template.format(a=a, b=b)}{house_note} (orb-weighted strength {factor.score:.2f})."
    if factor.context.get("kind") == "planet_house":
        house = factor.label.split()[-1]
        return f"{factor.meaning.text} ({HOUSE_BLURBS.get(int(house), '')})".strip()
    if factor.context.get("kind") == "planet_sign":
        tone = PLANET_TONES.get(factor.label.split()[0], "tone")
        return f"{factor.meaning.text}—shaping {tone} today."
    if factor.context.get("kind") == "numerology":
        return f"{factor.label}: {factor.meaning.text}"
    return factor.meaning.text if factor.meaning else factor.label


def _standout_transit_section(transit_aspects: list) -> Dict:
    if not transit_aspects:
        return {
            "title": "Standout Transit",
            "highlights": ["Quiet sky—no standout transit today."],
            "rating": 3,
        }
    strongest = sorted(transit_aspects, key=lambda a: a.strength_score, reverse=True)[0]
    template = ASPECT_TEMPLATES.get(
        strongest.aspect_type, "A key alignment shapes the day."
    )
    text = template.format(a=strongest.planet_a, b=strongest.planet_b)
    why = f"{text} (orb {strongest.orb:.2f}°, score {strongest.strength_score:.2f})."
    return {
        "title": "Standout Transit",
        "highlights": [why],
        "rating": _normalize_rating(strongest.strength_score * 5),
    }


def _numerology_overlay_section(numerology: Dict) -> Dict:
    highlights = []
    py = numerology.get("personal_year", {}).get("number")
    pm = numerology.get("personal_month", {}).get("number")
    pd = numerology.get("personal_day", {}).get("number")
    if py and py in NUMEROLOGY_OVERLAYS["personal_year"]:
        highlights.append(NUMEROLOGY_OVERLAYS["personal_year"][py])
    if pm and pm in NUMEROLOGY_OVERLAYS["personal_month"]:
        highlights.append(NUMEROLOGY_OVERLAYS["personal_month"][pm])
    if pd and pd in NUMEROLOGY_OVERLAYS["personal_day"]:
        highlights.append(NUMEROLOGY_OVERLAYS["personal_day"][pd])
    if not highlights:
        highlights.append("No cycle overlays today—steady as she goes.")
    return {"title": "Personal Year Overlay", "highlights": highlights, "rating": 4}


def _actions_section(seed: str) -> Dict:
    action = _deterministic_pick(seed + "action", ACTIONS)
    affirmation = AFFIRMATIONS.get("overview")
    return {
        "title": "Actions & Advice",
        "highlights": [action],
        "affirmation": affirmation,
        "rating": 4,
    }


def _deterministic_pick(seed: str, items: list) -> str:
    if not items:
        return ""
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(items)
    return items[idx]
