"""
planet_sign_meanings.py
Small reusable planet-in-sign meanings with topic weights.
"""

PLANET_SIGN_MEANINGS = {
    "Sun": {
        "Aries": {"text": "Direct, bold self-expression; leads with action.", "tags": ["identity", "drive"], "weights": {"general": 0.7, "career": 0.5}},
        "Taurus": {"text": "Steady, sensual core; builds patiently.", "tags": ["stability", "values"], "weights": {"general": 0.6, "career": 0.4}},
        "Gemini": {"text": "Curious, communicative identity; thrives on variety.", "tags": ["mind", "network"], "weights": {"general": 0.6}},
        "Cancer": {"text": "Protective, feeling-led presence; home-oriented.", "tags": ["emotional", "home"], "weights": {"emotional": 0.6, "love": 0.3}},
        "Leo": {"text": "Expressive, heart-forward; craves visibility.", "tags": ["expression"], "weights": {"general": 0.6, "career": 0.4}},
        "Virgo": {"text": "Service-minded and precise; improves systems.", "tags": ["service", "analysis"], "weights": {"career": 0.5, "general": 0.4}},
    },
    "Moon": {
        "Cancer": {"text": "Nurturing emotional core; protective instincts.", "tags": ["emotional", "home"], "weights": {"emotional": 0.8, "love": 0.4}},
        "Leo": {"text": "Warm, expressive moods; wants to be seen.", "tags": ["expression", "joy"], "weights": {"emotional": 0.6, "love": 0.4}},
        "Virgo": {"text": "Cares through practical service; attentive moods.", "tags": ["care", "detail"], "weights": {"emotional": 0.5, "health": 0.4}},
        "Scorpio": {"text": "Intense, private feelings; loyal bonds.", "tags": ["depth", "loyalty"], "weights": {"emotional": 0.7, "love": 0.5}},
    },
    "Mercury": {
        "Gemini": {"text": "Fast, flexible mind; conversational agility.", "tags": ["communication"], "weights": {"career": 0.4, "general": 0.4}},
        "Virgo": {"text": "Analytical, precise communicator; practical focus.", "tags": ["analysis"], "weights": {"career": 0.5, "health": 0.3}},
        "Capricorn": {"text": "Structured thinking; long-range planning.", "tags": ["structure"], "weights": {"career": 0.5}},
    },
    "Venus": {
        "Libra": {"text": "Relational harmony focus; aesthetic and fair.", "tags": ["love", "harmony"], "weights": {"love": 0.8, "social": 0.5}},
        "Scorpio": {"text": "Intense bonds; loyal and magnetic.", "tags": ["intimacy", "depth"], "weights": {"love": 0.9, "emotional": 0.5}},
        "Pisces": {"text": "Compassionate, artistic affection; dreamy bonds.", "tags": ["compassion", "art"], "weights": {"love": 0.6, "emotional": 0.5}},
    },
    "Mars": {
        "Aries": {"text": "Fast, assertive drive; starts quickly.", "tags": ["drive", "courage"], "weights": {"career": 0.6, "general": 0.5}},
        "Capricorn": {"text": "Disciplined, strategic action.", "tags": ["ambition", "structure"], "weights": {"career": 0.7, "general": 0.5}},
        "Scorpio": {"text": "Intense, focused will; transformative actions.", "tags": ["power"], "weights": {"career": 0.6, "emotional": 0.4}},
    },
    "Jupiter": {
        "Sagittarius": {"text": "Expansive, optimistic; seeks horizons.", "tags": ["growth"], "weights": {"career": 0.4, "general": 0.5, "spiritual": 0.4}},
        "Pisces": {"text": "Compassionate expansion; intuitive wisdom.", "tags": ["spiritual"], "weights": {"spiritual": 0.6, "general": 0.4}},
    },
    "Saturn": {
        "Capricorn": {"text": "Structured, responsible; mastery through rigor.", "tags": ["structure"], "weights": {"career": 0.6}},
        "Aquarius": {"text": "Systems thinker; reforms with discipline.", "tags": ["systems"], "weights": {"career": 0.4, "general": 0.4}},
    },
    "Uranus": {
        "Aquarius": {"text": "Innovative, future-focused; breaks norms.", "tags": ["innovation"], "weights": {"career": 0.3, "general": 0.3}},
    },
    "Neptune": {
        "Pisces": {"text": "Mystical, porous boundaries; creative flow.", "tags": ["spiritual", "dream"], "weights": {"spiritual": 0.6, "emotional": 0.4}},
    },
    "Pluto": {
        "Scorpio": {"text": "Transformative core; power and regeneration.", "tags": ["power", "depth"], "weights": {"emotional": 0.5, "career": 0.4}},
    },
}
