"""
house_themes.py
House theme meanings with topic weights.
"""

HOUSE_THEMES = {
    1: {"text": "Identity, body, approach to life.", "tags": ["self"], "weights": {"general": 0.4}},
    2: {"text": "Resources, money, skills, values.", "tags": ["money"], "weights": {"career": 0.4}},
    5: {"text": "Romance, play, creativity, children.", "tags": ["love", "joy"], "weights": {"love": 0.5, "general": 0.3}},
    6: {"text": "Daily work, health, service routines.", "tags": ["health"], "weights": {"career": 0.3, "health": 0.5}},
    7: {"text": "Partnerships and contracts.", "tags": ["relationship"], "weights": {"love": 0.5, "general": 0.3}},
    10: {"text": "Career, reputation, public life.", "tags": ["career"], "weights": {"career": 0.7}},
}
