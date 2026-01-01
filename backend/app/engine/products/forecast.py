from __future__ import annotations

import hashlib
from typing import Dict, Optional
from app.interpretation.translations import get_translation

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
    lang = profile.language
    result = rule_engine.evaluate(
        query_type, natal_chart, transit_aspects=transit_aspects, numerology=numerology, lang=lang
    )

    seed = hashlib.md5(
        f"{profile.name}{profile.date_of_birth}{anchor_date}{scope}".encode()
    ).hexdigest()

    structured = {
        "profile": {"name": profile.name, "dob": profile.date_of_birth},
        "scope": scope,
        "date": anchor_date,
        "summary": _summarise(result, scope),
        "sections": _build_sections(result, numerology, transit_aspects, seed, lang),
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
    result: RuleResult, numerology: Dict, transit_aspects: list, seed: str, lang: str = "en"
) -> list:
    return [
        _build_topic_section("Overview", result, "general", affirmation_key="overview", lang=lang),
        _build_topic_section(
            "Love & Relationships", result, "love", affirmation_key="love", lang=lang
        ),
        _build_topic_section("Work & Money", result, "career", affirmation_key="work", lang=lang),
        _build_topic_section(
            "Emotional / Spiritual", result, "emotional", affirmation_key="emotional", lang=lang
        ),
        _standout_transit_section(transit_aspects, lang=lang),
        _numerology_overlay_section(numerology, lang=lang),
        _actions_section(seed, lang=lang),
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
    title: str, result: RuleResult, topic: str, affirmation_key: str = "overview", lang: str = "en"
) -> Dict:
    factors = _top_factors(result, topic)
    explanations = [_format_factor(f, lang) for f in factors if f]
    rating = _normalize_rating(result.topic_scores.get(topic, 0))
    
    # Localize title
    title_key_map = {
        "Overview": "overview",
        "Love & Relationships": "love",
        "Work & Money": "career",
        "Emotional / Spiritual": "emotional"
    }
    title_key = f"section_title_{title_key_map.get(title, 'overview')}"
    localized_title = get_translation(lang, "forecast_sections", title_key)
    if not localized_title:
        localized_title = title
        
    # Localize affirmation
    affirmation_text = AFFIRMATIONS.get(affirmation_key, AFFIRMATIONS["overview"])
    localized_affirmation = get_translation(lang, "affirmations", f"affirmation_{affirmation_key}")
    if not localized_affirmation:
        localized_affirmation = affirmation_text

    return {
        "title": localized_title,
        "rating": rating,
        "highlights": explanations,
        "affirmation": localized_affirmation,
    }


def _format_factor(factor, lang: str = "en") -> str:
    """Format a factor into a concise, readable highlight."""
    kind = factor.context.get("kind")
    
    if kind in ["transit", "synastry"]:
        template_key = factor.label.split()[1]
        template = ASPECT_TEMPLATES.get(template_key, "{a}-{b} alignment.")
        if lang != "en":
            template = get_translation(lang, "aspect_templates", f"template_{template_key}") or template
            
        parts = factor.label.split()
        a, b = parts[0], parts[-1]
        return template.format(a=a, b=b)
    
    if kind == "planet_house":
        house = int(factor.label.split()[-1])
        house_name = HOUSE_BLURBS.get(house, f"house {house}")
        planet = factor.label.split()[0]
        tone = PLANET_TONES.get(planet, "energy")
        
        if lang != "en":
            house_name = get_translation(lang, "house_blurbs", f"house_{house}") or house_name
            tone = get_translation(lang, "planet_tones", f"tone_{planet}") or tone
            template = get_translation(lang, "forecast_templates", "planet_house_focus") or "{tone} focused on {house_name}."
            return template.format(tone=tone.title(), house_name=house_name.lower())
            
        return f"{tone.title()} focused on {house_name.lower()}."
    
    if kind == "planet_sign":
        return factor.meaning.text if factor.meaning else factor.label
    
    if kind == "numerology":
        # Extract just the number part for concise display
        label_parts = factor.label.split(":")
        return factor.meaning.text if factor.meaning else factor.label
    
    return factor.meaning.text if factor.meaning else factor.label


def _standout_transit_section(transit_aspects: list, lang: str = "en") -> Dict:
    title = "Standout Transit"
    if lang != "en":
        title = get_translation(lang, "forecast_sections", "section_title_standout") or title

    if not transit_aspects:
        msg = "Quiet sky—no standout transit today."
        if lang != "en":
            msg = get_translation(lang, "forecast_messages", "quiet_sky") or msg
        return {
            "title": title,
            "highlights": [msg],
            "rating": 3,
        }
    strongest = sorted(transit_aspects, key=lambda a: a.strength_score, reverse=True)[0]
    template = ASPECT_TEMPLATES.get(
        strongest.aspect_type, "A key alignment shapes the day."
    )
    if lang != "en":
        template = get_translation(lang, "aspect_templates", f"template_{strongest.aspect_type}") or template
        
    text = template.format(a=strongest.planet_a, b=strongest.planet_b)
    why = f"{text} (orb {strongest.orb:.2f}°, score {strongest.strength_score:.2f})."
    return {
        "title": title,
        "highlights": [why],
        "rating": _normalize_rating(strongest.strength_score * 5),
    }


def _numerology_overlay_section(numerology: Dict, lang: str = "en") -> Dict:
    highlights = []
    py = numerology.get("personal_year", {}).get("number")
    pm = numerology.get("personal_month", {}).get("number")
    pd = numerology.get("personal_day", {}).get("number")
    
    def get_overlay(category, num):
        if lang == "en":
            return NUMEROLOGY_OVERLAYS.get(category, {}).get(num)
        key = f"{category}_{num}"
        return get_translation(lang, "numerology_overlays", key) or NUMEROLOGY_OVERLAYS.get(category, {}).get(num)

    if py:
        text = get_overlay("personal_year", py)
        if text: highlights.append(text)
    if pm:
        text = get_overlay("personal_month", pm)
        if text: highlights.append(text)
    if pd:
        text = get_overlay("personal_day", pd)
        if text: highlights.append(text)
        
    if not highlights:
        msg = "No cycle overlays today—steady as she goes."
        if lang != "en":
            msg = get_translation(lang, "forecast_messages", "no_overlays") or msg
        highlights.append(msg)
        
    title = "Personal Year Overlay"
    if lang != "en":
        title = get_translation(lang, "forecast_sections", "section_title_numerology") or title
        
    return {"title": title, "highlights": highlights, "rating": 4}


def _actions_section(seed: str, lang: str = "en") -> Dict:
    # Localize ACTIONS pool
    actions_pool = ACTIONS
    if lang != "en":
        # Assuming ACTIONS is a list, we need to fetch localized list or iterate
        # Similar to fusion.py get_localized_pool
        localized_pool = []
        for i, item in enumerate(ACTIONS):
            key = f"action_{i}"
            translated = get_translation(lang, "forecast_actions", key)
            localized_pool.append(translated if translated else item)
        actions_pool = localized_pool

    action = _deterministic_pick(seed + "action", actions_pool)
    
    affirmation = AFFIRMATIONS.get("overview")
    if lang != "en":
        affirmation = get_translation(lang, "affirmations", "affirmation_overview") or affirmation
        
    title = "Actions & Advice"
    if lang != "en":
        title = get_translation(lang, "forecast_sections", "section_title_actions") or title
        
    return {
        "title": title,
        "highlights": [action],
        "affirmation": affirmation,
        "rating": 4,
    }


def _deterministic_pick(seed: str, items: list) -> str:
    if not items:
        return ""
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(items)
    return items[idx]
