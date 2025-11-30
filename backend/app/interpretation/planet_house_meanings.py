"""
planet_house_meanings.py
Planet placement meanings per house with topic weights.
"""

PLANET_HOUSE_MEANINGS = {
    "Sun": {
        1: {"text": "Identity is visible; life force upfront.", "tags": ["identity"], "weights": {"general": 0.7, "career": 0.5}},
        5: {"text": "Creative self-expression; play and visibility.", "tags": ["creativity"], "weights": {"love": 0.4, "general": 0.5}},
        7: {"text": "Self shines through partnership; relational focus.", "tags": ["relationship"], "weights": {"love": 0.5, "general": 0.4}},
        10: {"text": "Career and reputation spotlighted.", "tags": ["career", "public"], "weights": {"career": 0.9, "general": 0.6}},
    },
    "Moon": {
        4: {"text": "Emotions tied to home and roots.", "tags": ["home", "emotional"], "weights": {"emotional": 0.7, "love": 0.3}},
        6: {"text": "Mood linked to routines and health.", "tags": ["health"], "weights": {"health": 0.5, "emotional": 0.4}},
        7: {"text": "Feels safest in partnership.", "tags": ["relationship", "empathy"], "weights": {"love": 0.6, "emotional": 0.5}},
        12: {"text": "Private emotional life; intuition heightened.", "tags": ["inner"], "weights": {"emotional": 0.6, "spiritual": 0.4}},
    },
    "Mercury": {
        3: {"text": "Loves learning and communicating; neighbors/siblings matter.", "tags": ["communication"], "weights": {"general": 0.4, "career": 0.3}},
        6: {"text": "Analytical about work and health routines.", "tags": ["analysis"], "weights": {"career": 0.4, "health": 0.4}},
        10: {"text": "Public communicator; career benefits from messaging.", "tags": ["public"], "weights": {"career": 0.5}},
    },
    "Venus": {
        5: {"text": "Playful romance and creative pleasure.", "tags": ["love", "joy"], "weights": {"love": 0.8}},
        7: {"text": "Partnership focus; seeks balance.", "tags": ["partnership"], "weights": {"love": 0.9}},
        11: {"text": "Social harmony; friendships and networks bring ease.", "tags": ["social"], "weights": {"love": 0.3, "general": 0.4}},
    },
    "Mars": {
        1: {"text": "Bold presence; acts decisively.", "tags": ["drive"], "weights": {"general": 0.6, "career": 0.5}},
        10: {"text": "Ambition in career; assertive public moves.", "tags": ["career"], "weights": {"career": 0.8}},
        11: {"text": "Group efforts spark action; fights for community.", "tags": ["group"], "weights": {"general": 0.4}},
    },
    "Jupiter": {
        2: {"text": "Growth through skills and resources; abundance mindset.", "tags": ["money"], "weights": {"career": 0.4, "general": 0.3}},
        9: {"text": "Expansion via study, travel, and philosophy.", "tags": ["growth"], "weights": {"spiritual": 0.4, "career": 0.3}},
    },
    "Saturn": {
        4: {"text": "Seriousness about home and roots; slow building.", "tags": ["structure"], "weights": {"emotional": 0.3, "general": 0.3}},
        10: {"text": "Public responsibility and mastery; tests in career.", "tags": ["mastery"], "weights": {"career": 0.7}},
    },
    "Uranus": {
        1: {"text": "Unconventional identity; surprises in self-presentation.", "tags": ["innovation"], "weights": {"general": 0.3}},
        7: {"text": "Relationships awaken; non-traditional partnerships.", "tags": ["relationship"], "weights": {"love": 0.3}},
    },
    "Neptune": {
        1: {"text": "Fluid identity; empathetic presence.", "tags": ["dream"], "weights": {"spiritual": 0.4}},
        10: {"text": "Dreamy reputation; needs clarity in career boundaries.", "tags": ["boundaries"], "weights": {"career": 0.3, "general": 0.3}},
    },
    "Pluto": {
        1: {"text": "Transformative self; intense presence.", "tags": ["power"], "weights": {"general": 0.4}},
        7: {"text": "Deep lessons through partnership; merging and power themes.", "tags": ["intimacy"], "weights": {"love": 0.4, "emotional": 0.4}},
    },
}
