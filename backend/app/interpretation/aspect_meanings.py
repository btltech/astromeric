"""
aspect_meanings.py
Aspect meanings with topic weights and expanded pair coverage.
"""
from __future__ import annotations

from typing import Dict, Tuple

BASE_ASPECTS = {
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
}

PAIR_LIBRARY = [
    (
        ("Sun", "Moon", "conjunction"),
        {
            "text": "Will and emotions align; inner coherence.",
            "tags": ["identity", "emotional"],
            "weights": {"general": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Sun", "Moon", "square"),
        {
            "text": "Will vs. needs; find conscious compromise.",
            "tags": ["identity", "emotional"],
            "weights": {"challenge": 0.8},
        },
    ),
    (
        ("Sun", "Asc", "conjunction"),
        {
            "text": "Identity radiates through first impression.",
            "tags": ["identity"],
            "weights": {"general": 0.6},
        },
    ),
    (
        ("Sun", "Saturn", "conjunction"),
        {
            "text": "Purpose meets responsibility; long-range work.",
            "tags": ["identity", "structure"],
            "weights": {"career": 0.6},
        },
    ),
    (
        ("Moon", "Venus", "trine"),
        {
            "text": "Heart and affection blend smoothly.",
            "tags": ["love", "emotional"],
            "weights": {"love": 0.8, "emotional": 0.5},
        },
    ),
    (
        ("Moon", "Saturn", "opposition"),
        {
            "text": "Duty tests feelings; create safe structure.",
            "tags": ["emotional", "structure"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Moon", "Pluto", "square"),
        {
            "text": "Deep emotion stirred; transformation ahead.",
            "tags": ["depth"],
            "weights": {"challenge": 0.7, "emotional": 0.5},
        },
    ),
    (
        ("Mercury", "Mercury", "trine"),
        {
            "text": "Parallel thinking and easy dialogue.",
            "tags": ["communication"],
            "weights": {"general": 0.5},
        },
    ),
    (
        ("Mercury", "Saturn", "conjunction"),
        {
            "text": "Serious mind; strategic communication.",
            "tags": ["structure"],
            "weights": {"career": 0.5, "general": 0.4},
        },
    ),
    (
        ("Mercury", "Neptune", "square"),
        {
            "text": "Facts vs. fantasy tension; clarify messages.",
            "tags": ["mind"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Venus", "Mars", "conjunction"),
        {
            "text": "Attraction plus desire; sparks fly.",
            "tags": ["love", "desire"],
            "weights": {"love": 0.9},
        },
    ),
    (
        ("Venus", "Jupiter", "trine"),
        {
            "text": "Generous love; social abundance.",
            "tags": ["love", "growth"],
            "weights": {"love": 0.7, "general": 0.4},
        },
    ),
    (
        ("Venus", "Saturn", "square"),
        {
            "text": "Commitment lessons; vulnerability takes work.",
            "tags": ["structure", "love"],
            "weights": {"challenge": 0.8, "love": 0.4},
        },
    ),
    (
        ("Venus", "Uranus", "opposition"),
        {
            "text": "Freedom vs. closeness; embrace evolving bonds.",
            "tags": ["change"],
            "weights": {"challenge": 0.6, "love": 0.3},
        },
    ),
    (
        ("Mars", "Saturn", "square"),
        {
            "text": "Effort meets friction; discipline your drive.",
            "tags": ["ambition"],
            "weights": {"challenge": 0.8, "career": 0.5},
        },
    ),
    (
        ("Mars", "Uranus", "opposition"),
        {
            "text": "Impulses clash with change; handle volatility.",
            "tags": ["change"],
            "weights": {"challenge": 0.7},
        },
    ),
    (
        ("Jupiter", "Saturn", "opposition"),
        {
            "text": "Expansion vs. limits; calibrate bets.",
            "tags": ["growth", "structure"],
            "weights": {"challenge": 0.6},
        },
    ),
    (
        ("Jupiter", "Neptune", "trine"),
        {
            "text": "Inspired faith and big-picture creativity.",
            "tags": ["spiritual"],
            "weights": {"spiritual": 0.6},
        },
    ),
    (
        ("Saturn", "Pluto", "conjunction"),
        {
            "text": "Intensity of responsibility; rebuild foundations.",
            "tags": ["power", "structure"],
            "weights": {"career": 0.6},
        },
    ),
]

ASPECT_MEANINGS: Dict[Tuple[str, str, str], Dict] = {}
ASPECT_MEANINGS.update(BASE_ASPECTS)
ASPECT_MEANINGS.update({key: value for key, value in PAIR_LIBRARY})
