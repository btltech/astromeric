"""
numerology_meanings.py
Concise meaning blocks for numerology types and numbers 1–9.
"""

from __future__ import annotations

from typing import Dict
from .translations import get_translation

BASE_TYPES = {
    "life_path": {
        "text": "Your soul's purpose and core life lessons.",
        "tags": ["purpose", "destiny"],
        "weights": {"general": 0.6, "career": 0.5},
    },
    "expression": {
        "text": "Your natural talents and how you express them.",
        "tags": ["talent", "manifestation"],
        "weights": {"career": 0.5, "general": 0.4},
    },
    "soul_urge": {
        "text": "Your heart's deepest desires.",
        "tags": ["love", "emotional", "desire"],
        "weights": {"love": 0.6, "emotional": 0.5},
    },
    "personality": {
        "text": "How others perceive you.",
        "tags": ["social", "impression"],
        "weights": {"general": 0.3},
    },
    "personal_year": {
        "text": "This year's overarching theme.",
        "tags": ["timing", "yearly"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    "personal_month": {
        "text": "This month's energy focus.",
        "tags": ["timing", "monthly"],
        "weights": {"general": 0.2},
    },
    "personal_day": {
        "text": "Today's energy signature.",
        "tags": ["timing", "daily"],
        "weights": {"general": 0.1},
    },
    "birthday": {
        "text": "Your natural gifts and talents.",
        "tags": ["talent", "gift"],
        "weights": {"general": 0.3},
    },
}

NUMBER_TRAITS = {
    0: {
        "keyword": "All Challenges",
        "short": "Facing all life lessons simultaneously",
        "action": "Draw on your full range of experiences",
        "tags": ["universal", "wisdom"],
        "weights": {"general": 0.3, "spiritual": 0.3},
    },
    1: {
        "keyword": "Initiative",
        "short": "New beginnings, leadership, independence",
        "action": "Take the lead on something new today",
        "tags": ["start", "leadership"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    2: {
        "keyword": "Partnership",
        "short": "Cooperation, sensitivity, diplomacy",
        "action": "Collaborate and listen more than you speak",
        "tags": ["partnership", "receptivity"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    3: {
        "keyword": "Expression",
        "short": "Creativity, communication, joy",
        "action": "Express yourself creatively—write, draw, or speak",
        "tags": ["expression", "creativity"],
        "weights": {"general": 0.3, "career": 0.2},
    },
    4: {
        "keyword": "Foundation",
        "short": "Structure, discipline, stability",
        "action": "Build something lasting with patience",
        "tags": ["structure", "discipline"],
        "weights": {"career": 0.3},
    },
    5: {
        "keyword": "Freedom",
        "short": "Change, adventure, adaptability",
        "action": "Embrace change and try something different",
        "tags": ["change", "adventure"],
        "weights": {"general": 0.3},
    },
    6: {
        "keyword": "Responsibility",
        "short": "Nurturing, service, home & family",
        "action": "Show love through devoted action",
        "tags": ["care", "nurturing"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    7: {
        "keyword": "Wisdom",
        "short": "Introspection, spirituality, analysis",
        "action": "Seek quiet time for reflection and insight",
        "tags": ["insight", "spirituality"],
        "weights": {"spiritual": 0.3, "general": 0.2},
    },
    8: {
        "keyword": "Power",
        "short": "Abundance, ambition, material mastery",
        "action": "Take one bold step toward a goal",
        "tags": ["power", "abundance"],
        "weights": {"career": 0.3},
    },
    9: {
        "keyword": "Completion",
        "short": "Wisdom, humanitarianism, letting go",
        "action": "Release what no longer serves you",
        "tags": ["closure", "compassion"],
        "weights": {"spiritual": 0.3, "emotional": 0.2},
    },
    11: {
        "keyword": "Intuition",
        "short": "Spiritual insight, inspiration, illumination",
        "action": "Trust your inner knowing today",
        "tags": ["master", "vision"],
        "weights": {"spiritual": 0.4, "general": 0.3},
    },
    22: {
        "keyword": "Master Builder",
        "short": "Manifesting dreams, practical vision, legacy",
        "action": "Take action on your biggest vision",
        "tags": ["master", "creation"],
        "weights": {"career": 0.4, "general": 0.3},
    },
    33: {
        "keyword": "Master Teacher",
        "short": "Compassion, healing, selfless service",
        "action": "Uplift someone with love today",
        "tags": ["master", "healing"],
        "weights": {"spiritual": 0.4, "love": 0.3},
    },
}


def _merge_weights(base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


def get_numerology_meanings(lang: str = 'en') -> Dict[str, Dict]:
    """Build numerology meanings for a specific language."""
    meanings = {}
    
    # Get translations
    base_trans = get_translation(lang, 'numerology_base') if lang != 'en' else None
    traits_trans = get_translation(lang, 'number_traits') if lang != 'en' else None
    
    # Add base types (life_path, etc.) - these are usually just keys in the final dict?
    # Wait, the original code updates NUMEROLOGY_MEANINGS with BASE_TYPES first.
    # But BASE_TYPES values have "text", "tags", "weights".
    
    # We need to translate BASE_TYPES values first
    translated_base_types = {}
    for key, val in BASE_TYPES.items():
        new_val = val.copy()
        if base_trans and key in base_trans:
            new_val['text'] = base_trans[key]
        translated_base_types[key] = new_val
        
    meanings.update(translated_base_types)

    for tkey, tdata in BASE_TYPES.items():
        for number, ndata in NUMBER_TRAITS.items():
            key = f"{tkey}_{number}"
            
            # Get trait data (translated or original)
            trait_keyword = ndata['keyword']
            trait_short = ndata['short']
            trait_action = ndata['action']
            
            if traits_trans and number in traits_trans:
                t_data = traits_trans[number]
                trait_keyword = t_data['keyword']
                trait_short = t_data['short']
                trait_action = t_data['action']
            
            # Concise text with keyword and short description
            text = f"{trait_keyword}: {trait_short}. {trait_action}."
            
            tags = tdata["tags"] + ndata["tags"]
            weights = _merge_weights(tdata["weights"], ndata["weights"])
            meanings[key] = {"text": text, "tags": tags, "weights": weights}
            
    return meanings

# Pre-build English meanings dict
NUMEROLOGY_MEANINGS = get_numerology_meanings('en')
