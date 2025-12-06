"""
planet_house_meanings.py
Auto-generate planet-in-house meanings for 10 planets × 12 houses.
"""

from __future__ import annotations

from typing import Dict

PLANET_THEMES = {
    "Sun": {
        "verb": "illuminates",
        "focus": "core purpose",
        "essence": "You shine brightest and find your identity",
        "weights": {"general": 0.5, "career": 0.4},
    },
    "Moon": {
        "verb": "finds its nest in",
        "focus": "emotional anchor",
        "essence": "Your soul seeks nourishment and safety",
        "weights": {"emotional": 0.6, "love": 0.3},
    },
    "Mercury": {
        "verb": "circulates through",
        "focus": "mental territory",
        "essence": "Your mind wanders and wonders most keenly",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "verb": "weaves beauty into",
        "focus": "magnetism",
        "essence": "Love and pleasure arrive most naturally",
        "weights": {"love": 0.7},
    },
    "Mars": {
        "verb": "charges through",
        "focus": "warrior energy",
        "essence": "Your fighting spirit awakens",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "verb": "scatters abundance across",
        "focus": "growth path",
        "essence": "Fortune tends to multiply",
        "weights": {"spiritual": 0.3, "general": 0.3},
    },
    "Saturn": {
        "verb": "builds fortresses around",
        "focus": "mastery zone",
        "essence": "Life assigns you homework that ultimately crowns you",
        "weights": {"career": 0.4},
    },
    "Uranus": {
        "verb": "electrifies",
        "focus": "breakthrough point",
        "essence": "The unexpected arrives to liberate you",
        "weights": {"general": 0.3},
    },
    "Neptune": {
        "verb": "dissolves the walls around",
        "focus": "dreamscape",
        "essence": "Boundaries blur and magic seeps through",
        "weights": {"spiritual": 0.4},
    },
    "Pluto": {
        "verb": "excavates the depths of",
        "focus": "transformation crucible",
        "essence": "You're called to die and be reborn",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

HOUSE_THEMES = {
    1: {
        "area": "your identity and the mask you wear",
        "zone": "the front door of your existence",
        "tags": ["self", "presence"],
        "weights": {"general": 0.3},
    },
    2: {
        "area": "your resources, talents, and sense of worth",
        "zone": "the treasury where you store your gifts",
        "tags": ["money", "value"],
        "weights": {"career": 0.3},
    },
    3: {
        "area": "how you think, speak, and move through your neighborhood",
        "zone": "the crossroads where ideas meet words",
        "tags": ["communication", "learning"],
        "weights": {"general": 0.2},
    },
    4: {
        "area": "your roots, home, and ancestral inheritance",
        "zone": "the foundation of your inner castle",
        "tags": ["home", "roots"],
        "weights": {"emotional": 0.3},
    },
    5: {
        "area": "your creative fire, romance, and childlike play",
        "zone": "the stage where your heart performs",
        "tags": ["love", "creativity"],
        "weights": {"love": 0.3},
    },
    6: {
        "area": "your daily rituals, service, and bodily temple",
        "zone": "the workshop where craft meets devotion",
        "tags": ["health", "service"],
        "weights": {"career": 0.2, "health": 0.4},
    },
    7: {
        "area": "your mirrors, partnerships, and committed bonds",
        "zone": "the dance floor where two become we",
        "tags": ["relationship", "partnership"],
        "weights": {"love": 0.4},
    },
    8: {
        "area": "the depths you share with others, transformation, and taboo",
        "zone": "the cave where shadows hold treasure",
        "tags": ["intimacy", "depth"],
        "weights": {"emotional": 0.3},
    },
    9: {
        "area": "your philosophy, far horizons, and quest for meaning",
        "zone": "the mountain where truth becomes visible",
        "tags": ["vision", "wisdom"],
        "weights": {"spiritual": 0.3},
    },
    10: {
        "area": "your calling, public role, and summit ambitions",
        "zone": "the throne room of your worldly purpose",
        "tags": ["career", "legacy"],
        "weights": {"career": 0.5},
    },
    11: {
        "area": "your tribes, future visions, and collective dreams",
        "zone": "the network that amplifies your frequency",
        "tags": ["community", "innovation"],
        "weights": {"general": 0.2},
    },
    12: {
        "area": "the unseen, your solitude, and spiritual undercurrents",
        "zone": "the sanctuary behind the veil",
        "tags": ["inner", "transcendence"],
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
        text = f"{planet} {pdata['verb']} {hdata['area']}—{pdata['essence']} in {hdata['zone']}."
        tags = [pdata["focus"], *hdata["tags"]]
        weights = _merge_weights(pdata["weights"], hdata["weights"])
        PLANET_HOUSE_MEANINGS[planet][house] = {
            "text": text,
            "tags": tags,
            "weights": weights,
        }
