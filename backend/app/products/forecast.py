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
from ..engine.guidance import get_daily_guidance


def build_forecast(profile: Dict, scope: str = "daily", lang: str = "en") -> Dict:
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
        lang=lang,
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
    
    # Generate daily guidance (Avoid/Embrace) with location for power hours
    guidance = get_daily_guidance(
        natal, 
        transit, 
        numerology, 
        scope,
        latitude=profile.get("latitude"),
        longitude=profile.get("longitude"),
        timezone=profile.get("timezone", "UTC"),
        lang=lang,
    )

    return {
        "scope": scope,
        "date": anchor.date().isoformat(),
        "sections": _sections(result, smoothed, numerology, scope),
        "theme": _top_theme(result),
        "numerology": numerology,
        "charts": {"natal": natal, "transit": transit},
        "ratings": _ratings(smoothed, numerology),
        "guidance": guidance,
    }


def _sections(result: Dict, smoothed_scores: Dict, numerology: Dict, scope: str = "daily") -> list:
    blocks = result["selected_blocks"]
    sections = []
    used_sources: set = set()  # Track sources to avoid repetition
    
    sections.append(
        _topic_section("Overview", None, blocks, smoothed_scores, numerology, used_sources, scope)
    )
    sections.append(
        _topic_section(
            "Love & Relationships", "love", blocks, smoothed_scores, numerology, used_sources, scope
        )
    )
    sections.append(
        _topic_section("Career & Money", "career", blocks, smoothed_scores, numerology, used_sources, scope)
    )
    sections.append(
        _topic_section(
            "Emotional & Spiritual", "emotional", blocks, smoothed_scores, numerology, used_sources, scope
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
    used_sources: Optional[set] = None,
    scope: str = "daily",
) -> Dict:
    """Build a section with highlights relevant to the topic, avoiding repetition."""
    if used_sources is None:
        used_sources = set()
    
    # Scope-specific source preferences
    # Daily: emphasize transits and fast-moving indicators
    # Weekly: emphasize Mars, Venus transits and medium-term themes
    # Monthly: emphasize Jupiter, Saturn and structural themes
    scope_source_boost = {
        "daily": ["Transit Moon", "Transit Mercury", "Transit Sun", "personal day"],
        "weekly": ["Transit Mars", "Transit Venus", "Transit Jupiter", "personal month"],
        "monthly": ["Transit Jupiter", "Transit Saturn", "Transit Pluto", "personal year", "Life Path"],
    }
    preferred_sources = scope_source_boost.get(scope, [])
    
    def source_boost(b):
        source = b.get("source", "")
        for pref in preferred_sources:
            if pref.lower() in source.lower():
                return 0.5
        return 0.0
    
    if topic_key:
        # Sort by how relevant blocks are to THIS specific topic
        def topic_relevance(b):
            weights = b.get("weights", {})
            tags = b.get("tags", [])
            # Primary: direct weight for this topic
            direct_weight = weights.get(topic_key, 0)
            # Secondary: tag match
            tag_match = 0.5 if topic_key in tags else 0
            # Penalty for blocks that are more relevant to OTHER topics
            other_weight = sum(v for k, v in weights.items() if k != topic_key)
            # Add scope-specific source boost
            boost = source_boost(b)
            # Include block weight from rule engine
            block_weight = b.get("weight", 1.0)
            return (direct_weight + tag_match - (other_weight * 0.3) + boost) * block_weight
        
        # Filter to blocks that have SOME relevance to this topic
        relevant = [
            b for b in blocks
            if topic_key in b.get("weights", {}) or topic_key in b.get("tags", [])
        ]
        # Sort by topic-specific relevance
        relevant = sorted(relevant, key=topic_relevance, reverse=True)
    else:
        # Overview: prefer blocks with high general weight, avoid topic-specific ones
        def overview_relevance(b):
            weights = b.get("weights", {})
            general = weights.get("general", 0)
            # Bonus for blocks that span multiple topics
            breadth = len([v for v in weights.values() if v > 0.2])
            # Add scope-specific source boost
            boost = source_boost(b)
            # Include block weight from rule engine
            block_weight = b.get("weight", 1.0)
            return (general + (breadth * 0.1) + boost) * block_weight
        
        relevant = sorted(blocks, key=overview_relevance, reverse=True)
    
    # Select highlights, avoiding already-used sources
    # Output clean text only (no source prefix for cleaner UX)
    highlights = []
    for b in relevant:
        source = b.get("source", "")
        # Skip if this exact source was already used in a previous section
        if source in used_sources:
            continue
        # Clean text only - no technical prefixes
        highlights.append(b['text'])
        used_sources.add(source)
        if len(highlights) >= 4:
            break
    
    # If we couldn't find enough unique blocks, allow some overlap
    if len(highlights) < 2:
        for b in relevant[:4]:
            text = b['text']
            if text not in highlights:
                highlights.append(text)
            if len(highlights) >= 4:
                break
    
    numerology_note = _numerology_hook(topic_key, numerology)
    if numerology_note:
        highlights.append(numerology_note)
    
    # Provide section-specific topic scores so the UI can render meaningful ratings.
    if topic_key:
        section_scores = {
            topic_key: scores.get(topic_key, 0.0),
            "general": scores.get("general", 0.0),
        }
    else:
        section_scores = scores

    return {
        "title": title,
        "highlights": highlights or ["Quiet sky; stay present."],
        "topic_scores": section_scores,
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
    meaning = cycle.get("meaning")
    if not meaning:
        return None
    # Return just the meaning - clean and concise
    return meaning
