"""
Interpretation layer aggregating small meaning blocks for reuse.
Each meaning block is a dict with text, tags, and weights by topic.
"""

from .aspect_meanings import ASPECT_MEANINGS, get_aspect_meanings
from .house_themes import HOUSE_THEMES, get_house_themes
from .numerology_meanings import NUMEROLOGY_MEANINGS, get_numerology_meanings
from .planet_house_meanings import PLANET_HOUSE_MEANINGS, get_planet_house_meanings
from .planet_sign_meanings import PLANET_SIGN_MEANINGS, get_planet_sign_text, get_planet_sign_meanings
from .translations import get_translation

__all__ = [
    "PLANET_SIGN_MEANINGS",
    "PLANET_HOUSE_MEANINGS",
    "ASPECT_MEANINGS",
    "HOUSE_THEMES",
    "NUMEROLOGY_MEANINGS",
    "get_planet_sign_text",
    "get_planet_sign_meanings",
    "get_planet_house_meanings",
    "get_aspect_meanings",
    "get_numerology_meanings",
    "get_house_themes",
    "get_translation",
]
