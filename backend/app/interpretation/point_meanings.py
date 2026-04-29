"""Meaning blocks for chart points and sensitive lots."""

from __future__ import annotations

from typing import Dict, Optional

from .planet_house_meanings import HOUSE_THEMES
from .planet_sign_meanings import SIGN_FLAVORS

POINT_ARCHETYPES = {
    "North Node": {
        "keyword": "Growth path",
        "focus": "future direction",
        "prompt": "Lean toward what stretches you, even when it feels less familiar.",
        "tags": ["destiny", "growth"],
        "weights": {"general": 0.45, "career": 0.3, "spiritual": 0.35},
    },
    "South Node": {
        "keyword": "Inherited mastery",
        "focus": "comfort zone",
        "prompt": "Use what comes naturally without getting trapped in repetition.",
        "tags": ["karma", "pattern"],
        "weights": {"general": 0.35, "emotional": 0.25, "spiritual": 0.35},
    },
    "Chiron": {
        "keyword": "Healing edge",
        "focus": "wound and wisdom",
        "prompt": "Turn the sensitive spot into a place of skill, compassion, and medicine.",
        "tags": ["healing", "teacher"],
        "weights": {"emotional": 0.45, "love": 0.2, "spiritual": 0.35},
    },
    "Part of Fortune": {
        "keyword": "Natural flow",
        "focus": "ease and opportunity",
        "prompt": "Notice where life opens more easily and build from that current.",
        "tags": ["luck", "prosperity"],
        "weights": {"general": 0.4, "career": 0.25, "love": 0.2},
    },
}


def _merge_weights(base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
    weights = base.copy()
    for key, value in extra.items():
        weights[key] = round(weights.get(key, 0.0) + value, 2)
    return weights


def get_point_text(
    point_name: str,
    sign: str,
    house: Optional[int] = None,
    chart_type: Optional[str] = None,
) -> str:
    point = POINT_ARCHETYPES.get(point_name)
    sign_data = SIGN_FLAVORS.get(sign)
    if not point or not sign_data:
        return f"{point_name} in {sign}."

    house_text = ""
    if house in HOUSE_THEMES:
        house_text = f" In relationships with {HOUSE_THEMES[house]['area']}, this theme becomes easier to see."

    chart_text = ""
    if point_name == "Part of Fortune" and chart_type in {"day", "night"}:
        chart_text = f" This is a {chart_type} chart, so the flow is especially tied to conscious timing."

    return (
        f"{point['keyword']}: {point['focus']} is {sign_data['style']}. "
        f"{point['prompt']}"
        f"{house_text}"
        f"{chart_text}"
    ).strip()


def get_point_meanings() -> Dict[str, Dict[str, Dict]]:
    meanings: Dict[str, Dict[str, Dict]] = {}
    for point_name, point_data in POINT_ARCHETYPES.items():
        meanings[point_name] = {}
        for sign, sign_data in SIGN_FLAVORS.items():
            meanings[point_name][sign] = {
                "text": get_point_text(point_name, sign),
                "tags": [point_data["focus"], *point_data["tags"], *sign_data["tags"]],
                "weights": _merge_weights(point_data["weights"], sign_data["weights"]),
            }
    return meanings


POINT_MEANINGS = get_point_meanings()
