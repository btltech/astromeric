"""
Interpretation layer aggregating small meaning blocks for reuse.
Each meaning block is a dict with text, tags, and weights by topic.
"""

from .aspect_meanings import ASPECT_MEANINGS
from .house_themes import HOUSE_THEMES
from .numerology_meanings import NUMEROLOGY_MEANINGS
from .planet_house_meanings import PLANET_HOUSE_MEANINGS
from .planet_sign_meanings import PLANET_SIGN_MEANINGS

__all__ = [
    "PLANET_SIGN_MEANINGS",
    "PLANET_HOUSE_MEANINGS",
    "ASPECT_MEANINGS",
    "HOUSE_THEMES",
    "NUMEROLOGY_MEANINGS",
]
