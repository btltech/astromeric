"""
aspect_meanings.py
Aspect meanings with topic weights.
"""

ASPECT_MEANINGS = {
    "conjunction": {
        "text": "Fusion of energies; amplified expression.",
        "tags": ["intensity"],
        "weights": {"general": 0.6},
    },
    "trine": {
        "text": "Ease and flow; supportive talent.",
        "tags": ["support"],
        "weights": {"general": 0.5, "career": 0.3, "love": 0.3},
    },
    "sextile": {
        "text": "Cooperation and opportunity; act to unlock.",
        "tags": ["opportunity"],
        "weights": {"general": 0.4, "career": 0.3},
    },
    "square": {
        "text": "Productive friction; demands action.",
        "tags": ["challenge"],
        "weights": {"challenge": 0.8},
    },
    "opposition": {
        "text": "Polarity seeking balance; integration work.",
        "tags": ["balance"],
        "weights": {"challenge": 0.6, "love": 0.3},
    },
    # Pair-specific examples to expand library
    ("Sun", "Moon", "conjunction"): {
        "text": "Will and emotions aligned; strong inner coherence.",
        "tags": ["identity", "emotional"],
        "weights": {"general": 0.7, "emotional": 0.5},
    },
    ("Sun", "Moon", "square"): {
        "text": "Tension between will and needs; learn to mediate.",
        "tags": ["identity", "emotional"],
        "weights": {"challenge": 0.8},
    },
    ("Venus", "Mars", "conjunction"): {
        "text": "Magnetic chemistry; desire meets affection.",
        "tags": ["love", "desire"],
        "weights": {"love": 0.9},
    },
    ("Venus", "Saturn", "square"): {
        "text": "Tests in commitment and vulnerability.",
        "tags": ["structure", "love"],
        "weights": {"challenge": 0.8, "love": 0.4},
    },
    ("Moon", "Saturn", "opposition"): {
        "text": "Emotional reserve meets duty; balance nurture and boundary.",
        "tags": ["emotional", "structure"],
        "weights": {"challenge": 0.7},
    },
    ("Mercury", "Mercury", "trine"): {
        "text": "Easy communication and shared thinking.",
        "tags": ["communication"],
        "weights": {"general": 0.5},
    },
    ("Sun", "Asc", "conjunction"): {
        "text": "Core identity shines through presentation.",
        "tags": ["identity"],
        "weights": {"general": 0.6},
    },
}
