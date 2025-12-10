"""
house_themes.py
House theme meanings with topic weights.
"""

HOUSE_THEMES = {
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
        "text": "Spirituality & solitude—the unconscious, transcendence.",
        "tags": ["inner", "transcendence"],
        "weights": {"spiritual": 0.4, "emotional": 0.2},
    },
}
