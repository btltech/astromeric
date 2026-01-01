"""
aspect_meanings.py
Concise aspect meanings with topic weights.
"""

from __future__ import annotations

from typing import Dict, Tuple
from .translations import get_translation

BASE_ASPECTS = {
    "conjunction": {
        "text": "Intense fusion—amplified energy.",
        "tags": ["intensity", "fusion"],
        "weights": {"general": 0.6},
    },
    "trine": {
        "text": "Natural flow—effortless harmony.",
        "tags": ["support", "grace"],
        "weights": {"general": 0.5, "career": 0.3, "love": 0.3},
    },
    "sextile": {
        "text": "Opportunity—potential when activated.",
        "tags": ["opportunity", "cooperation"],
        "weights": {"general": 0.4, "career": 0.3},
    },
    "square": {
        "text": "Creative tension—growth through challenge.",
        "tags": ["challenge", "growth"],
        "weights": {"challenge": 0.8},
    },
    "opposition": {
        "text": "Balance needed—integrate both sides.",
        "tags": ["balance", "polarity"],
        "weights": {"challenge": 0.6, "love": 0.3},
    },
}

PAIR_LIBRARY = [
    (
        ("Sun", "Moon", "conjunction"),
        {
            "text": "Will and emotion aligned—inner coherence.",
            "tags": ["identity", "emotional"],
            "weights": {"general": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Sun", "Moon", "square"),
        {
            "text": "Tension between wants and needs—honor both.",
            "tags": ["identity", "emotional"],
            "weights": {"challenge": 0.8},
        },
    ),
    (
        ("Sun", "Asc", "conjunction"),
        {
            "text": "Authentic presence—what you show is who you are.",
            "tags": ["identity"],
            "weights": {"general": 0.6},
        },
    ),
    (
        ("Sun", "Saturn", "conjunction"),
        {
            "text": "Purpose through discipline—build something lasting.",
            "tags": ["identity", "structure"],
            "weights": {"career": 0.6},
        },
    ),
    (
        ("Moon", "Venus", "trine"),
        {
            "text": "Emotions and love flow naturally together.",
            "tags": ["love", "emotional"],
            "weights": {"love": 0.8, "emotional": 0.5},
        },
    ),
    (
        ("Moon", "Saturn", "opposition"),
        {
            "text": "Feelings meet duty—create safe containers.",
            "tags": ["emotional", "structure"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Moon", "Pluto", "square"),
        {
            "text": "Intense emotions—transform through acceptance.",
            "tags": ["depth", "transformation"],
            "weights": {"challenge": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Mercury", "Mercury", "trine"),
        {
            "text": "Minds connect easily—natural understanding.",
            "tags": ["communication"],
            "weights": {"general": 0.5},
        },
    ),
    (
        ("Mercury", "Saturn", "conjunction"),
        {
            "text": "Careful thinking—words carry weight.",
            "tags": ["structure", "strategy"],
            "weights": {"career": 0.5, "general": 0.4},
        },
    ),
    (
        ("Mercury", "Neptune", "square"),
        {
            "text": "Logic vs intuition—let both inform you.",
            "tags": ["mind", "imagination"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Venus", "Mars", "conjunction"),
        {
            "text": "Magnetic attraction—passion runs high.",
            "tags": ["love", "desire", "passion"],
            "weights": {"love": 0.9},
        },
    ),
    (
        ("Venus", "Jupiter", "trine"),
        {
            "text": "Love expands—generosity returns multiplied.",
            "tags": ["love", "growth", "abundance"],
            "weights": {"love": 0.7, "general": 0.4},
        },
    ),
    (
        ("Venus", "Saturn", "square"),
        {
            "text": "Love requires patience—trust builds slowly.",
            "tags": ["structure", "love", "maturity"],
            "weights": {"challenge": 0.8, "love": 0.4},
        },
    ),
    (
        ("Venus", "Uranus", "opposition"),
        {
            "text": "Freedom vs connection—balance independence.",
            "tags": ["change", "independence"],
            "weights": {"challenge": 0.6, "love": 0.3},
        },
    ),
    (
        ("Mars", "Saturn", "square"),
        {
            "text": "Drive meets resistance—persistence wins.",
            "tags": ["ambition", "perseverance"],
            "weights": {"challenge": 0.8, "career": 0.5},
        },
    ),
    (
        ("Mars", "Uranus", "opposition"),
        {
            "text": "Impulsive energy—channel it wisely.",
            "tags": ["change", "volatility"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Jupiter", "Saturn", "opposition"),
        {
            "text": "Expansion vs limits—find the middle way.",
            "tags": ["growth", "structure", "wisdom"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Jupiter", "Neptune", "trine"),
        {
            "text": "Faith flows freely—trust your visions.",
            "tags": ["spiritual", "inspiration"],
            "weights": {"spiritual": 0.6},
        },
    ),
    (
        ("Saturn", "Pluto", "conjunction"),
        {
            "text": "Deep transformation—rebuild stronger.",
            "tags": ["power", "structure", "transformation"],
            "weights": {"career": 0.6},
        },
    ),
]

def get_aspect_meanings(lang: str = 'en') -> Dict[Tuple[str, str, str], Dict]:
    """Build aspect meanings for a specific language."""
    meanings = {}
    
    # Get translations
    aspects_trans = get_translation(lang, 'aspects') if lang != 'en' else None
    pairs_trans = get_translation(lang, 'aspect_pairs') if lang != 'en' else None
    
    # 1. Add Base Aspects
    # Note: BASE_ASPECTS keys are single strings (aspect name), but ASPECT_MEANINGS expects tuples?
    # Wait, the original code does:
    # ASPECT_MEANINGS.update(BASE_ASPECTS)
    # ASPECT_MEANINGS.update({key: value for key, value in PAIR_LIBRARY})
    # So ASPECT_MEANINGS is a mix of str keys and tuple keys?
    # The type hint says Dict[Tuple[str, str, str], Dict], but BASE_ASPECTS has str keys.
    # This implies the type hint might be slightly off or loose, or BASE_ASPECTS are used differently.
    # Let's preserve the behavior.
    
    translated_base_aspects = {}
    for key, val in BASE_ASPECTS.items():
        new_val = val.copy()
        if aspects_trans and key in aspects_trans:
            new_val['text'] = aspects_trans[key]
        translated_base_aspects[key] = new_val
        
    meanings.update(translated_base_aspects)
    
    # 2. Add Pair Library
    for (p1, p2, aspect), data in PAIR_LIBRARY:
        key = (p1, p2, aspect)
        new_data = data.copy()
        
        # Construct lookup key for translation
        trans_key = f"{p1}_{p2}_{aspect}"
        
        if pairs_trans and trans_key in pairs_trans:
            new_data['text'] = pairs_trans[trans_key]
            
        meanings[key] = new_data
        
    return meanings

# Pre-build English meanings dict
ASPECT_MEANINGS = get_aspect_meanings('en')
