"""
planet_sign_meanings.py
Programmatically generate planet-in-sign meaning blocks for full coverage.
Each block contains text, tags, and weighted topics.
"""

from __future__ import annotations

import random
from typing import Dict, List

PLANET_ARCHETYPES = {
    "Sun": {
        "focus": "identity",
        "verbs": ["express yourself", "radiate confidence", "channel your identity"],
        "noun": "core self",
        "weights": {"general": 0.6, "career": 0.4},
    },
    "Moon": {
        "focus": "emotional needs",
        "verbs": ["feel things deeply", "nurture others", "respond emotionally"],
        "noun": "emotional nature",
        "weights": {"emotional": 0.7, "love": 0.3},
    },
    "Mercury": {
        "focus": "mind and communication",
        "verbs": ["think and learn", "communicate ideas", "process information"],
        "noun": "mental style",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "focus": "relating style",
        "verbs": ["connect with others", "show affection", "attract what you value"],
        "noun": "relationship approach",
        "weights": {"love": 0.7, "emotional": 0.3},
    },
    "Mars": {
        "focus": "drive and courage",
        "verbs": ["pursue goals", "assert yourself", "take action"],
        "noun": "action style",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "focus": "growth philosophy",
        "verbs": ["expand your horizons", "seek meaning", "explore possibilities"],
        "noun": "growth path",
        "weights": {"spiritual": 0.4, "general": 0.3},
    },
    "Saturn": {
        "focus": "structure and mastery",
        "verbs": ["build lasting foundations", "master challenges", "take responsibility"],
        "noun": "approach to responsibility",
        "weights": {"career": 0.5},
    },
    "Uranus": {
        "focus": "innovation impulse",
        "verbs": ["break new ground", "embrace change", "think independently"],
        "noun": "change instinct",
        "weights": {"general": 0.3, "career": 0.2},
    },
    "Neptune": {
        "focus": "imagination and faith",
        "verbs": ["dream big", "tap into intuition", "connect spiritually"],
        "noun": "spiritual vision",
        "weights": {"spiritual": 0.5, "emotional": 0.3},
    },
    "Pluto": {
        "focus": "transformational power",
        "verbs": ["transform deeply", "let go and regenerate", "reclaim your power"],
        "noun": "capacity for reinvention",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

SIGN_FLAVORS = {
    "Aries": {
        "keywords": "bold, pioneering fire",
        "style": "bold and pioneering",
        "advice": "channel that fire into decisive action",
        "tags": ["courage"],
        "weights": {"general": 0.2, "career": 0.2},
    },
    "Taurus": {
        "keywords": "steady, sensual earth",
        "style": "patient and grounded",
        "advice": "build steadily and savor the journey",
        "tags": ["stability"],
        "weights": {"love": 0.2, "career": 0.1},
    },
    "Gemini": {
        "keywords": "curious, versatile air",
        "style": "curious and adaptable",
        "advice": "stay open to new ideas and conversations",
        "tags": ["communication"],
        "weights": {"general": 0.2},
    },
    "Cancer": {
        "keywords": "protective, intuitive water",
        "style": "nurturing and intuitive",
        "advice": "trust your gut and protect what matters",
        "tags": ["home"],
        "weights": {"emotional": 0.2, "love": 0.1},
    },
    "Leo": {
        "keywords": "radiant, expressive fire",
        "style": "confident and expressive",
        "advice": "let your authentic self shine",
        "tags": ["expression"],
        "weights": {"general": 0.2, "career": 0.1},
    },
    "Virgo": {
        "keywords": "discerning, service-minded earth",
        "style": "practical and detail-oriented",
        "advice": "refine your approach and be of service",
        "tags": ["service"],
        "weights": {"career": 0.2},
    },
    "Libra": {
        "keywords": "harmonizing, relational air",
        "style": "diplomatic and partnership-focused",
        "advice": "seek balance and meaningful connection",
        "tags": ["relationship"],
        "weights": {"love": 0.2},
    },
    "Scorpio": {
        "keywords": "intense, regenerative water",
        "style": "deep and transformative",
        "advice": "embrace intensity and let go of what no longer serves you",
        "tags": ["depth"],
        "weights": {"emotional": 0.2},
    },
    "Sagittarius": {
        "keywords": "expansive, truth-seeking fire",
        "style": "adventurous and philosophical",
        "advice": "expand your horizons and follow your truth",
        "tags": ["philosophy"],
        "weights": {"spiritual": 0.2},
    },
    "Capricorn": {
        "keywords": "ambitious, disciplined earth",
        "style": "ambitious and disciplined",
        "advice": "set long-term goals and work toward mastery",
        "tags": ["structure"],
        "weights": {"career": 0.2},
    },
    "Aquarius": {
        "keywords": "visionary, future-minded air",
        "style": "innovative and humanitarian",
        "advice": "think ahead and embrace your uniqueness",
        "tags": ["innovation"],
        "weights": {"general": 0.2},
    },
    "Pisces": {
        "keywords": "dreamy, empathic water",
        "style": "imaginative and compassionate",
        "advice": "trust your intuition and stay connected to your dreams",
        "tags": ["compassion"],
        "weights": {"spiritual": 0.2, "emotional": 0.1},
    },
}

# Sentence templates for variety - all grammatically correct with "you" subject
_TEMPLATES: List[str] = [
    "Your {noun} is {style}—{advice}.",
    "With {planet} in {sign}, you tend to {verb} in {article} {style} way. {advice_cap}.",
    "{planet} in {sign} gives you {article} {style} {noun}. {advice_cap}.",
    "You naturally {verb} with {style} energy—{advice}.",
]


def _combine_weights(
    base: Dict[str, float], extra: Dict[str, float]
) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


def _article(word: str) -> str:
    """Return 'an' if word starts with vowel sound, else 'a'."""
    return "an" if word[0].lower() in "aeiou" else "a"


def _build_text(planet: str, pdata: Dict, sign: str, sdata: Dict) -> str:
    """Generate a readable, varied sentence for a planet-sign combo."""
    template = random.choice(_TEMPLATES)
    verb = random.choice(pdata["verbs"])
    advice_cap = sdata["advice"][0].upper() + sdata["advice"][1:]
    article = _article(sdata["style"])
    return template.format(
        planet=planet,
        sign=sign,
        noun=pdata["noun"],
        style=sdata["style"],
        article=article,
        advice=sdata["advice"],
        advice_cap=advice_cap,
        verb=verb,
    )


# Pre-build meanings dict (text generated once at import; could regenerate per request for variety)
PLANET_SIGN_MEANINGS: Dict[str, Dict[str, Dict]] = {}
for planet, pdata in PLANET_ARCHETYPES.items():
    PLANET_SIGN_MEANINGS[planet] = {}
    for sign, sdata in SIGN_FLAVORS.items():
        text = _build_text(planet, pdata, sign, sdata)
        tags = [pdata["focus"], *sdata["tags"]]
        weights = _combine_weights(pdata["weights"], sdata["weights"])
        PLANET_SIGN_MEANINGS[planet][sign] = {
            "text": text,
            "tags": tags,
            "weights": weights,
        }


def get_planet_sign_text(planet: str, sign: str) -> str:
    """Return a fresh, human-friendly sentence for planet in sign."""
    pdata = PLANET_ARCHETYPES.get(planet)
    sdata = SIGN_FLAVORS.get(sign)
    if not pdata or not sdata:
        return f"{planet} in {sign}."
    return _build_text(planet, pdata, sign, sdata)
