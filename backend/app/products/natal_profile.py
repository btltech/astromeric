"""
natal_profile.py
Builds a structured natal profile using chart + numerology + rule engine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

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
        _section("Overview", general, chart, numerology, birth_time_assumed),
        _section("Love & Relationships", love, chart, numerology, birth_time_assumed),
        _section("Career & Money", career, chart, numerology, birth_time_assumed),
    ]

    return {
        "metadata": chart["metadata"],
        "sections": sections,
        "numerology": numerology,
        "chart": chart,
    }


TOPIC_MAP = {
    "Overview": "general",
    "Love & Relationships": "love",
    "Career & Money": "career",
}


def _section(
    title: str,
    result: Dict,
    chart: Dict,
    numerology: Dict,
    birth_time_assumed: bool = False,
) -> Dict:
    ordered_blocks = _ordered_blocks(result)
    highlights = [f"{block['source']}: {block['text']}" for block in ordered_blocks[:3]]

    # When birth time is unknown, filter out house-specific interpretations
    # so we don't mislead users with inaccurate house placements.
    if birth_time_assumed:
        highlights = [
            h
            for h in highlights
            if not any(
                kw in h.lower()
                for kw in ["house", "ascendant", "rising", "midheaven", "angular"]
            )
        ] or highlights[
            :1
        ]  # always keep at least one highlight

    visible_blocks = [
        block
        for block in ordered_blocks
        if not birth_time_assumed or not _is_house_specific(block)
    ]
    if not visible_blocks:
        visible_blocks = ordered_blocks[:1]

    topic_key = TOPIC_MAP.get(title, "general")

    section = {
        "title": title,
        "topic_scores": result["topic_scores"],
        "highlights": highlights,
        "top_themes": ordered_blocks[:5],
        "summary": _compose_summary(title, visible_blocks, chart, numerology),
        "affirmation": _build_affirmation(title, visible_blocks),
        "rating": _section_rating(result["topic_scores"], topic_key),
    }
    if birth_time_assumed:
        section["data_quality_note"] = (
            "This reading is based on your Sun and Moon signs. "
            "Add your exact birth time for house-specific insights."
        )
    return section


def _ordered_blocks(result: Dict) -> List[Dict]:
    ranked = result.get("top_themes") or []
    if ranked:
        return ranked
    return sorted(
        result.get("selected_blocks") or [],
        key=lambda block: block.get("weight", 0),
        reverse=True,
    )


def _is_house_specific(block: Dict) -> bool:
    text = f"{block.get('source', '')} {block.get('text', '')}".lower()
    return any(
        keyword in text
        for keyword in ["house", "ascendant", "rising", "midheaven", "angular"]
    )


def _terminal_punctuation(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    if cleaned[-1] in ".!?":
        return cleaned
    return f"{cleaned}."


def _compose_summary(
    title: str, blocks: List[Dict], chart: Dict, numerology: Dict
) -> str:
    primary = next((block for block in blocks if block.get("text")), None)
    if primary is None:
        return "Your chart points to a meaningful period of growth, reflection, and better timing."

    sentences = [_terminal_punctuation(primary["text"])]

    secondary = next(
        (
            block
            for block in blocks[1:]
            if block.get("text") and block.get("source") != primary.get("source")
        ),
        None,
    )
    if secondary is not None:
        sentences.append(_terminal_punctuation(secondary["text"]))
    else:
        dignity_sentence = _dignity_sentence(primary, chart)
        if dignity_sentence:
            sentences.append(dignity_sentence)

    if len(sentences) == 1:
        numerology_sentence = _numerology_sentence(title, numerology)
        if numerology_sentence:
            sentences.append(numerology_sentence)

    return " ".join(sentence for sentence in sentences if sentence).strip()


def _dignity_sentence(block: Dict, chart: Dict) -> Optional[str]:
    source = block.get("source") or ""
    planet_name = source.split(" in ", 1)[0]
    if not planet_name:
        return None

    planet = next(
        (item for item in chart.get("planets", []) if item.get("name") == planet_name),
        None,
    )
    dignity = planet.get("dignity") if planet else None
    if dignity in {"domicile", "exaltation"}:
        return f"{planet_name} is in {dignity}, so this theme has extra support and comes through more clearly."
    if dignity in {"detriment", "fall"}:
        return f"{planet_name} is in {dignity}, so this area rewards steadier, more conscious handling."
    return None


def _numerology_sentence(title: str, numerology: Dict) -> Optional[str]:
    if title == "Love & Relationships":
        source = numerology.get("soul_urge", {})
    elif title == "Career & Money":
        source = numerology.get("expression", {})
    else:
        source = numerology.get("life_path", {})

    meaning = source.get("meaning")
    if not meaning:
        return None
    return _terminal_punctuation(meaning)


def _section_rating(topic_scores: Dict[str, float], topic_key: str) -> int:
    score = float(topic_scores.get(topic_key, 0.0))
    return max(1, min(5, round(score / 3)))


def _build_affirmation(title: str, blocks: List[Dict]) -> str:
    sources = " ".join(block.get("source", "") for block in blocks[:2])
    lowered = sources.lower()

    if "north node" in lowered:
        return "I trust the path that stretches me into my next chapter."
    if "part of fortune" in lowered:
        return "I follow the current that brings ease, meaning, and right opportunity."
    if "chiron" in lowered:
        return "I can turn sensitivity into wisdom, skill, and compassion."
    if title == "Love & Relationships":
        return "I bring warmth, clarity, and self-respect into the way I connect."
    if title == "Career & Money":
        return (
            "I build lasting progress by using my strengths with discipline and timing."
        )
    return "I trust my nature, use my gifts well, and move forward with intention."
