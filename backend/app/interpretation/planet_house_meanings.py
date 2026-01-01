"""
planet_house_meanings.py
Concise planet-in-house meanings.
"""

from __future__ import annotations

from typing import Dict
from .translations import get_translation

PLANET_THEMES = {
    "Sun": {
        "keyword": "Identity",
        "focus": "core purpose",
        "weights": {"general": 0.5, "career": 0.4},
    },
    "Moon": {
        "keyword": "Emotions",
        "focus": "emotional anchor",
        "weights": {"emotional": 0.6, "love": 0.3},
    },
    "Mercury": {
        "keyword": "Mind",
        "focus": "mental territory",
        "weights": {"general": 0.4, "career": 0.3},
    },
    "Venus": {
        "keyword": "Love",
        "focus": "magnetism",
        "weights": {"love": 0.7},
    },
    "Mars": {
        "keyword": "Drive",
        "focus": "warrior energy",
        "weights": {"career": 0.5, "general": 0.4},
    },
    "Jupiter": {
        "keyword": "Growth",
        "focus": "growth path",
        "weights": {"spiritual": 0.3, "general": 0.3},
    },
    "Saturn": {
        "keyword": "Discipline",
        "focus": "mastery zone",
        "weights": {"career": 0.4},
    },
    "Uranus": {
        "keyword": "Change",
        "focus": "breakthrough point",
        "weights": {"general": 0.3},
    },
    "Neptune": {
        "keyword": "Dreams",
        "focus": "dreamscape",
        "weights": {"spiritual": 0.4},
    },
    "Pluto": {
        "keyword": "Power",
        "focus": "transformation crucible",
        "weights": {"emotional": 0.4, "career": 0.3},
    },
}

HOUSE_THEMES = {
    1: {
        "area": "self & presence",
        "action": "Be authentic",
        "tags": ["self", "presence"],
        "weights": {"general": 0.3},
    },
    2: {
        "area": "money & values",
        "action": "Build resources",
        "tags": ["money", "value"],
        "weights": {"career": 0.3},
    },
    3: {
        "area": "communication",
        "action": "Share ideas",
        "tags": ["communication", "learning"],
        "weights": {"general": 0.2},
    },
    4: {
        "area": "home & roots",
        "action": "Create security",
        "tags": ["home", "roots"],
        "weights": {"emotional": 0.3},
    },
    5: {
        "area": "creativity & romance",
        "action": "Express yourself",
        "tags": ["love", "creativity"],
        "weights": {"love": 0.3},
    },
    6: {
        "area": "health & work",
        "action": "Serve with skill",
        "tags": ["health", "service"],
        "weights": {"career": 0.2, "health": 0.4},
    },
    7: {
        "area": "partnerships",
        "action": "Collaborate",
        "tags": ["relationship", "partnership"],
        "weights": {"love": 0.4},
    },
    8: {
        "area": "transformation",
        "action": "Embrace depth",
        "tags": ["intimacy", "depth"],
        "weights": {"emotional": 0.3},
    },
    9: {
        "area": "philosophy & travel",
        "action": "Expand horizons",
        "tags": ["vision", "wisdom"],
        "weights": {"spiritual": 0.3},
    },
    10: {
        "area": "career & legacy",
        "action": "Build your reputation",
        "tags": ["career", "legacy"],
        "weights": {"career": 0.5},
    },
    11: {
        "area": "community & goals",
        "action": "Connect with like minds",
        "tags": ["community", "innovation"],
        "weights": {"general": 0.2},
    },
    12: {
        "area": "spirituality & solitude",
        "action": "Seek inner wisdom",
        "tags": ["inner", "transcendence"],
        "weights": {"spiritual": 0.3, "emotional": 0.2},
    },
}


def _merge_weights(base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


def get_planet_house_meanings(lang: str = 'en') -> Dict[str, Dict[int, Dict]]:
    """Build planet house meanings for a specific language."""
    meanings = {}
    
    # Get translations
    ph_trans = get_translation(lang, 'planet_house') if lang != 'en' else None
    p_keywords_trans = ph_trans.get('planet_keywords') if ph_trans else None
    h_actions_trans = ph_trans.get('house_actions') if ph_trans else None
    
    for planet, pdata in PLANET_THEMES.items():
        meanings[planet] = {}
        
        # Get planet keyword/focus
        p_keyword = pdata['keyword']
        p_focus = pdata['focus']
        
        if p_keywords_trans and planet in p_keywords_trans:
            p_keyword = p_keywords_trans[planet]['keyword']
            p_focus = p_keywords_trans[planet]['focus']
            
        for house, hdata in HOUSE_THEMES.items():
            # Get house area/action
            h_area = hdata['area']
            h_action = hdata['action']
            
            if h_actions_trans and house in h_actions_trans:
                h_area = h_actions_trans[house]['area']
                h_action = h_actions_trans[house]['action']
            
            # Construct text
            # "Keyword focused on area. Action."
            # Note: Grammar might vary.
            if lang == 'en':
                text = f"{p_keyword} focused on {h_area}. {h_action}."
            else:
                # Simple construction for other languages
                text = f"{p_keyword} ({p_focus}) - {h_area}. {h_action}."
            
            tags = [p_focus, *hdata["tags"]]
            weights = _merge_weights(pdata["weights"], hdata["weights"])
            meanings[planet][house] = {
                "text": text,
                "tags": tags,
                "weights": weights,
            }
            
    return meanings

# Pre-build English meanings dict
PLANET_HOUSE_MEANINGS = get_planet_house_meanings('en')
