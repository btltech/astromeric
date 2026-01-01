"""
planet_sign_meanings.py
Concise planet-in-sign meaning blocks.
"""

from __future__ import annotations

from typing import Dict, List
from .translations import get_translation

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

def get_planet_sign_text(planet: str, sign: str, lang: str = 'en') -> str:
    """Return a concise, action-oriented sentence for planet in sign."""
    # Try to get translation
    if lang != 'en':
        p_keywords = get_translation(lang, 'planet_keywords')
        s_flavors = get_translation(lang, 'sign_flavors')
        
        if p_keywords and s_flavors:
            p_keyword = p_keywords.get(planet)
            s_data = s_flavors.get(sign)
            
            if p_keyword and s_data:
                # Simple sentence construction: "Keyword: style. Action."
                # Using title() for keyword might not be correct for all languages, but acceptable
                return f"{p_keyword.title()}: {s_data['style']}. {s_data['action']}."

    # Fallback to English
    pdata = PLANET_ARCHETYPES.get(planet)
    sdata = SIGN_FLAVORS.get(sign)
    if not pdata or not sdata:
        return f"{planet} in {sign}."
    return f"{pdata['keyword'].title()} is {sdata['style']}. {sdata['action']}."


def get_planet_sign_meanings(lang: str = 'en') -> Dict[str, Dict[str, Dict]]:
    """Build planet sign meanings for a specific language."""
    meanings = {}
    for planet, pdata in PLANET_ARCHETYPES.items():
        meanings[planet] = {}
        for sign, sdata in SIGN_FLAVORS.items():
            text = get_planet_sign_text(planet, sign, lang)
            tags = [pdata["focus"], *sdata["tags"]]
            weights = _combine_weights(pdata["weights"], sdata["weights"])
            meanings[planet][sign] = {
                "text": text,
                "tags": tags,
                "weights": weights,
            }
    return meanings


# Pre-build meanings dict (English default)
PLANET_SIGN_MEANINGS = get_planet_sign_meanings('en')
