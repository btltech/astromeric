"""
planet_sign_meanings.py
Programmatically generate planet-in-sign meaning blocks for full coverage.
Each block contains text, tags, and weighted topics.
"""

from __future__ import annotations

from typing import Dict

PLANET_ARCHETYPES = {
    "Sun": {"focus": "identity", "weights": {"general": 0.6, "career": 0.4}},
    "Moon": {"focus": "emotional needs", "weights": {"emotional": 0.7, "love": 0.3}},
    "Mercury": {
        "focus": "mind and communication",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {"focus": "relating style", "weights": {"love": 0.7, "emotional": 0.3}},
    "Mars": {"focus": "drive and courage", "weights": {"career": 0.5, "general": 0.4}},
    "Jupiter": {
        "focus": "growth philosophy",
        "weights": {"spiritual": 0.4, "general": 0.3},
    },
    "Saturn": {"focus": "structure and mastery", "weights": {"career": 0.5}},
    "Uranus": {
        "focus": "innovation impulse",
        "weights": {"general": 0.3, "career": 0.2},
    },
    "Neptune": {
        "focus": "imagination and faith",
        "weights": {"spiritual": 0.5, "emotional": 0.3},
    },
    "Pluto": {
        "focus": "transformational power",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

SIGN_FLAVORS = {
    "Aries": {
        "keywords": "bold, pioneering fire",
        "tags": ["courage"],
        "weights": {"general": 0.2, "career": 0.2},
    },
    "Taurus": {
        "keywords": "steady, sensual earth",
        "tags": ["stability"],
        "weights": {"love": 0.2, "career": 0.1},
    },
    "Gemini": {
        "keywords": "curious, versatile air",
        "tags": ["communication"],
        "weights": {"general": 0.2},
    },
    "Cancer": {
        "keywords": "protective, intuitive water",
        "tags": ["home"],
        "weights": {"emotional": 0.2, "love": 0.1},
    },
    "Leo": {
        "keywords": "radiant, expressive fire",
        "tags": ["expression"],
        "weights": {"general": 0.2, "career": 0.1},
    },
    "Virgo": {
        "keywords": "discerning, service-minded earth",
        "tags": ["service"],
        "weights": {"career": 0.2},
    },
    "Libra": {
        "keywords": "harmonizing, relational air",
        "tags": ["relationship"],
        "weights": {"love": 0.2},
    },
    "Scorpio": {
        "keywords": "intense, regenerative water",
        "tags": ["depth"],
        "weights": {"emotional": 0.2},
    },
    "Sagittarius": {
        "keywords": "expansive, truth-seeking fire",
        "tags": ["philosophy"],
        "weights": {"spiritual": 0.2},
    },
    "Capricorn": {
        "keywords": "ambitious, disciplined earth",
        "tags": ["structure"],
        "weights": {"career": 0.2},
    },
    "Aquarius": {
        "keywords": "visionary, future-minded air",
        "tags": ["innovation"],
        "weights": {"general": 0.2},
    },
    "Pisces": {
        "keywords": "dreamy, empathic water",
        "tags": ["compassion"],
        "weights": {"spiritual": 0.2, "emotional": 0.1},
    },
}


def _combine_weights(
    base: Dict[str, float], extra: Dict[str, float]
) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


PLANET_SIGN_MEANINGS: Dict[str, Dict[str, Dict]] = {}
for planet, pdata in PLANET_ARCHETYPES.items():
    PLANET_SIGN_MEANINGS[planet] = {}
    for sign, sdata in SIGN_FLAVORS.items():
        text = f"{planet} {pdata['focus']} flows through {sign}'s {sdata['keywords']}, shaping instinctive choices."
        tags = [pdata["focus"], *sdata["tags"]]
        weights = _combine_weights(pdata["weights"], sdata["weights"])
        PLANET_SIGN_MEANINGS[planet][sign] = {
            "text": text,
            "tags": tags,
            "weights": weights,
        }
