"""
house_themes.py
House theme meanings with topic weights.
"""

from .translations import get_translation

HOUSE_THEMES_DATA = {
    1: {
        "text": "Self & identity—your presence and personal brand.",
        "tags": ["self", "identity"],
        "weights": {"general": 0.4},
    },
    2: {
        "text": "Money & values—what you own and what you're worth.",
        "tags": ["money", "value"],
        "weights": {"career": 0.4},
    },
    3: {
        "text": "Communication & learning—how you think and connect.",
        "tags": ["communication", "learning"],
        "weights": {"general": 0.3},
    },
    4: {
        "text": "Home & roots—family, ancestry, emotional foundation.",
        "tags": ["home", "roots"],
        "weights": {"emotional": 0.4},
    },
    5: {
        "text": "Romance & creativity—self-expression and joy.",
        "tags": ["love", "joy", "creativity"],
        "weights": {"love": 0.5, "general": 0.3},
    },
    6: {
        "text": "Work & health—daily routines and service.",
        "tags": ["health", "service"],
        "weights": {"career": 0.3, "health": 0.5},
    },
    7: {
        "text": "Partnership—relationships and collaboration.",
        "tags": ["relationship", "partnership"],
        "weights": {"love": 0.5, "general": 0.3},
    },
    8: {
        "text": "Depth & transformation—shared resources, intimacy.",
        "tags": ["depth", "transformation"],
        "weights": {"emotional": 0.4},
    },
    9: {
        "text": "Wisdom & expansion—philosophy, travel, higher learning.",
        "tags": ["wisdom", "vision"],
        "weights": {"spiritual": 0.4},
    },
    10: {
        "text": "Career & legacy—public role and ambition.",
        "tags": ["career", "legacy"],
        "weights": {"career": 0.7},
    },
    11: {
        "text": "Community & dreams—friends, groups, future vision.",
        "tags": ["community", "innovation"],
        "weights": {"general": 0.3},
    },
    12: {
        "text": "Spirituality & closure—the unconscious and hidden realms.",
        "tags": ["spirituality", "closure"],
        "weights": {"spiritual": 0.6},
    },
}

def get_house_themes(lang: str = 'en') -> dict:
    """Build house themes for a specific language."""
    themes = {}
    
    # Get translations
    house_trans = get_translation(lang, 'house_themes') if lang != 'en' else None
    
    for house, data in HOUSE_THEMES_DATA.items():
        new_data = data.copy()
        if house_trans and house in house_trans:
            new_data['text'] = house_trans[house]
        themes[house] = new_data
        
    return themes

# Pre-build English themes dict
HOUSE_THEMES = get_house_themes('en')
