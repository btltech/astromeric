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
        "focus": "radiant identity",
        "verbs": [
            "illuminate the room with your presence",
            "blaze a trail that others instinctively follow",
            "pour your essence into everything you create",
            "command attention without saying a word",
        ],
        "noun": "inner fire",
        "essence": "the golden thread of your authentic self",
        "weights": {"general": 0.6, "career": 0.4},
    },
    "Moon": {
        "focus": "soul tides",
        "verbs": [
            "sense the unspoken currents beneath the surface",
            "wrap others in your instinctive understanding",
            "ebb and flow with the rhythms of your inner world",
            "hold space for feelings that defy easy words",
        ],
        "noun": "emotional depths",
        "essence": "the silver mirror reflecting your deepest needs",
        "weights": {"emotional": 0.7, "love": 0.3},
    },
    "Mercury": {
        "focus": "quicksilver mind",
        "verbs": [
            "weave ideas into patterns others miss",
            "translate the unsayable into words that land",
            "connect dots across vast mental landscapes",
            "dance through concepts with effortless agility",
        ],
        "noun": "mental signature",
        "essence": "the winged messenger carrying your thoughts to the world",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "focus": "heart magnetism",
        "verbs": [
            "draw kindred spirits into your orbit",
            "weave beauty into the ordinary",
            "speak the secret language of attraction",
            "taste the sweetness hidden in connection",
        ],
        "noun": "love frequency",
        "essence": "the rose that blooms toward what you truly value",
        "weights": {"love": 0.7, "emotional": 0.3},
    },
    "Mars": {
        "focus": "warrior flame",
        "verbs": [
            "charge toward what sets your blood alive",
            "carve your will into reality",
            "rise to challenges that would break lesser spirits",
            "ignite momentum where others only see obstacles",
        ],
        "noun": "battle rhythm",
        "essence": "the blade you forge in the fires of desire",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "focus": "expansive vision",
        "verbs": [
            "stretch beyond horizons you once thought fixed",
            "find gold in paths others overlook",
            "trust the cosmic generosity flowing your way",
            "gather wisdom from every corner of experience",
        ],
        "noun": "abundance signature",
        "essence": "the arrow of faith you shoot toward possibility",
        "weights": {"spiritual": 0.4, "general": 0.3},
    },
    "Saturn": {
        "focus": "earned mastery",
        "verbs": [
            "sculpt enduring structures from raw discipline",
            "transform limitations into launchpads",
            "carry weight that ultimately makes you unshakable",
            "build legacies brick by patient brick",
        ],
        "noun": "mastery blueprint",
        "essence": "the mountain you're destined to climb and claim",
        "weights": {"career": 0.5},
    },
    "Uranus": {
        "focus": "lightning insight",
        "verbs": [
            "shatter comfortable cages with a single spark",
            "tune into frequencies the world hasn't heard yet",
            "rewire convention into something revolutionary",
            "electrify stagnant waters with sudden brilliance",
        ],
        "noun": "rebel code",
        "essence": "the lightning bolt that refuses to follow the same path twice",
        "weights": {"general": 0.3, "career": 0.2},
    },
    "Neptune": {
        "focus": "mystic waters",
        "verbs": [
            "dissolve boundaries between dreams and waking",
            "hear the music behind the silence",
            "surrender to currents larger than yourself",
            "channel visions that shimmer just beyond logic",
        ],
        "noun": "dream weave",
        "essence": "the ocean of imagination where all things connect",
        "weights": {"spiritual": 0.5, "emotional": 0.3},
    },
    "Pluto": {
        "focus": "phoenix power",
        "verbs": [
            "descend into shadows and return transformed",
            "burn away what no longer serves your evolution",
            "reclaim buried power others feared to touch",
            "transmute pain into unbreakable strength",
        ],
        "noun": "resurrection force",
        "essence": "the volcanic core where endings birth beginnings",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

SIGN_FLAVORS = {
    "Aries": {
        "keywords": "blazing pioneer",
        "style": "fearless and untamed",
        "advice": "strike while the iron of your courage is white-hot",
        "spark": "the first spark of creation before thought catches up",
        "tags": ["courage", "initiation"],
        "weights": {"general": 0.2, "career": 0.2},
    },
    "Taurus": {
        "keywords": "rooted sensualist",
        "style": "deliberately luxurious",
        "advice": "let patience be the soil where your deepest desires take root",
        "spark": "the ancient wisdom of bodies that remember how to bloom",
        "tags": ["stability", "pleasure"],
        "weights": {"love": 0.2, "career": 0.1},
    },
    "Gemini": {
        "keywords": "quicksilver shapeshifter",
        "style": "endlessly curious",
        "advice": "let your mind butterfly between worlds—that's where magic hides",
        "spark": "the electric thrill of two ideas colliding into something new",
        "tags": ["communication", "versatility"],
        "weights": {"general": 0.2},
    },
    "Cancer": {
        "keywords": "guardian of hidden depths",
        "style": "fiercely tender",
        "advice": "trust the wisdom swimming in your emotional undertow",
        "spark": "the shell that protects a pearl only moonlight can find",
        "tags": ["home", "intuition"],
        "weights": {"emotional": 0.2, "love": 0.1},
    },
    "Leo": {
        "keywords": "blazing sovereign",
        "style": "magnificently unapologetic",
        "advice": "let your heart roar—the world needs your particular brilliance",
        "spark": "the stage that appears wherever you dare to be fully yourself",
        "tags": ["expression", "leadership"],
        "weights": {"general": 0.2, "career": 0.1},
    },
    "Virgo": {
        "keywords": "sacred craftsperson",
        "style": "precisely devoted",
        "advice": "find the divine hiding in the details you're born to perfect",
        "spark": "the alchemy of turning chaos into usefulness",
        "tags": ["service", "refinement"],
        "weights": {"career": 0.2},
    },
    "Libra": {
        "keywords": "equilibrium artist",
        "style": "gracefully strategic",
        "advice": "weave connection from the threads only you can see",
        "spark": "the mirror that shows others their own beauty",
        "tags": ["relationship", "harmony"],
        "weights": {"love": 0.2},
    },
    "Scorpio": {
        "keywords": "depth alchemist",
        "style": "unrelentingly true",
        "advice": "dive where others dare not look—treasure waits in those shadows",
        "spark": "the x-ray vision that pierces every comfortable lie",
        "tags": ["depth", "transformation"],
        "weights": {"emotional": 0.2},
    },
    "Sagittarius": {
        "keywords": "horizon hunter",
        "style": "wildly philosophical",
        "advice": "let your arrows fly toward truths that haven't been named yet",
        "spark": "the fire that turns every ending into a departure gate",
        "tags": ["philosophy", "adventure"],
        "weights": {"spiritual": 0.2},
    },
    "Capricorn": {
        "keywords": "summit architect",
        "style": "quietly relentless",
        "advice": "build the mountain if one doesn't exist—then climb it anyway",
        "spark": "the ancient knowing that slow rivers carve the deepest canyons",
        "tags": ["structure", "ambition"],
        "weights": {"career": 0.2},
    },
    "Aquarius": {
        "keywords": "future whisperer",
        "style": "brilliantly alien",
        "advice": "trust the vision only you can download from tomorrow",
        "spark": "the frequency that connects strangers into chosen family",
        "tags": ["innovation", "community"],
        "weights": {"general": 0.2},
    },
    "Pisces": {
        "keywords": "dream oracle",
        "style": "boundlessly empathic",
        "advice": "dissolve into the collective dream and bring back the medicine",
        "spark": "the veil between worlds worn thin enough to walk through",
        "tags": ["compassion", "transcendence"],
        "weights": {"spiritual": 0.2, "emotional": 0.1},
    },
}

# Sentence templates for variety - evocative, distinct phrasing
_TEMPLATES: List[str] = [
    "Your {noun} carries {style} energy—{advice}.",
    "With {planet} in {sign}, you {verb}. {advice_cap}.",
    "{planet} in {sign} reveals {article} {style} {noun}—{essence}. {advice_cap}.",
    "You instinctively {verb}, shaped by {spark}.",
    "Here lives {essence}, expressing itself through {style} intensity. {advice_cap}.",
    "{planet} in {sign} means you were born to {verb}—{advice}.",
    "There's something {style} about how you {verb}. {advice_cap}.",
    "Your {noun} hums with {spark}. {advice_cap}.",
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
        essence=pdata.get("essence", pdata["noun"]),
        spark=sdata.get("spark", sdata["keywords"]),
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
