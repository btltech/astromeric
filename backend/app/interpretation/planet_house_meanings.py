"""
planet_house_meanings.py
Auto-generate planet-in-house meanings for 10 planets × 12 houses.
"""
from __future__ import annotations

from typing import Dict

PLANET_THEMES = {
    "Sun": {
        "verb": "spotlights",
        "focus": "identity work",
        "weights": {"general": 0.5, "career": 0.4},
    },
    "Moon": {
        "verb": "seeks comfort in",
        "focus": "emotional security",
        "weights": {"emotional": 0.6, "love": 0.3},
    },
    "Mercury": {
        "verb": "analyzes",
        "focus": "thought process",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "verb": "attracts harmony through",
        "focus": "relationships",
        "weights": {"love": 0.7},
    },
    "Mars": {
        "verb": "pushes for action in",
        "focus": "drive",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "verb": "expands through",
        "focus": "growth",
        "weights": {"spiritual": 0.3, "general": 0.3},
    },
    "Saturn": {
        "verb": "demands mastery in",
        "focus": "discipline",
        "weights": {"career": 0.4},
    },
    "Uranus": {
        "verb": "innovates around",
        "focus": "change",
        "weights": {"general": 0.3},
    },
    "Neptune": {
        "verb": "dissolves boundaries in",
        "focus": "intuition",
        "weights": {"spiritual": 0.4},
    },
    "Pluto": {
        "verb": "transforms",
        "focus": "power themes",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

HOUSE_THEMES = {
    1: {
        "area": "identity and first impressions",
        "tags": ["self"],
        "weights": {"general": 0.3},
    },
    2: {
        "area": "resources, skills, and values",
        "tags": ["money"],
        "weights": {"career": 0.3},
    },
    3: {
        "area": "learning, messaging, and siblings",
        "tags": ["communication"],
        "weights": {"general": 0.2},
    },
    4: {
        "area": "home, family, and roots",
        "tags": ["home"],
        "weights": {"emotional": 0.3},
    },
    5: {
        "area": "creativity, romance, and play",
        "tags": ["love"],
        "weights": {"love": 0.3},
    },
    6: {
        "area": "work rituals and wellness",
        "tags": ["health"],
        "weights": {"career": 0.2, "health": 0.4},
    },
    7: {
        "area": "partnerships and contracts",
        "tags": ["relationship"],
        "weights": {"love": 0.4},
    },
    8: {
        "area": "shared resources and depth",
        "tags": ["intimacy"],
        "weights": {"emotional": 0.3},
    },
    9: {
        "area": "philosophy, study, and travel",
        "tags": ["vision"],
        "weights": {"spiritual": 0.3},
    },
    10: {
        "area": "career, status, and legacy",
        "tags": ["career"],
        "weights": {"career": 0.5},
    },
    11: {
        "area": "friends, networks, and causes",
        "tags": ["community"],
        "weights": {"general": 0.2},
    },
    12: {
        "area": "rest, subconscious, and retreat",
        "tags": ["inner"],
        "weights": {"spiritual": 0.3, "emotional": 0.2},
    },
}


def _merge_weights(base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


PLANET_HOUSE_MEANINGS: Dict[str, Dict[int, Dict]] = {}
for planet, pdata in PLANET_THEMES.items():
    PLANET_HOUSE_MEANINGS[planet] = {}
    for house, hdata in HOUSE_THEMES.items():
        text = f"{planet} {pdata['verb']} {hdata['area']}, linking {pdata['focus']} to this zone."
        tags = [pdata["focus"], *hdata["tags"]]
        weights = _merge_weights(pdata["weights"], hdata["weights"])
        PLANET_HOUSE_MEANINGS[planet][house] = {
            "text": text,
            "tags": tags,
            "weights": weights,
        }
