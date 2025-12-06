"""
aspect_meanings.py
Aspect meanings with topic weights and expanded pair coverage.
"""

from __future__ import annotations

from typing import Dict, Tuple

BASE_ASPECTS = {
    "conjunction": {
        "text": "Two forces merge into one amplified current—the volume knob turned all the way up on both frequencies.",
        "tags": ["intensity", "fusion"],
        "weights": {"general": 0.6},
    },
    "trine": {
        "text": "A natural channel opens between these energies—gifts that flow without forcing, talents that feel like breathing.",
        "tags": ["support", "grace"],
        "weights": {"general": 0.5, "career": 0.3, "love": 0.3},
    },
    "sextile": {
        "text": "An invitation waits to be accepted—potential that activates when you reach for it deliberately.",
        "tags": ["opportunity", "cooperation"],
        "weights": {"general": 0.4, "career": 0.3},
    },
    "square": {
        "text": "Tension that refuses to be ignored—the friction that forges diamonds from carbon.",
        "tags": ["challenge", "growth"],
        "weights": {"challenge": 0.8},
    },
    "opposition": {
        "text": "Two ends of the same axis demanding integration—the tightrope walk that teaches balance.",
        "tags": ["balance", "polarity"],
        "weights": {"challenge": 0.6, "love": 0.3},
    },
}

PAIR_LIBRARY = [
    (
        ("Sun", "Moon", "conjunction"),
        {
            "text": "Your will and your heart beat as one drum—a rare inner coherence where what you want and what you need speak the same language.",
            "tags": ["identity", "emotional"],
            "weights": {"general": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Sun", "Moon", "square"),
        {
            "text": "An ongoing negotiation between your conscious direction and your emotional undertow—growth comes from honoring both voices.",
            "tags": ["identity", "emotional"],
            "weights": {"challenge": 0.8},
        },
    ),
    (
        ("Sun", "Asc", "conjunction"),
        {
            "text": "Who you are and how you appear are the same person—your presence announces your truth before you speak.",
            "tags": ["identity"],
            "weights": {"general": 0.6},
        },
    ),
    (
        ("Sun", "Saturn", "conjunction"),
        {
            "text": "Purpose crystallized through discipline—you were born to build something that outlasts the moment.",
            "tags": ["identity", "structure"],
            "weights": {"career": 0.6},
        },
    ),
    (
        ("Moon", "Venus", "trine"),
        {
            "text": "Your emotional intelligence and your capacity for love speak fluently to each other—affection comes naturally, like honey from the comb.",
            "tags": ["love", "emotional"],
            "weights": {"love": 0.8, "emotional": 0.5},
        },
    ),
    (
        ("Moon", "Saturn", "opposition"),
        {
            "text": "Feelings meet the demands of reality—learning to build safe containers for tender places is your soul curriculum.",
            "tags": ["emotional", "structure"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Moon", "Pluto", "square"),
        {
            "text": "Emotional depths that volcanic forces stir—transformation happens when you befriend the intensity instead of fearing it.",
            "tags": ["depth", "transformation"],
            "weights": {"challenge": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Mercury", "Mercury", "trine"),
        {
            "text": "Minds that meet like rivers joining—conversation flows without translation, understanding arrives before explanation.",
            "tags": ["communication"],
            "weights": {"general": 0.5},
        },
    ),
    (
        ("Mercury", "Saturn", "conjunction"),
        {
            "text": "Thought anchored in consequence—your words carry weight because you've measured them against reality.",
            "tags": ["structure", "strategy"],
            "weights": {"career": 0.5, "general": 0.4},
        },
    ),
    (
        ("Mercury", "Neptune", "square"),
        {
            "text": "The logical and the mystical compete for your attention—clarity comes when you let facts and intuition inform each other.",
            "tags": ["mind", "imagination"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Venus", "Mars", "conjunction"),
        {
            "text": "Desire and attraction dance in your blood—magnetism that ignites rooms and pulls people into your orbit.",
            "tags": ["love", "desire", "passion"],
            "weights": {"love": 0.9},
        },
    ),
    (
        ("Venus", "Jupiter", "trine"),
        {
            "text": "Love expands when you give it—generosity returns to you multiplied, as if the universe rewards your open heart.",
            "tags": ["love", "growth", "abundance"],
            "weights": {"love": 0.7, "general": 0.4},
        },
    ),
    (
        ("Venus", "Saturn", "square"),
        {
            "text": "Love asks you to grow up—vulnerability requires walls to come down slowly, trust built brick by deliberate brick.",
            "tags": ["structure", "love", "maturity"],
            "weights": {"challenge": 0.8, "love": 0.4},
        },
    ),
    (
        ("Venus", "Uranus", "opposition"),
        {
            "text": "Your heart craves both freedom and connection—the art is creating bonds elastic enough for two sovereign souls.",
            "tags": ["change", "independence"],
            "weights": {"challenge": 0.6, "love": 0.3},
        },
    ),
    (
        ("Mars", "Saturn", "square"),
        {
            "text": "Drive meets resistance that ultimately makes you unstoppable—the friction that tempers your will into steel.",
            "tags": ["ambition", "perseverance"],
            "weights": {"challenge": 0.8, "career": 0.5},
        },
    ),
    (
        ("Mars", "Uranus", "opposition"),
        {
            "text": "Lightning in your action signature—impulses that need channeling lest they scatter your power to the winds.",
            "tags": ["change", "volatility"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Jupiter", "Saturn", "opposition"),
        {
            "text": "The dreamer and the realist arm-wrestle in your psyche—wisdom emerges when you let both have their say.",
            "tags": ["growth", "structure", "wisdom"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Jupiter", "Neptune", "trine"),
        {
            "text": "Faith flows through an open channel—visions arrive that feel like remembering instead of imagining.",
            "tags": ["spiritual", "inspiration"],
            "weights": {"spiritual": 0.6},
        },
    ),
    (
        ("Saturn", "Pluto", "conjunction"),
        {
            "text": "Pressure that creates diamonds—the universe asks you to demolish and rebuild, forging something unshakable from the ruins.",
            "tags": ["power", "structure", "transformation"],
            "weights": {"career": 0.6},
        },
    ),
]

ASPECT_MEANINGS: Dict[Tuple[str, str, str], Dict] = {}
ASPECT_MEANINGS.update(BASE_ASPECTS)
ASPECT_MEANINGS.update({key: value for key, value in PAIR_LIBRARY})
