"""
house_themes.py
House theme meanings with topic weights.
"""

HOUSE_THEMES = {
    1: {
        "text": "The doorway through which you enter every room—your body, your presence, your personal myth.",
        "tags": ["self", "identity"],
        "weights": {"general": 0.4},
    },
    2: {
        "text": "The vault of your talents, treasures, and self-worth—what you possess and what possesses you.",
        "tags": ["money", "value"],
        "weights": {"career": 0.4},
    },
    3: {
        "text": "The crossroads of mind and message—how you think, speak, and connect your neighborhood of ideas.",
        "tags": ["communication", "learning"],
        "weights": {"general": 0.3},
    },
    4: {
        "text": "The roots that anchor your soul—home, ancestry, and the foundation of your inner castle.",
        "tags": ["home", "roots"],
        "weights": {"emotional": 0.4},
    },
    5: {
        "text": "The stage where your heart performs—romance, creative fire, and the child who still lives in you.",
        "tags": ["love", "joy", "creativity"],
        "weights": {"love": 0.5, "general": 0.3},
    },
    6: {
        "text": "The temple of daily devotion—rituals of work, health, and humble service that craft your days.",
        "tags": ["health", "service"],
        "weights": {"career": 0.3, "health": 0.5},
    },
    7: {
        "text": "The mirror held by others—partnerships, contracts, and the dance of two becoming we.",
        "tags": ["relationship", "partnership"],
        "weights": {"love": 0.5, "general": 0.3},
    },
    8: {
        "text": "The cave where shadows guard treasure—shared resources, intimacy, death, and rebirth.",
        "tags": ["depth", "transformation"],
        "weights": {"emotional": 0.4},
    },
    9: {
        "text": "The mountain peak of meaning—philosophy, far journeys, and the truths you've come to teach.",
        "tags": ["wisdom", "vision"],
        "weights": {"spiritual": 0.4},
    },
    10: {
        "text": "The throne room of your worldly calling—career, legacy, and the summit you're climbing toward.",
        "tags": ["career", "legacy"],
        "weights": {"career": 0.7},
    },
    11: {
        "text": "The network that amplifies your signal—friends, collective dreams, and visions of tomorrow.",
        "tags": ["community", "innovation"],
        "weights": {"general": 0.3},
    },
    12: {
        "text": "The sanctuary behind the veil—solitude, the unconscious, and where you dissolve into something larger.",
        "tags": ["inner", "transcendence"],
        "weights": {"spiritual": 0.4, "emotional": 0.2},
    },
}
