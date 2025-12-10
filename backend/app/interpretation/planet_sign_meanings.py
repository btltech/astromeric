"""
planet_sign_meanings.py
Concise planet-in-sign meaning blocks.
"""

from __future__ import annotations

from typing import Dict, List

PLANET_ARCHETYPES = {
    "Sun": {
        "focus": "identity",
        "keyword": "core self",
        "weights": {"general": 0.6, "career": 0.4},
    },
    "Moon": {
        "focus": "emotions",
        "keyword": "emotional nature",
        "weights": {"emotional": 0.7, "love": 0.3},
    },
    "Mercury": {
        "focus": "mind",
        "keyword": "thinking style",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "focus": "love",
        "keyword": "love language",
        "weights": {"love": 0.7, "emotional": 0.3},
    },
    "Mars": {
        "focus": "action",
        "keyword": "drive",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "focus": "growth",
        "keyword": "expansion",
        "weights": {"spiritual": 0.4, "general": 0.3},
    },
    "Saturn": {
        "focus": "discipline",
        "keyword": "mastery",
        "weights": {"career": 0.5},
    },
    "Uranus": {
        "focus": "innovation",
        "keyword": "uniqueness",
        "weights": {"general": 0.3, "career": 0.2},
    },
    "Neptune": {
        "focus": "dreams",
        "keyword": "imagination",
        "weights": {"spiritual": 0.5, "emotional": 0.3},
    },
    "Pluto": {
        "focus": "transformation",
        "keyword": "power",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

SIGN_FLAVORS = {
    "Aries": {
        "style": "bold and direct",
        "action": "Take initiative",
        "tags": ["courage", "initiation"],
        "weights": {"general": 0.2, "career": 0.2},
    },
    "Taurus": {
        "style": "steady and sensual",
        "action": "Build with patience",
        "tags": ["stability", "pleasure"],
        "weights": {"love": 0.2, "career": 0.1},
    },
    "Gemini": {
        "style": "curious and adaptable",
        "action": "Communicate and connect",
        "tags": ["communication", "versatility"],
        "weights": {"general": 0.2},
    },
    "Cancer": {
        "style": "nurturing and intuitive",
        "action": "Trust your feelings",
        "tags": ["home", "intuition"],
        "weights": {"emotional": 0.2, "love": 0.1},
    },
    "Leo": {
        "style": "confident and creative",
        "action": "Express yourself fully",
        "tags": ["expression", "leadership"],
        "weights": {"general": 0.2, "career": 0.1},
    },
    "Virgo": {
        "style": "precise and helpful",
        "action": "Perfect the details",
        "tags": ["service", "refinement"],
        "weights": {"career": 0.2},
    },
    "Libra": {
        "style": "harmonious and fair",
        "action": "Seek balance",
        "tags": ["relationship", "harmony"],
        "weights": {"love": 0.2},
    },
    "Scorpio": {
        "style": "intense and transformative",
        "action": "Embrace depth",
        "tags": ["depth", "transformation"],
        "weights": {"emotional": 0.2},
    },
    "Sagittarius": {
        "style": "adventurous and philosophical",
        "action": "Expand your horizons",
        "tags": ["philosophy", "adventure"],
        "weights": {"spiritual": 0.2},
    },
    "Capricorn": {
        "style": "ambitious and disciplined",
        "action": "Build your legacy",
        "tags": ["structure", "ambition"],
        "weights": {"career": 0.2},
    },
    "Aquarius": {
        "style": "innovative and independent",
        "action": "Think differently",
        "tags": ["innovation", "community"],
        "weights": {"general": 0.2},
    },
    "Pisces": {
        "style": "intuitive and compassionate",
        "action": "Trust your intuition",
        "tags": ["compassion", "transcendence"],
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


def get_planet_sign_text(planet: str, sign: str) -> str:
    """Return a concise, action-oriented sentence for planet in sign."""
    pdata = PLANET_ARCHETYPES.get(planet)
    sdata = SIGN_FLAVORS.get(sign)
    if not pdata or not sdata:
        return f"{planet} in {sign}."
    return f"{pdata['keyword'].title()} is {sdata['style']}. {sdata['action']}."


# Pre-build meanings dict
PLANET_SIGN_MEANINGS: Dict[str, Dict[str, Dict]] = {}
for planet, pdata in PLANET_ARCHETYPES.items():
    PLANET_SIGN_MEANINGS[planet] = {}
    for sign, sdata in SIGN_FLAVORS.items():
        text = get_planet_sign_text(planet, sign)
        tags = [pdata["focus"], *sdata["tags"]]
        weights = _combine_weights(pdata["weights"], sdata["weights"])
        PLANET_SIGN_MEANINGS[planet][sign] = {
            "text": text,
            "tags": tags,
            "weights": weights,
        }
